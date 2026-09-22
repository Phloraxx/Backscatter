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
