#!/usr/bin/env python3
"""Export a small honest Backscatter web demo from real NASA/OPERA raster files.

Input data must be present under ~/Downloads/backscatter-validated-kuttanad.
Output is web/public/data, tracked in Git (not raw NASA HDF5/GeoTIFF files).

NISAR HHHH power -> average to OPERA's native 30m grid -> 10*log10 power.
No inferred flood classifications are generated.
"""
import json
import sys
from pathlib import Path
import numpy as np
import rasterio
from rasterio.warp import transform
from PIL import Image
import matplotlib
matplotlib.use("Agg")
from matplotlib import colormaps, colors

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/"scripts"))
from compare_nisar_opera_hls import ROOT as DATA, read_pair
from evaluate_dualpol_quality import read_dual

OUTPUT = ROOT/"web"/"public"/"data"
OUT_META = OUTPUT/"meta.json"


def rgba_float(data, low, high, cmap):
    norm = np.clip((data-low)/(high-low), 0, 1)
    norm = np.nan_to_num(norm, nan=0.0)
    rgba = np.rint(colormaps.get_cmap(cmap)(norm)*255).astype(np.uint8)
    rgba[~np.isfinite(data),3] = 0
    return rgba

def optical_rgba(label):
    result = np.zeros((*label.shape,4),dtype=np.uint8)
    palette = {0: (246,241,225,185),1: (31,112,196,232),2: (71,202,175,208)}
    for k,color in palette.items():result[label==k] = color
    return result

def main():
    OUTPUT.mkdir(exist_ok=True,parents=True)
    with rasterio.open(DATA/"nisar_2026-10-29_hhhh_raw.tif") as ref:
        bounds,crs=ref.bounds,ref.crs
    a=read_pair("2026-10-29","S2B","2026-10-29",bounds,crs)
    b=read_pair("2026-11-05","S2A","2026-11-10",bounds,crs)
    assert a["transform"] == b["transform"] and a["label"].shape == b["label"].shape
    H,W=a["label"].shape
    pre=np.asarray(a["radar_db"],dtype=np.float32).astype("<f4")
    post=np.asarray(b["radar_db"],dtype=np.float32).astype("<f4")
    delta=post-pre
    dual_before=read_dual("2026-10-29",a)
    dual_after=read_dual("2026-11-10",a)
    hv_before=np.asarray(dual_before["hv_db"],dtype=np.float32).astype("<f4")
    hv_after=np.asarray(dual_after["hv_db"],dtype=np.float32).astype("<f4")
    hv_delta=hv_after-hv_before
    optical=np.asarray(a["label"],dtype=np.uint8)
    Image.fromarray(rgba_float(pre,-27,0,"viridis")).save(OUTPUT/"oct29.png",optimize=True)
    Image.fromarray(rgba_float(post,-27,0,"viridis")).save(OUTPUT/"nov10.png",optimize=True)
    Image.fromarray(rgba_float(delta,-8,8,"coolwarm")).save(OUTPUT/"change.png",optimize=True)
    Image.fromarray(rgba_float(hv_delta,-8,8,"coolwarm")).save(OUTPUT/"hv_change.png",optimize=True)
    Image.fromarray(optical_rgba(optical)).save(OUTPUT/"opera_oct29.png",optimize=True)
    (OUTPUT/"pixels.bin").write_bytes(pre.tobytes()+post.tobytes()+hv_before.tobytes()+hv_after.tobytes()+optical.tobytes())

    tf=a["transform"]
    x0,y0=tf.c,tf.f
    xs=[x0,x0+W*tf.a,x0+W*tf.a,x0]
    ys=[y0,y0,y0+H*tf.e,y0+H*tf.e]
    lons,lats=transform(a["crs"],"EPSG:4326",xs,ys)
    corners=[[round(float(lon),8),round(float(lat),8)] for lon,lat in zip(lons,lats)]
    reference=json.loads((DATA/"independent_comparison/nisar_opera_diagnostic.json").read_text())
    baseline=json.loads((DATA/"independent_comparison/change_baseline.json").read_text())
    radar=json.loads((DATA/"nisar_pair_summary.json").read_text())
    dual=json.loads((DATA/"independent_comparison/dualpol_quality_evaluation.json").read_text())
    meta={
        "title":"Backscatter — Kuttanad experimental SAR surface-change viewer",
        "bbox_wgs84":[76.42,9.4,76.49,9.47],
        "crs":a["crs"],"rows":H,"cols":W,
        "x0":float(x0),"y0":float(y0),
        "pixel_width_m":float(tf.a),"pixel_height_m":float(-tf.e),
        "image_coordinates_lonlat":corners,
        "primary_dates":["2026-10-29","2026-11-10"],
        "opera_date":"2026-10-29",
        "opera_product":reference["comparisons"][0]["opera_product"],
        "data_binary_format":"little-endian Float32 HH_before[N], Float32 HH_after[N], Float32 HV_before[N], Float32 HV_after[N], Uint8 OPERA_WTR[N]; N=rows*cols",
        "statistics":{
            "radar_shared_valid_km2":radar["shared_valid_km2"],
            "radar_paired_median_delta_db":radar["paired_median_delta_db"],
            "same_day_opera_auc":reference["comparisons"][0]["diagnostic_auc_openwater_vs_nonwater"],
            "east_holdout_static_f1":baseline["static_water_test_east"]["f1"],
            "gain_f1":dual["results"]["single_hh"]["gain"]["f1"],
            "loss_f1":dual["results"]["single_hh"]["loss"]["f1"],
            "dualpol_static_east_f1":dual["results"]["weighted_hh_hv"]["static_east"]["f1"],
            "dualpol_gain_f1":dual["results"]["weighted_hh_hv"]["gain"]["f1"],
            "dualpol_loss_f1":dual["results"]["weighted_hh_hv"]["loss"]["f1"],
        },
        "limitations":[
            "Not a flood detection or prediction product",
            "NISAR radar change does not uniquely imply water change",
            "OPERA layer is an optical satellite classification, not ground truth",
            "The second reference used in comparison was 2026-11-05; five days before NISAR 2026-11-10",
            "Spatially correlated pixels and crops affect reference agreement",
            "HVHV helps static discrimination in this test but worsens candidate gain/loss mask F1",
        ],
        "credits":"NISAR validated GCOV V1 / NASA and ISRO; NASA OPERA DSWx-HLS v1.1; NASA Earthdata/ASF/PO.DAAC",
        "source_manifest":"https://github.com/Phloraxx/Backscatter/blob/main/research/kuttanad_validated_2026_10_11/scene_manifest.json"
    }
    OUT_META.write_text(json.dumps(meta,indent=2)+"\n")
    for p in sorted(OUTPUT.iterdir()):print(p.name,p.stat().st_size)
    print("GRID",W,H,"CORNERS",corners)
    print("OPERA_CLASS_COUNTS",{int(x):int(n) for x,n in zip(*np.unique(optical,return_counts=True))})
    print("READY for static web build")

if __name__=="__main__":
    main()
