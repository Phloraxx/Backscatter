# Backscatter

**NASA Space Apps Challenge 2026 — Dancing with the SARs**

Backscatter is a working project concept for turning NASA–ISRO NISAR Synthetic Aperture Radar observations into understandable evidence of surface change.

## Current direction

The strongest MVP direction is **flood / wetland inundation change detection**, because:
- SAR can observe day/night and through cloud cover.
- NISAR is explicitly designed to measure surface and inundation change.
- The result can be demonstrated visually and validated quantitatively.
- It gives a clean India/NASA–ISRO story without making the product India-only.

The intended product is **not a satellite-image viewer** and **not an AI flood predictor**.

It should be an evidence-driven surface-change system:

`NISAR observation pair → measured radar change → classification → confidence → explanation → map`

## Status

Working concept. Exact geography and event case studies remain deliberately unlocked until scene-level NISAR availability is verified.

Start with:
1. `CONTEXT.md`
2. `AGENTS.md`
3. `docs/PRODUCT_VISION.md`
4. `docs/SCIENCE_AND_SAR.md`
5. `docs/DATA_AND_PIPELINE.md`
6. `docs/VALIDATION_PLAN.md`
7. `docs/JUDGING_STRATEGY.md`

## Working score

Concept potential: **92/100** against the latest published Space Apps-style criteria, assuming strong scientific validation and execution. This is a planning estimate, not an official score.
