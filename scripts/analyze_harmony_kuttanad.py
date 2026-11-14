#!/usr/bin/env python3
"""Analyze two small validated NISAR HHHH GeoTIFFs obtained via Harmony.

Usage:
  pip install numpy rasterio matplotlib
  python scripts/analyze_harmony_kuttanad.py

Writes georeferenced dB rasters, a before/after/delta preview, and a JSON
summary. Results measure radar backscatter changes, NOT inundation extent.
"""
import json
from pathlib import Path

ROOT = Path.home() / "Downloads" / "backscatter-validated-kuttanad"
DATES = ("2026-10-29", "2026-11-10")
GRANULES = (
    "NISAR_L2_PR_GCOV_034_077_D_084_4005_DHDH_A_20261029T132026_20261029T132100_P05036_N_F_J_001",
    "NISAR_L2_PR_GCOV_035_077_D_084_4005_DHDH_A_20261110T132027_20261110T132100_P05036_N_F_J_001",
)


def main():
    import numpy as np
    import rasterio

    arrays, info, profiles = [], [], []
    for date in DATES:
        path = ROOT / ("nisar_" + date + "_hhhh_raw.tif")
        with rasterio.open(path) as src:
            raster = src.read(1, masked=True).filled(np.nan).astype(np.float32)
            arrays.append(raster)
            info.append((str(src.crs), tuple(src.transform), raster.shape))
            profiles.append(src.profile.copy())
    if info[0] != info[1]:
        raise RuntimeError("Rasters are not on the same grid; explicitly reproject before analysis")

    before, after = arrays
    valid = (np.isfinite(before) & np.isfinite(after)
             & (before > 0) & (after > 0))
    if int(valid.sum()) < 200:
        raise RuntimeError("Insufficient shared positive radar pixels")

    before_db = np.full(before.shape, np.nan, dtype=np.float32)
    after_db = np.full(before.shape, np.nan, dtype=np.float32)
    before_db[valid] = 10.0 * np.log10(before[valid])
    after_db[valid] = 10.0 * np.log10(after[valid])
    delta = after_db - before_db
    vals = delta[valid]

    with rasterio.open(ROOT / ("nisar_" + DATES[0] + "_hhhh_raw.tif")) as src:
        pixel_area_m2 = abs(src.transform.a * src.transform.e - src.transform.b * src.transform.d)
        resolution = [abs(src.transform.a), abs(src.transform.e)]
        bounds = [float(v) for v in src.bounds]

    report = {
        "dataset": "NISAR_L2_GCOV_V1 validated HHHH gamma0 power",
        "dates": list(DATES),
        "granule_ids": list(GRANULES),
        "grid": {"crs": info[0][0], "shape": list(before.shape),
                 "resolution_m": resolution, "bounds_m": bounds},
        "shared_valid_pixels": int(valid.sum()),
        "shared_valid_km2": round(float(valid.sum() * pixel_area_m2 / 1e6), 5),
        "median_before_db": round(float(np.median(before_db[valid])), 4),
        "median_after_db": round(float(np.median(after_db[valid])), 4),
        "paired_median_delta_db": round(float(np.median(vals)), 4),
        "paired_mean_delta_db": round(float(np.mean(vals)), 4),
        "delta_percentiles_db": [round(float(v), 4) for v in np.percentile(vals, [10, 25, 75, 90])],
        "fraction_delta_less_minus3db": round(float((vals < -3).mean()), 5),
        "fraction_delta_greater_plus3db": round(float((vals > 3).mean()), 5),
        "fraction_abs_delta_over3db": round(float((np.abs(vals) > 3).mean()), 5),
        "method": "10 * log10 of positive finite GCOV HHHH power; Nov 10 minus Oct 29 on common native grid",
        "warning": "Unclassified radar backscatter changes; not validated flood or water coverage estimates",
    }
    for date, arr in zip(DATES, (before_db, after_db)):
        profile = profiles[0].copy()
        profile.update(dtype="float32", nodata=np.nan, compress="deflate", predictor=3)
        with rasterio.open(ROOT / ("nisar_" + date + "_hhhh_db.tif"), "w", **profile) as dst:
            dst.write(arr, 1)
    profile = profiles[0].copy()
    profile.update(dtype="float32", nodata=np.nan, compress="deflate", predictor=3)
    with rasterio.open(ROOT / "nisar_delta_hhhh_db.tif", "w", **profile) as dst:
        dst.write(delta.astype(np.float32), 1)

    (ROOT / "nisar_pair_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
        for ax, arr, title, (lo, hi), cmap in zip(
            axes, (before_db, after_db, delta),
            ("NISAR HHHH — 29 Oct 2026", "NISAR HHHH — 10 Nov 2026",
             "Backscatter change: Nov minus Oct"),
            ((-27, 0), (-27, 0), (-8, 8)),
            ("viridis", "viridis", "coolwarm")
        ):
            im = ax.imshow(np.ma.masked_invalid(arr), vmin=lo, vmax=hi, cmap=cmap)
            ax.set_title(title, fontsize=11)
            ax.axis("off")
            fig.colorbar(im, ax=ax, shrink=0.72, label="dB")
        fig.suptitle("Kuttanad • NISAR validated GCOV, 10 m • Unclassified radar signal")
        fig.savefig(ROOT / "nisar_hhhh_comparison.png", dpi=145)
        plt.close(fig)
    except ImportError:
        print("No matplotlib; PNG preview skipped")
    print(json.dumps(report, indent=2))
    print("Outputs saved:", ROOT)


if __name__ == "__main__":
    main()
