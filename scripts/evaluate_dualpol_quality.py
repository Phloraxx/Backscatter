#!/usr/bin/env python3
"""Evaluate GCOV HVHV/HHHH and quality masks against OPERA WTR classes.

Requires existing NISAR HHHH, additional frequency-A HVHV, mask and
numberOfLooks Harmony TIFFs, and OPERA DSWx-HLS WTR TIFFs.

Methods:
- Warp *linear* 10m HH and HV power to native OPERA 30m grid by average.
- Filter non-positive power, NASA GCOV subswath invalid pixels (0/255).
- Treat OPERA class 0=non-water and 1=open water as exploratory reference.
- Select a 1-D water score from weighted HH/HV dB on the Oct29 WEST half.
- Test on Oct29 EAST half and test transfer on Nov10 NISAR vs Nov05 OPERA
  (5-day temporal mismatch). Compare strict class-0/1 change masks without
  training on their change labels.
- Assess a fixed +/-2dB both-channel sign gate as optional, non-tuned filter.
- Treat >=4 looks as a *sensitivity check*, NOT an established quality cutoff.

NO flood mapping or ground-truth claims.
"""
import json
import sys
from pathlib import Path
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling

from compare_nisar_opera_hls import ROOT, OUTPUT, read_pair, auc_roc
from evaluate_change_baseline import confusion

EXTRA = ROOT / "extra_layers"
RADAR_DATES = ("2026-10-29", "2026-11-10")
REPORT = OUTPUT / "dualpol_quality_evaluation.json"

def area_30m(arr):
    return int(arr.sum()) * 0.0009

def require_equal_grid(ds, reference):
    if ds.crs != reference.crs or ds.transform != reference.transform or \
       ds.width != reference.width or ds.height != reference.height:
        raise RuntimeError("Extra layer is not on same native NISAR raster grid")

def open_extra(date, layer, ref):
    path = EXTRA / ("nisar_" + date + "_" + layer + ".tif")
    with rasterio.open(path) as ds:
        require_equal_grid(ds, ref)
        arr = np.ma.asarray(ds.read(1, masked=True), dtype=np.float64).filled(np.nan)
    return arr

def average_to_30m(src, src_ds, target):
    out = np.full(target["label"].shape, np.nan, dtype=np.float32)
    reproject(
        source=np.asarray(src, dtype=np.float32), destination=out,
        src_transform=src_ds.transform, src_crs=src_ds.crs,
        src_nodata=np.nan, dst_transform=target["transform"],
        dst_crs=target["crs"], dst_nodata=np.nan,
        resampling=Resampling.average, num_threads=1,
    )
    return out

def read_dual(date, opera):
    with rasterio.open(ROOT / ("nisar_" + date + "_hhhh_raw.tif")) as ref:
        hh = np.ma.asarray(ref.read(1,masked=True),dtype=np.float64).filled(np.nan)
        hv = open_extra(date,"HVHV",ref)
        mask = open_extra(date,"mask",ref)
        looks = open_extra(date,"numberOfLooks",ref)
        mask_good = np.isfinite(mask) & (mask > 0) & (mask < 255)
        hh_good = mask_good & np.isfinite(hh) & (hh > 0)
        hv_good = mask_good & np.isfinite(hv) & (hv > 0)

        # Average power, then convert to dB. Do not interpolate already-logged values.
        a_hh = average_to_30m(np.where(hh_good,hh,np.nan),ref,opera)
        a_hv = average_to_30m(np.where(hv_good,hv,np.nan),ref,opera)
        a_looks = average_to_30m(np.where(mask_good,looks,np.nan),ref,opera)

        # Nodata beyond scene is 0, not excluded, for coverage fractions.
        # This is a validity *coverage* proxy, not a calibrated confidence score.
        coverage = np.full(opera["label"].shape,0,dtype=np.float32)
        reproject(
            source=mask_good.astype(np.float32), destination=coverage,
            src_transform=ref.transform,src_crs=ref.crs,
            dst_transform=opera["transform"],dst_crs=opera["crs"],
            resampling=Resampling.average,num_threads=1
        )
        native_counts = {
          "total_pixels":int(mask.size),
          "radar_valid_subswath":int(mask_good.sum()),
          "radar_invalid_zero":int(np.sum(mask == 0)),
          "radar_fill_255":int(np.sum(mask == 255)),
          "radar_masked_nodata":int(np.sum(~np.isfinite(mask))),
          "positive_hh":int(hh_good.sum()),
          "positive_hv":int(hv_good.sum()),
          "number_of_looks_percentiles": [
              round(float(v),3) for v in np.percentile(looks[mask_good & np.isfinite(looks)],[1,10,50,90,99])
          ],
        }
    with np.errstate(divide="ignore",invalid="ignore"):
        hh_db=10*np.log10(a_hh)
        hv_db=10*np.log10(a_hv)
    hh_db[~np.isfinite(hh_db)]=np.nan
    hv_db[~np.isfinite(hv_db)]=np.nan
    # Ratio HH/HV expressed in dB is HH_dB minus HV_dB.
    ratio_db=hh_db-hv_db
    return dict(date=date,hh_db=hh_db,hv_db=hv_db,ratio_db=ratio_db,
                looks=a_looks,coverage=coverage,native_counts=native_counts)

def score(d, weight):
    return (1.0-weight)*d["hh_db"]+weight*d["hv_db"]

def fit_feature(data, opt_labels, train, weights):
    ref=opt_labels==1
    best=None
    for w in weights:
        vals=score(data,w)
        for cutoff in np.arange(-40.,5.,0.25):
            pred=vals<=cutoff
            out=confusion(pred,ref,train)
            candidate={"weight_hv":float(w),"cutoff_db":round(float(cutoff),2),"train":out}
            if best is None or candidate["train"]["f1"]>best["train"]["f1"]:
                best=candidate
    return best

def evaluate_pair(first, second, first_labels, second_labels, selected, common, baseline):
    rows,cols=np.indices(first_labels.shape)
    west=cols<(first_labels.shape[1]//2)
    east=~west
    strict_first=np.isin(first_labels,[0,1])&common
    strict_second=np.isin(second_labels,[0,1])&common
    strict_change=strict_first&strict_second

    base_score_first=score(first,0.0)
    base_score_second=score(second,0.0)
    dual_score_first=score(first,selected["weight_hv"])
    dual_score_second=score(second,selected["weight_hv"])
    baseline_cutoff=baseline["cutoff_db"]
    dual_cutoff=selected["cutoff_db"]
    def describe(x0,x1,cutoff):
        first_water=x0<=cutoff
        last_water=x1<=cutoff
        y0=first_labels==1
        y1=second_labels==1
        masks=dict(
            static_west=confusion(first_water,y0,strict_first&west),
            static_east=confusion(first_water,y0,strict_first&east),
            static_second_date=confusion(last_water,y1,strict_second),
            gain=confusion(~first_water&last_water,~y0&y1,strict_change),
            loss=confusion(first_water&~last_water,y0&~y1,strict_change),
        )
        return first_water,last_water,masks

    base0,base1,bs=describe(base_score_first,base_score_second,baseline_cutoff)
    dual0,dual1,ds=describe(dual_score_first,dual_score_second,dual_cutoff)
    with np.errstate(invalid="ignore"):
        delta_hh=second["hh_db"]-first["hh_db"]
        delta_hv=second["hv_db"]-first["hv_db"]
    # Do not tune sign gate on these evaluation labels.
    gated_gain=(~dual0 & dual1 & (delta_hh<=-2.0) & (delta_hv<=-2.0))
    gated_loss=(dual0 & ~dual1 & (delta_hh>=2.0) & (delta_hv>=2.0))
    gain_ref=(first_labels==0)&(second_labels==1)
    loss_ref=(first_labels==1)&(second_labels==0)
    gates=dict(
      gain=confusion(gated_gain,gain_ref,strict_change),
      loss=confusion(gated_loss,loss_ref,strict_change),
      rule="dual-threshold transition AND both channels change by at least 2dB in expected direction; NOT tuned",
    )

    look_mask=(common & np.isfinite(first["looks"]) & np.isfinite(second["looks"]) &
               (first["looks"]>=4.0) & (second["looks"]>=4.0))
    look_strict=strict_change&look_mask
    filtered=dict(
        gain=confusion(~dual0&dual1,gain_ref,look_strict),
        loss=confusion(dual0&~dual1,loss_ref,look_strict),
        gain_gated=confusion(gated_gain,gain_ref,look_strict),
        loss_gated=confusion(gated_loss,loss_ref,look_strict),
        strict_valid_cells=int(look_strict.sum()),
        caveat=">=4 looks is a sensitivity check only, not an established threshold",
    )

    def roc_for(x,w,where):
        pred=score(x,w)
        valid=np.isfinite(pred)&where
        return round(float(auc_roc(first_labels[valid]==1,-pred[valid])),5) if valid.any() else None

    return {
        "shared_valid_all_radar_cells":int(common.sum()),
        "shared_valid_strict_reference_cells":int(strict_change.sum()),
        "spatial_holdout_cells":int((strict_first&east).sum()),
        "same_day_east_auc": {
            "hh":roc_for(first,0.0,strict_first&east),
            "hv":roc_for(first,1.0,strict_first&east),
            "weighted":roc_for(first,selected["weight_hv"],strict_first&east),
        },
        "single_hh":bs, "weighted_hh_hv":ds,
        "fixed_2db_joint_delta_gate":gates,
        "looks_ge4_sensitivity":filtered,
        "paired_ratio_db_median":[
            round(float(np.nanmedian(d["ratio_db"][common])),4) for d in (first,second)
        ]
    }

def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    with rasterio.open(ROOT/"nisar_2026-10-29_hhhh_raw.tif") as ds:
        bounds,crs=ds.bounds,ds.crs
    optical0=read_pair("2026-10-29","S2B","2026-10-29",bounds,crs)
    optical1=read_pair("2026-11-05","S2A","2026-11-10",bounds,crs)
    assert optical0["label"].shape==optical1["label"].shape and \
           optical0["transform"]==optical1["transform"],"Different reference grids"
    date0=read_dual("2026-10-29",optical0)
    date1=read_dual("2026-11-10",optical0)
    mask_all=(np.isfinite(date0["hh_db"])&np.isfinite(date0["hv_db"])&
              np.isfinite(date1["hh_db"])&np.isfinite(date1["hv_db"])&
              (date0["coverage"]>=0.99)&(date1["coverage"]>=0.99))
    cols=np.indices(mask_all.shape)[1]
    training=(np.isin(optical0["label"],[0,1])&mask_all&
              (cols<(mask_all.shape[1]//2)))
    if int(training.sum())<1000:
        raise RuntimeError("Insufficient shared quality-filtered training cells")
    hh=fit_feature(date0,optical0["label"],training,[0.0])
    combo=fit_feature(date0,optical0["label"],training,[0.0,0.25,0.5,0.75,1.0])
    ev=evaluate_pair(date0,date1,optical0["label"],optical1["label"],combo,mask_all,hh)
    report=dict(
      study="Kuttanad dual-polarization and subswath-mask sensitivity",
      sources={
        "nisar":["2026-10-29","2026-11-10"],
        "reference_opera":["2026-10-29","2026-11-05"],
        "temporal_gap_second_days":5,
        "collection":"NISAR_L2_GCOV_V1 C3622241360-ASF",
        "variables":["/science/LSAR/GCOV/grids/frequencyA/HHHH",
                     "/science/LSAR/GCOV/grids/frequencyA/HVHV",
                     "/science/LSAR/GCOV/grids/frequencyA/mask",
                     "/science/LSAR/GCOV/grids/frequencyA/numberOfLooks"],
      },
      methodology="HH/HV powers in common quality-masked 30m cells, log10 after averaging",
      mask_coverage_threshold=0.99,
      mask_valid_codes="subswath index 1-254; mask 0 invalid, 255 fill; NaN excluded",
      number_of_looks_method="quality sensitivity test at >=4 looks",
      training="Oct29 west half, OPERA 0 nonwater vs 1 open water; no change-label fitting",
      fit_hh_only=hh,fit_weighted=combo,
      individual_dates={date0["date"]:date0["native_counts"],
                        date1["date"]:date1["native_counts"]},
      results=ev,
      limitations=[
        "OPERA is satellite classification, not field ground truth",
        "Second radar on Nov10 versus optical label Nov05, mismatch 5 days",
        "One landscape and date pair; crop management and spatial autocorrelation confound results",
        "A good static water-versus-land classifier is not a validated flood-change detector",
        "Weight search is trained on Oct29 west half and evaluated on east half",
        "Averaging 10m SAR onto 30m grid can blur mixed shorelines",
        "Number-of-looks >=4 is a convenience sensitivity filter, not validated confidence",
      ]
    )
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    # Save the cross-polarization power as a GeoTIFF and PNG preview only if actual
    # source layers exist and have compatible georeferencing.
    generate_preview(date0,date1,optical0,ev)
    print("REPORT",REPORT)
    for name,d in (("HH-only",ev["single_hh"]),("Weighted HH/HV",ev["weighted_hh_hv"])):
        print(name,"STATIC_EAST_F1",d["static_east"]["f1"],
              "STATIC_SECOND_F1",d["static_second_date"]["f1"],
              "GAIN_F1",d["gain"]["f1"],"LOSS_F1",d["loss"]["f1"],
              "GAIN_PRECISION",d["gain"]["precision"],"LOSS_PRECISION",d["loss"]["precision"])
    print("CHOSEN_WEIGHT",combo["weight_hv"],"TRAIN_F1",combo["train"]["f1"],
          "THRESHOLD",combo["cutoff_db"])
    print("SAME_DAY_EAST_AUC",ev["same_day_east_auc"])
    print("JOINT_DELTA_GATE",ev["fixed_2db_joint_delta_gate"])
    print("LOOKS_SENSITIVITY",ev["looks_ge4_sensitivity"])
    print("PER_DATE_NATIVE_MASK",{date: v["native_counts"]["radar_valid_subswath"]
      for date,v in ((date0["date"],date0),(date1["date"],date1))})
    print("SHARED_QUALITY_CELLS",int(mask_all.sum()))

def generate_preview(before,after,optical,evaluation):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,3,figsize=(14,4.5),constrained_layout=True)
    for ax,img,title,limits in zip(
        axs,
        (before["hv_db"],after["hv_db"],after["hv_db"]-before["hv_db"]),
        ("HVHV 29 Oct (dB)","HVHV 10 Nov (dB)","HVHV change, Nov − Oct (dB)"),
        ((-36,-10),(-36,-10),(-8,8))):
        im=ax.imshow(np.ma.masked_invalid(img),vmin=limits[0],vmax=limits[1],
                     cmap="viridis" if "change" not in title else "coolwarm")
        fig.colorbar(im,ax=ax,shrink=.8)
        ax.set_title(title,fontsize=10);ax.axis("off")
    fig.suptitle("Backscatter — cross-polarization measured changes (not flood extent)")
    fig.savefig(OUTPUT/"crosspol_diagnostic.png",dpi=150)
    plt.close(fig)

if __name__ == "__main__":
    main()
