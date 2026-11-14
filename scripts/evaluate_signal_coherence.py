#!/usr/bin/env python3
"""Conservative, pre-declared NISAR radar-change *signal* experiment.

This is NOT water/flood classification, water area, or event attribution.
Compare three zero-training, fixed-parameter changes on TWO independently
observed geographic cases:
    raw: signed pixel-wise HH delta above absolute 3 dB;
    median3: median of HH dB in 3x3 source-date windows, delta >3 dB;
    coherent: median3 threshold plus >=6/9 neighbors with same change sign.

Reference diagnostics use only common OPERA 0/1 strict cells and label
transition 0->1 vs 1->0; HLS reference dates: Oct29/Nov05 vs NISAR
Oct29/Nov10. S1 reference: Oct31/Nov10 vs NISAR Oct28/Nov09.
Any agreement numbers are product-to-product diagnostics, not flood accuracy.
OPERA WTR class 3 inundated vegetation in S1 is always excluded from
binary open-water transition evaluation, but its area is recorded separately.

Runnable offline with numpy/rasterio/matplotlib plus local source TIFFs:
  python scripts/evaluate_signal_coherence.py
"""
from pathlib import Path
import json
import sys
import warnings

import numpy as np
from PIL import Image
from numpy.lib.stride_tricks import sliding_window_view

HERE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(HERE/"scripts"))
from compare_nisar_opera_hls import ROOT as K_ROOT, read_pair
from compare_assam_opera import ROOT as A_ROOT, observe

RESULT_DIR=HERE/"research"/"signal_coherence"
# Thresholds specified in advance, not fit or selected using OPERA labels.
MAGNITUDE_DB=3.0
NEIGHBOR_RADIUS=1
MIN_VALID_NEIGHBORS=5
MIN_CONSISTENT_NEIGHBORS=6
MIN_SUPPORT_VALID=7

def local_median(x):
    """3x3 NaN-aware spatial median, at least 5 valid source-date cells."""
    padded=np.pad(x,1,mode="constant",constant_values=np.nan)
    win=sliding_window_view(padded,(3,3))
    valid=np.isfinite(win).sum(axis=(-1,-2))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore",RuntimeWarning)
        v=np.nanmedian(win,axis=(-1,-2))
    v[valid<MIN_VALID_NEIGHBORS]=np.nan
    return v.astype(np.float32)

def neighbor_count(mask):
    padded=np.pad(mask.astype(np.uint8),1,mode="constant",constant_values=0)
    return sliding_window_view(padded,(3,3)).sum(axis=(-1,-2),dtype=np.uint8)

def methods(before,after):
    common=np.isfinite(before)&np.isfinite(after)
    raw=after-before
    med0,med1=local_median(before),local_median(after)
    filtered=med1-med0
    raw_less=common&(raw<=-MAGNITUDE_DB)
    raw_more=common&(raw>=MAGNITUDE_DB)
    filt_common=common&np.isfinite(filtered)
    filt_less=filt_common&(filtered<=-MAGNITUDE_DB)
    filt_more=filt_common&(filtered>=MAGNITUDE_DB)
    # Spatially coherent radar SIGNAL changes, *not* water probabilities.
    # Preserve valid core coverage; require >=7/9 common valid cells and
    # >=6/9 strong same-sign neighboring pixels (including center).
    support=neighbor_count(filt_common)>=MIN_SUPPORT_VALID
    dec=filt_less&support&(neighbor_count(filt_less)>=MIN_CONSISTENT_NEIGHBORS)
    inc=filt_more&support&(neighbor_count(filt_more)>=MIN_CONSISTENT_NEIGHBORS)
    return dict(
      raw=(raw_less,raw_more),
      median3=(filt_less,filt_more),
      coherent=(dec,inc),
    ),dict(common=common,raw=raw,median_delta=filtered,filt_common=filt_common)

def confusion(pred,true,valid):
    tp=int((pred&true&valid).sum())
    fp=int((pred&~true&valid).sum())
    fn=int((~pred&true&valid).sum())
    tn=int((~pred&~true&valid).sum())
    return dict(tp=tp,fp=fp,fn=fn,tn=tn,
       precision=round(tp/(tp+fp),5) if tp+fp else None,
       recall=round(tp/(tp+fn),5) if tp+fn else None,
       f1=round(2*tp/(2*tp+fp+fn),5) if (2*tp+fp+fn) else None)

def source_study(site):
    if site=="kuttanad":
        import rasterio
        with rasterio.open(K_ROOT/"nisar_2026-10-29_hhhh_raw.tif") as src:
            bounds,crs=src.bounds,src.crs
        a=read_pair("2026-10-29","S2B","2026-10-29",bounds,crs)
        b=read_pair("2026-11-05","S2A","2026-11-10",bounds,crs)
        shape=a["radar_db"].shape
        if shape!=b["radar_db"].shape or a["transform"]!=b["transform"]:
            raise RuntimeError("Kuttanad geospatial grid mismatch")
        return dict(before=a["radar_db"],after=b["radar_db"],
             ref_before=a["label"],ref_after=b["label"],
             pixel_area_km2=abs(a["transform"].a*a["transform"].e-a["transform"].b*a["transform"].d)/1e6,
             radar_dates=["2026-10-29","2026-11-10"],
             reference_dates=["2026-10-29","2026-11-05"],
             reference="OPERA DSWx-HLS optical")
    if site=="assam":
        a=observe("2026-10-28","2026-10-31")
        b=observe("2026-11-09","2026-11-10")
        if a["radar_db"].shape!=b["radar_db"].shape or a["grid_transform"]!=b["grid_transform"]:
            raise RuntimeError("Lower Assam geospatial grid mismatch")
        return dict(before=a["radar_db"],after=b["radar_db"],
             ref_before=a["labels"],ref_after=b["labels"],
             pixel_area_km2=a["pixel_area_km2"],
             radar_dates=["2026-10-28","2026-11-09"],
             reference_dates=["2026-10-31","2026-11-10"],
             reference="OPERA DSWx-S1 Sentinel-1 C-band")
    raise ValueError(site)

def render_signal(dec,inc,path):
    """RGBA overlay showing NISAR signal dimming/brightening only."""
    rgba=np.zeros((*dec.shape,4),dtype=np.uint8)
    rgba[dec]=(48,202,215,224)     # strong coherent decrease (teal)
    rgba[inc]=(244,160,90,224)     # strong coherent increase (amber)
    Image.fromarray(rgba).save(path,optimize=True)

def evaluate_site(site):
    d=source_study(site)
    classes0,classes1=d["ref_before"],d["ref_after"]
    mask=np.isin(classes0,[0,1])&np.isin(classes1,[0,1])
    true_gain=(classes0==0)&(classes1==1)
    true_loss=(classes0==1)&(classes1==0)
    stable_land=(classes0==0)&(classes1==0)
    stable_open=(classes0==1)&(classes1==1)
    candidates,values=methods(d["before"],d["after"])
    valid=mask&values["common"]
    delta=values["raw"][values["common"]]
    med=float(np.median(delta))
    report={
      "site":site,
      "experiment":"Fixed-parameter radar signal-change filter, not flood classification",
      "radar_dates":d["radar_dates"],
      "reference_dates":d["reference_dates"],
      "reference":d["reference"],
      "method_parameters":{
        "magnitude_db":MAGNITUDE_DB,
        "local_median_window_pixels":3,
        "median_min_valid_neighbors":MIN_VALID_NEIGHBORS,
        "coherent_same_sign_neighbors_required":MIN_CONSISTENT_NEIGHBORS,
        "coherent_min_valid_neighbors":MIN_SUPPORT_VALID,
        "OPERA_reference_labels_used_in_method":False,
      },
      "grid":{"shape":list(d["before"].shape),"pixel_area_km2":d["pixel_area_km2"]},
      "common_valid_radar_cells":int(values["common"].sum()),
      "strict_opera_class_0_1_both_cells":int(valid.sum()),
      "ref_new_open_water_cells":int((true_gain&valid).sum()),
      "ref_lost_open_water_cells":int((true_loss&valid).sum()),
      "reference_class_3_inundated_vegetation_counts":[
          int((classes0==3).sum()),int((classes1==3).sum())
        ] if site=="assam" else None,
      "radar_delta_median_db":round(med,5),
      "radar_delta_mad_db":round(float(np.median(np.abs(delta-med))),5),
      "methods":{},
      "limitations":[
        "Radar dimming/brightening is not synonymous with water gain/loss",
        "OPERA WTR is an independent satellite product, not field ground truth",
        "OPERA reference acquisition dates do not match radar exactly",
        "Kuttanad OPERA HLS and Assam OPERA S1 are not cross-sensor harmonized",
        "The fixed spatial filter can suppress real small changes and retain structured non-water changes",
        "No multi-date same-track validated reference baseline exists for these sites as of Nov 14 2026",
        "NISAR pre-Nov12 modes may have radiometric residuals near 1dB; scene-specific impact unknown",
      ]
    }
    for name,(decrease,increase) in candidates.items():
        # Never use OPERA reference labels to modify change candidate masks.
        record={
          "candidate_decrease_cells":int(decrease.sum()),
          "candidate_increase_cells":int(increase.sum()),
          "candidate_any_km2":round(float((decrease|increase).sum()*d["pixel_area_km2"]),4),
          "fraction_of_shared_valid_radar_flagged":round(
              float(((decrease|increase)&values["common"]).sum()/values["common"].sum()),5),
          "reference_diagnostic":{
            "water_gain_vs_radar_decrease":confusion(decrease,true_gain,valid),
            "water_loss_vs_radar_increase":confusion(increase,true_loss,valid),
            "stable_nonwater_flag_fraction":round(float(((decrease|increase)&valid&stable_land).sum() /
                  ((valid&stable_land).sum() or 1)),5),
            "stable_openwater_flag_fraction":round(float(((decrease|increase)&valid&stable_open).sum() /
                  ((valid&stable_open).sum() or 1)),5),
          }
        }
        report["methods"][name]=record
    directory=HERE/"web"/"public"/"data"/("assam" if site=="assam" else "")
    directory.mkdir(parents=True,exist_ok=True)
    out=directory/"coherent_change.png"
    render_signal(*candidates["coherent"],out)
    RESULT_DIR.mkdir(exist_ok=True,parents=True)
    (RESULT_DIR/(site+"_metrics.json")).write_text(json.dumps(report,indent=2)+"\n")

    # Keep generated visualization metadata synchronized with recomputed
    # science. Run this script AFTER the two export_*_demo.py scripts.
    metadata_path=directory/"meta.json"
    if metadata_path.is_file():
        meta=json.loads(metadata_path.read_text())
        if (int(meta.get("rows",-1)),int(meta.get("cols",-1)))!=d["before"].shape:
            raise RuntimeError("Unexpected web metadata grid for "+site)
        if meta.get("primary_dates")!=d["radar_dates"]:
            raise RuntimeError("Web radar dates do not match scientific experiment")
        meta.setdefault("statistics",{})["coherent_signal_area_km2"]=(
          report["methods"]["coherent"]["candidate_any_km2"])
        meta["statistics"]["coherent_signal_fraction"]=(
          report["methods"]["coherent"]["fraction_of_shared_valid_radar_flagged"])
        meta["radar_signal_cluster_note"]=(
          "HHHH radar signal only; fixed 3dB threshold plus 3x3 median "
          "and 6/9-neighbor agreement; NOT flood detection")
        meta["radar_signal_cluster_source"]=(
          "https://github.com/Phloraxx/Backscatter/blob/main/research/signal_coherence/"
          +site+"_metrics.json")
        metadata_path.write_text(json.dumps(meta,indent=2)+"\n")
    print("\nSITE",site,"RADAR_SHARED",report["common_valid_radar_cells"],
          "STRICT_OPERA",report["strict_opera_class_0_1_both_cells"],
          "MEDIAN_DELTA_DB",report["radar_delta_median_db"],
          "DELTA_MAD_DB",report["radar_delta_mad_db"])
    for name,stats in report["methods"].items():
        comparison=stats["reference_diagnostic"]
        print(name,
          "CANDIDATE_KM2",stats["candidate_any_km2"],
          "FLAGGED_FRACTION",stats["fraction_of_shared_valid_radar_flagged"],
          "GAIN_P",comparison["water_gain_vs_radar_decrease"]["precision"],
          "GAIN_R",comparison["water_gain_vs_radar_decrease"]["recall"],
          "GAIN_F1",comparison["water_gain_vs_radar_decrease"]["f1"],
          "LOSS_P",comparison["water_loss_vs_radar_increase"]["precision"],
          "LOSS_R",comparison["water_loss_vs_radar_increase"]["recall"],
          "LOSS_F1",comparison["water_loss_vs_radar_increase"]["f1"],
          "STABLE_LAND_FLAG",comparison["stable_nonwater_flag_fraction"])
    print("SAVED",out, "AND", RESULT_DIR/(site+"_metrics.json"))
    return report

def main():
    x=evaluate_site("kuttanad")
    y=evaluate_site("assam")
    summary={
      "experiment":"Fixed-parameter diagnostic SAR signal-change methods, not water/flood classifier",
      "date":"2026-11-14",
      "methods":["raw","median3","coherent"],
      "site_metric_files":["kuttanad_metrics.json","assam_metrics.json"],
      "key_caveat":"Different OPERA products and date offsets; do not pool F1 or claim field accuracy"
    }
    (RESULT_DIR/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")

if __name__=="__main__":
    main()
