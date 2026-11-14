#!/usr/bin/env python3
"""Export *measured* Lower Assam NISAR and OPERA DSWx-S1 case for the web viewer.

Reads authenticated local GeoTIFFs, writes lightweight transparent overlays,
a georeferenced pixel-metadata JSON, and a compact binary 30m measurement grid.
No inferred flood water masks are exported. Raw data and tokens remain local.
"""
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine
from rasterio.warp import transform
from PIL import Image
from matplotlib import colormaps

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from compare_assam_opera import ROOT, observe

OUTPUT = REPO / "web" / "public" / "data" / "assam"

def rgba_radar(values, lo, hi, cmap):
    normalized = np.clip((values-lo)/(hi-lo),0,1)
    normalized = np.nan_to_num(normalized,nan=0)
    out = np.rint(colormaps.get_cmap(cmap)(normalized)*255).astype(np.uint8)
    out[~np.isfinite(values),3]=0
    return out

def rgba_reference(labels):
    rgba=np.zeros((*labels.shape,4),dtype=np.uint8)
    colors = {
        0:(246,241,225,185),
        1:(31,112,196,230),
        3:(71,202,175,210),
    }
    for cls,rgb in colors.items():rgba[labels==cls]=rgb
    return rgba

def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    a=observe("2026-10-28","2026-10-31")
    b=observe("2026-11-09","2026-11-10")
    if a["radar_db"].shape!=b["radar_db"].shape or a["grid_transform"]!=b["grid_transform"]:
        raise RuntimeError("Images use different reference grids")
    pre=np.asarray(a["radar_db"],dtype="<f4")
    post=np.asarray(b["radar_db"],dtype="<f4")
    delta=post-pre
    optical=np.asarray(a["labels"],dtype=np.uint8)
    # The common viewer binary format reserves HV channels; Assam's two HV layers
    # have not been extracted. Fill those channels with NaN, never fake HV pixels.
    missing_hv=np.full(pre.shape,np.nan,dtype="<f4")
    Image.fromarray(rgba_radar(pre,-27,0,"viridis")).save(OUTPUT/"before.png",optimize=True)
    Image.fromarray(rgba_radar(post,-27,0,"viridis")).save(OUTPUT/"after.png",optimize=True)
    Image.fromarray(rgba_radar(delta,-8,8,"coolwarm")).save(OUTPUT/"change.png",optimize=True)
    Image.fromarray(rgba_reference(optical)).save(OUTPUT/"opera.png",optimize=True)
    (OUTPUT/"pixels.bin").write_bytes(pre.tobytes()+post.tobytes()+
                                     missing_hv.tobytes()+missing_hv.tobytes()+optical.tobytes())
    tf=Affine(*a["grid_transform"][:6])
    rows,cols=pre.shape
    x=[tf.c,tf.c+cols*tf.a,tf.c+cols*tf.a,tf.c]
    y=[tf.f,tf.f,tf.f+rows*tf.e,tf.f+rows*tf.e]
    lons,lats=transform(a["grid_crs"],"EPSG:4326",x,y)
    corners=[[round(float(lon),8),round(float(lat),8)] for lon,lat in zip(lons,lats)]
    results=json.loads((ROOT/"analysis/assam_nisar_opera_diagnostic.json").read_text())
    meta={
        "title":"Backscatter — Lower Assam measured SAR surface-change case",
        "study":"assam",
        "region_name":"Lower Assam",
        "region_state":"Assam, India",
        "study_number":"02",
        "crs":a["grid_crs"],"rows":rows,"cols":cols,
        "x0":float(tf.c),"y0":float(tf.f),
        "pixel_width_m":float(tf.a),"pixel_height_m":float(-tf.e),
        "image_coordinates_lonlat":corners,
        "bbox_wgs84":[90.28,26.16,90.35,26.23],
        "primary_dates":["2026-10-28","2026-11-09"],
        "opera_date":"2026-10-31",
        "opera_product":a["reference_filename"],
        "opera_kind":"DSWx-S1",
        "opera_reference_offsets_days":[3,1],
        "radar_polarizations":["HHHH"],
        "data_binary_format":"little-endian Float32 HH_before[N], Float32 HH_after[N], Float32 HV_before[N]=NaN, Float32 HV_after[N]=NaN, Uint8 OPERA_WTR[N]; N=rows*cols",
        "statistics":{
            "radar_shared_valid_km2":results["shared_valid_radar_area_km2"],
            "radar_paired_median_delta_db":results["median_nisar_delta_db"],
            "east_holdout_static_f1":results["first_reference_east_test"]["f1"],
            "gain_f1":results["candidate_gain_agreement"]["f1"],
            "loss_f1":results["candidate_loss_agreement"]["f1"],
            "kerala_threshold_transfer_f1":results["unmodified_kerala_threshold_transfer"]["first_reference_all_strict"]["f1"],
            "kerala_threshold_transfer_gain_f1":results["unmodified_kerala_threshold_transfer"]["candidate_gain_agreement"]["f1"],
            "kerala_threshold_transfer_loss_f1":results["unmodified_kerala_threshold_transfer"]["candidate_loss_agreement"]["f1"],
            "static_fitted_threshold_db":results["fitted_water_threshold_db"],
        },
        "limitations":[
            "Measured radar change only; not confirmed flooding",
            "OPERA DSWx-S1 reference is Sentinel-1 C-band classification, not field ground truth",
            "Radar and reference acquisitions are offset by 3 and 1 calendar days",
            "Inundated vegetation is OPERA class 3; excluded from strict class 0-vs-1 F1",
            "Same Kuttanad threshold transferred to Assam showed poor static and zero change-mask agreement",
            "Mode-specific pre-Nov 12 2026 NISAR radiometric residuals may affect some acquisitions; scene status unknown",
        ],
        "credits":"NASA–ISRO NISAR validated GCOV V1; NASA OPERA DSWx-S1 v1.0; Earthdata/ASF/PO.DAAC",
        "source_manifest":"https://github.com/Phloraxx/Backscatter/blob/main/research/assam_validated_2026_10_11/scene_manifest.json",
        "analysis_report":"https://github.com/Phloraxx/Backscatter/blob/main/research/assam_validated_2026_10_11/assam_nisar_opera_diagnostic.json",
    }
    (OUTPUT/"meta.json").write_text(json.dumps(meta,indent=2)+"\n")
    if (OUTPUT/"pixels.bin").stat().st_size!=rows*cols*17:
        raise RuntimeError("Binary data file format mismatch")
    print("ASSAM_EXPORT",rows,cols)
    for p in sorted(OUTPUT.iterdir()):print(p.name,p.stat().st_size)
    print("COMMON_VALID_RADAR_KM2",meta["statistics"]["radar_shared_valid_km2"])
    print("OPERA_S1_CLASSES",{int(k):int(v) for k,v in zip(*np.unique(optical,return_counts=True))})

if __name__=="__main__":
    main()
