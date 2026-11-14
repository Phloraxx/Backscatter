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

## Real Kuttanad validation experiment (November 14, 2026)

**Measured product-to-product comparison; not ground-truth validation.** NASA OPERA DSWx-HLS v1.1 WTR optical classes (0 nonwater, 1 open water, 2 partial surface water, 252/253/254/255 excluded) were compared with NISAR validated GCOV HHHH. Radar 10-metre power was averaged onto optical 30-metre cells *before* converting to dB. Strict binary metrics exclude class 2.

- Oct 29 same-calendar-day open-water ROC-AUC 0.98306; optical class-1 median HHHH −18.0946 dB vs class-0 −5.0692 dB.
- Train a single open-water threshold on **west-half Oct 29** against OPERA labels; east-half spatial holdout F1 **0.9435**.
- Transfer unchanged threshold to Nov 10 radar against Nov 05 OPERA labels: F1 **0.8953**, **5-day date mismatch**.
- Candidate water-gain/loss mask comparison against OPERA Oct 29/Nov 05: F1 **0.2013 gain**, **0.2181 loss**, precision **0.2087/0.1669**. Thus static-water classification is NOT a validated flood-change detector.
- Conditional strict OPERA class transitions are directionally supported by NISAR: new open-water classes (715 cells) exhibit reduced backscatter in 89.51%; lost open-water classes (1,314 cells) exhibit increased backscatter in 89.65%. This does not imply overall mask accuracy.
- Failure modes: changing crops/field water management, partial-water categories, radar speckle, different sensing times, optical clouds/quality masks, and spatially correlated classification labels.

Do not report 0.9435 as "flood detection accuracy". Complete experimental artifacts and source granule IDs are under `research/kuttanad_validated_2026_10_11/`.


## Lower Assam second-case plan

The November 14 metadata preflight confirms two validated NISAR observations and two OPERA Sentinel-1 water references. No raster-level results are yet claimed. Native OPERA 30-metre water labels should be compared to coarsened NISAR **linear power** values converted to dB only after averaging. For OPERA DSWx-S1, class 3 is inundated vegetation (not partial water); exclude it from strict class-0/class-1 open-water evaluation and report it separately. Date offsets are +3 and +1 days, so OPERA is not simultaneous field truth.

NASA ASF flags possible mode-specific calibration residuals around 1 dB before Nov 12, 2026. Check the affected radar mode or RCID before interpreting small median differences as physical change. Source: https://hyp3-docs.asf.alaska.edu/nisar-docs/release-notes/.
