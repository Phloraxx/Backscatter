# Backscatter project status — 2026-11-03

## Scope and decision

**Primary candidate:** Kuttanad, Kerala, India; water extent / wetland inundation change. **Backup:** Lower Assam floodplain. NISAR-based flood detection remains a hypothesis, not an observed result. NISAR L2 GCOV is the proposed main data source; OPERA DSWx-S1 is an independent Sentinel-1 water-product comparison.

## Feasibility checklist

| Gate | Status as of 2026-11-03 | Evidence / next step |
|---|---|---|
| 1. Compatible NISAR observations cover a common AOI | **Passed at catalog/footprint level** | Same track/frame 113/A/006/4005/DHDH on Sep 14 and Sep 26; spatial alignment of actual arrays not tested |
| 2. Extract usable NISAR radar values without full download | **Not passed** | HTTP 206 plus correct HDF5 header confirmed; no GCOV measurement dataset extracted |
| 3. Detect meaningful, interpretable NISAR-derived physical change | **Not passed** | No radar-difference image, classifier, calibrated measurement, event proof or uncertainty map |
| 4. Independent reference observations available | **Passed for access/comparison data** | OPERA DSWx-S1 30 m water classes for Sep 15 and 27 downloaded, inspected and compared; **not** yet NISAR validation |

**Current checklist: 2/4 data-feasibility gates.** All four HTTP header/access checks passed; those are a different metric from the four scientific gates.

## Measured OPERA-only result

Area: WGS84 bbox `76.42,9.40,76.49,9.47`. OPERA tile: `T43PFL`. Dates: 2026-09-15 and 2026-09-27. Grid: EPSG:32643; 30 m pixels (900 m²). Masks: only pixels classified on **both dates** as 0 non-water, 1 open water, or 3 inundated vegetation. Classes 1 and 3 were combined into an exploratory water/inundation mask.

- Shared valid area: **59.9067 km²** (66,563 cells)
- Newly water/inundated-vegetation classified: **3.0483 km²** (3,387 cells)
- No longer water/inundated-vegetation classified: **5.1462 km²** (5,718 cells)
- Water/inundated vegetation on both dates: **8.4474 km²** (9,386 cells)
- Non-water on both dates: **43.2648 km²** (48,072 cells)
- Water area (of shared valid pixels): **13.5936 → 11.4957 km²**, net **−2.0979 km²**, approximately **15.4%** lower.

**Interpretation:** This is a change in *OPERA satellite-classified* water/vegetation states, not observed NISAR flood extent, flood damage, ground truth, or proof of a specific storm event. The date mismatch (one day after each NISAR acquisition) and inundated-vegetation class complicate comparison.

## What still needs to be done

1. Test a safe and reproducible extraction of GCOV measurement datasets from both NISAR HDF5 files, preferably a small AOI (without 4-GB full downloads).
2. Check geocoding, polarization, nodata, scale, calibration, comparable incidence/geometry, and quality flags.
3. Calculate raw and dB backscatter changes; avoid equating darker/changed pixels automatically with flooding.
4. Compare candidate masks with OPERA, inspect errors and report confusion matrix/IoU only where justified.
5. Decide whether this location shows enough credible physical change to keep as the main demo; otherwise test Lower Assam.
6. Confirm Space Apps pre-hackathon preparation restrictions with the event organizer.

## Reproducible sources

See `research/kuttanad_2026_09/scene_manifest.json` (exact NASA product IDs/CMR collections), `research/kuttanad_2026_09/opera_comparison.json` (machine-readable OPERA-only metrics), and `docs/REPRODUCTION.md`.

No credentials are included in this repository.
