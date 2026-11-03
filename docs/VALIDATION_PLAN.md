# Validation Plan

Scientific validation is a major competitive differentiator.

## Objective

Measure whether the inferred inundation/change mask matches an independent reference.

## Possible references

Depending on case-study availability:
- cloud-free optical water classification on a close date;
- authoritative flood extent data;
- high-quality open water datasets;
- manually labelled reference samples;
- event-specific government/scientific products.

Reference data must not simply repeat the same NISAR-derived algorithm.

## Metrics

For binary inundation classification:
- precision;
- recall;
- F1;
- IoU / Jaccard;
- confusion matrix.

For changed area:
- absolute area error;
- relative area error.

## Spatial split

Avoid evaluating only on the exact pixels/regions used to tune thresholds.

Prefer:
- tune on one subregion / event;
- validate on another;
or
- spatial holdout blocks.

## Required reporting

Never report a single accuracy number without:
- reference source;
- date mismatch;
- AOI;
- sample definition;
- threshold/model version;
- known limitations.

## Failure analysis

Explicitly inspect:
- rough water;
- urban areas;
- flooded vegetation;
- steep terrain;
- radar shadow;
- agricultural fields;
- seasonal vegetation changes.

The demo should include at least one acknowledged failure mode. That increases credibility.


## Available reference candidate — 2026-11-03

OPERA DSWx-S1 WTR tiles `T43PFL` for 2026-09-15 and 2026-09-27 have been acquired and compared. They are processed Sentinel-1 classifications (not ground truth). NISAR scenes are 2026-09-14 and 2026-09-26, introducing a one-day offset per comparison. For binary exploratory water masks, OPERA codes 1 (open water) and 3 (inundated vegetation) were grouped; keep per-class results when possible. The net observed OPERA-only classified-water change is −2.0979 km² on 59.9067 km² common valid area.

**No NISAR validation metric is yet available.** Future metrics must refer to NISAR-derived candidate classifications and not be calculated from OPERA compared against itself. Include grid alignment, invalid masks, reference limitations and temporal mismatch. See `docs/PROJECT_STATUS.md`.
