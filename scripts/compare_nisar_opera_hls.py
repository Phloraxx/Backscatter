#!/usr/bin/env python3
"""Backscatter: diagnostic comparison of validated NISAR GCOV and OPERA DSWx-HLS.

Reproducible, evidence-limited experiment. No water/flood area is inferred from
NISAR; OPERA is a satellite-classification reference, not ground truth.

NISAR October 29 / November 10, 2026; OPERA Oct 29 (S2B) / Nov 05 (S2A).
Averaging calibrated *linear* NISAR HHHH power onto the optical native 30 m
grid avoids pseudo-replication of 10 m radar cells. Convert to dB afterward.

Requires numpy rasterio matplotlib; source files already on the user's Mac.
"""
import json
from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds, reproject, Resampling

ROOT = Path.home() / "Downloads" / "backscatter-validated-kuttanad"
HLS_DIR = ROOT / "opera_hls"
OUTPUT = ROOT / "independent_comparison"
DATES = {"2026-10-29": "S2B", "2026-11-05": "S2A"}
# Radar dated Nov 10 compared against 5-days-earlier Nov 05 optical only as exploratory context.
RADAR_DATES = {"2026-10-29": "2026-10-29", "2026-11-05": "2026-11-10"}
# WTR v1.1: 0 nonwater, 1 open water, 2 partial water; 252/253/254/255 invalid.
OPEN_WATER, NON_WATER, PARTIAL = 1, 0, 2

def get_hls_product(date, sensor):
    paths = sorted(HLS_DIR.glob("OPERA_L3_DSWx-HLS_T43PFL_" + date.replace("-", "") + "*" +
                                "_" + sensor + "_30_v1.1_B01_WTR.tif"))
    if len(paths) != 1:
        raise RuntimeError("Expected exactly one HLS product for " + date + " " + sensor)
    return paths[0]

def radar_to_optical_grid(radar_date, window_transform, shape, ref_crs):
    radar_path = ROOT / ("nisar_" + radar_date + "_hhhh_raw.tif")
    with rasterio.open(radar_path) as ds:
        src = ds.read(1, masked=True).filled(np.nan).astype(np.float32)
        invalid = (~np.isfinite(src)) | (src <= 0)
        src[invalid] = np.nan
        out = np.full(shape, np.nan, dtype=np.float32)
        reproject(source=src, destination=out,
                  src_transform=ds.transform, src_crs=ds.crs,
                  src_nodata=np.nan, dst_transform=window_transform,
                  dst_crs=ref_crs, dst_nodata=np.nan,
                  resampling=Resampling.average, num_threads=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        backscatter_db = 10 * np.log10(out)
    backscatter_db[~np.isfinite(backscatter_db)] = np.nan
    return backscatter_db

def read_pair(opera_date, sensor, radar_date, reference_bounds, radar_crs):
    path = get_hls_product(opera_date, sensor)
    with rasterio.open(path) as ds:
        bbox = transform_bounds(radar_crs, ds.crs, *reference_bounds)
        window = from_bounds(*bbox, transform=ds.transform).round_offsets().round_lengths()
        label = ds.read(1, window=window, boundless=True, fill_value=255)
        transform = ds.window_transform(window)
        crs = ds.crs
        resolution = ds.res
    radar = radar_to_optical_grid(radar_date, transform, label.shape, crs)
    return dict(opera_date=opera_date, radar_date=radar_date, sensor=sensor,
                label=label, radar_db=radar,
                transform=transform, crs=str(crs), resolution=resolution,
                source_file=path.name)

def auc_roc(ground_truth, scores):
    """Rank-based ROC-AUC with tie-aware averaging; no external ML package."""
    y = np.asarray(ground_truth, dtype=bool)
    z = np.asarray(scores, dtype=float)
    npos, nneg = int(y.sum()), int((~y).sum())
    if not npos or not nneg:
        return None
    order = np.argsort(z, kind="mergesort")
    sorted_scores = z[order]
    _, first, counts = np.unique(sorted_scores, return_index=True, return_counts=True)
    group_midrank = first + (counts + 1) / 2.0
    ranks = np.repeat(group_midrank, counts)
    ranks_unsorted = np.empty_like(ranks)
    ranks_unsorted[order] = ranks
    return float((ranks_unsorted[y].sum() - npos*(npos+1)/2.0) / (npos*nneg))

def radar_diagnostics(x):
    classes = x["label"]
    db = x["radar_db"]
    any_good = np.isin(classes, [0, 1, 2]) & np.isfinite(db)
    strict = np.isin(classes, [0, 1]) & np.isfinite(db)
    y = classes[strict] == 1
    score = -db[strict]  # darker NISAR return -> higher hypothesized open-water likelihood
    out = {
        "opera_product": x["source_file"], "sensor": x["sensor"], "optical_date": x["opera_date"],
        "radar_date": x["radar_date"], "days_radar_minus_optical":
            int((np.datetime64(x["radar_date"]) - np.datetime64(x["opera_date"])).astype(int)),
        "grid_resolution_m": list(x["resolution"]),
        "aoi_grid_cells": int(classes.size),
        "optically_valid_cells_0_1_2": int(np.isin(classes, [0, 1, 2]).sum()),
        "optically_invalid_or_masked_cells": int((~np.isin(classes, [0, 1, 2])).sum()),
        "radar_plus_optical_valid_cells": int(any_good.sum()),
        "strict_openwater_nonwater_cells": int(strict.sum()),
        "classes": {
            str(val): {
                "n_common_with_radar": int(((classes == val) & np.isfinite(db)).sum()),
                "median_radar_db": (
                    round(float(np.nanmedian(db[(classes == val) & np.isfinite(db)])), 4)
                    if ((classes == val) & np.isfinite(db)).any() else None)
            } for val in (0, 1, 2)
        },
        "diagnostic_auc_openwater_vs_nonwater": (
            round(auc_roc(y, score), 5) if y.any() and (~y).any() else None
        ),
        "water_score": "-NISAR HHHH dB (lower backscatter implies higher open-water likelihood)",
        "note": "Single-scene same-day classification discrimination if offset is 0 days; not flood-change validation",
    }
    if int(strict.sum()) > 0:
        out["fixed_threshold_checks"] = {}
        for threshold in (-22., -20., -18., -16., -14.):
            guess = db[strict] <= threshold
            tp = int((guess & y).sum())
            fp = int((guess & ~y).sum())
            fn = int((~guess & y).sum())
            tn = int((~guess & ~y).sum())
            precision = tp / (tp + fp) if tp + fp else 0.
            recall = tp / (tp + fn) if tp + fn else 0.
            f1 = 2*precision*recall/(precision+recall) if precision+recall else 0.
            out["fixed_threshold_checks"][str(int(threshold))] = {
                "tp": tp, "fp": fp, "fn": fn, "tn": tn,
                "precision": round(precision, 4), "recall": round(recall, 4),
                "f1": round(f1, 4)
            }
    return out

def optical_change(first, second):
    if (first["label"].shape != second["label"].shape or
            first["transform"] != second["transform"] or
            first["crs"] != second["crs"]):
        raise RuntimeError("OPERA products not on the same 30m geospatial grid")
    a, b = first["label"], second["label"]
    valid = np.isin(a, [0, 1, 2]) & np.isin(b, [0, 1, 2])
    wa, wb = np.isin(a, [1, 2]), np.isin(b, [1, 2])
    new, lost, stable = valid & ~wa & wb, valid & wa & ~wb, valid & wa & wb
    stableland = valid & ~wa & ~wb
    factor = abs(first["transform"].a*first["transform"].e -
                 first["transform"].b*first["transform"].d)/1e6
    counts = {k: int(v.sum()) for k, v in [
        ("valid_both", valid), ("new_optical_water", new), ("lost_optical_water", lost),
        ("stable_optical_water", stable), ("stable_optical_nonwater", stableland)]}
    return dict(optical_dates=[first["opera_date"], second["opera_date"]],
                sensors=[first["sensor"], second["sensor"]],
                counts=counts,
                area_km2={k: round(float(v*factor), 4) for k,v in counts.items()},
                net_optical_water_change_km2=round(float((new.sum()-lost.sum())*factor),4),
                note="7-day independent optical DSWx classified-state change, not NISAR flood validation; cloud/partial water may influence results")

def plots(first, second, result):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 3, figsize=(13, 8), constrained_layout=True)
    for i, x in enumerate((first, second)):
        db = x["radar_db"]
        cls = x["label"]
        m = ax[i,0].imshow(np.ma.masked_invalid(db), cmap="viridis", vmin=-27,vmax=0)
        ax[i,0].set_title("NISAR " + x["radar_date"] + " (HHHH dB, 30 m)")
        fig.colorbar(m,ax=ax[i,0],shrink=.72)
        wtr = np.where(cls==0,0,np.where(cls==1,1,np.where(cls==2,2,3)))
        m = ax[i,1].imshow(wtr,cmap="viridis",vmin=0,vmax=3)
        ax[i,1].set_title("OPERA "+x["opera_date"]+" ("+x["sensor"]+")\n0=nonwater 1=open 2=partial 3=masked")
        fig.colorbar(m,ax=ax[i,1],shrink=.72)
        openwater = np.isfinite(db) & (cls==1)
        land = np.isfinite(db) & (cls==0)
        ax[i,2].hist(db[land],bins=75,range=(-35,5),density=True,alpha=.55,label="OPERA nonwater")
        ax[i,2].hist(db[openwater],bins=75,range=(-35,5),density=True,alpha=.55,label="OPERA open water")
        ax[i,2].set_title("Radar backscatter by optical class")
        ax[i,2].set_xlabel("HHHH dB")
        ax[i,2].legend(fontsize=8)
    for z in ax.flat:
        if z is not ax[0,2] and z is not ax[1,2]:z.axis("off")
    fig.suptitle("NISAR vs OPERA DSWx-HLS diagnostic — same-day Oct 29 / 5-day offset Nov 10",fontsize=12)
    out=OUTPUT/"nisar_opera_diagnostic.png"
    fig.savefig(out,dpi=145);plt.close(fig)
    print("FIGURE",out)

def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with rasterio.open(ROOT/"nisar_2026-10-29_hhhh_raw.tif") as ds:
        bounds,crs = ds.bounds,ds.crs
    values = [read_pair(day, sensor, RADAR_DATES[day], bounds, crs)
              for day,sensor in DATES.items()]
    comparisons = [radar_diagnostics(x) for x in values]
    optical = optical_change(*values)
    result = {"purpose":"Experimental consistency checks; no flood classifier",
              "study":"Kuttanad, Kerala",
              "reference_collection":"C2617126679-POCLOUD",
              "reference_product":"OPERA DSWx-HLS v1.1",
              "nisar_collection":"C3622241360-ASF",
              "comparisons":comparisons,"optical_change":optical,
              "limitations":[
                  "OPERA is optical satellite-derived classification, not field ground truth",
                  "Second NISAR acquisition is five days later than second OPERA reference",
                  "Class 2 partial surface water excluded from strict binary ROC-AUC",
                  "OPERA class 252/253/254/255 excluded as invalid or ambiguous",
                  "Radar power was averaged to native 30 m optical grid before log10",
                  "Spatial correlation and crop management can bias diagnostic metrics",
                  "AUC and fixed thresholds measure single-date discrimination, not flood change",
                  "No spatial holdout threshold calibration or uncertainty calibration",
              ]}
    path=OUTPUT/"nisar_opera_diagnostic.json"
    path.write_text(json.dumps(result,indent=2)+"\n")
    plots(*values,result)
    print("RESULTS")
    for x in comparisons:
        print(x["optical_date"],x["sensor"],"radar",x["radar_date"],
              "days_offset",x["days_radar_minus_optical"],
              "valid",x["radar_plus_optical_valid_cells"],
              "strict",x["strict_openwater_nonwater_cells"],
              "class_medians", {c:v["median_radar_db"] for c,v in x["classes"].items()},
              "ROC_AUC",x["diagnostic_auc_openwater_vs_nonwater"])
        print("THRESHOLDS",x.get("fixed_threshold_checks"))
    print("OPTICAL_CHANGE",json.dumps(optical["area_km2"]),optical["net_optical_water_change_km2"])
    print("JSON",path)

if __name__ == "__main__":
    main()
