# AGENTS.md

This file is the operating contract for AI coding/research agents working on Backscatter.

## Read first

Before making architecture or product decisions, read:
- `CONTEXT.md`
- `docs/PRODUCT_VISION.md`
- `docs/SCIENCE_AND_SAR.md`
- `docs/DATA_AND_PIPELINE.md`
- `docs/VALIDATION_PLAN.md`
- `docs/DECISIONS.md`

## Non-negotiable rules

1. **NISAR must remain central.** Do not solve the project primarily with another dataset and use NISAR decoratively.
2. **Never equate radar change with flood automatically.** Classification must be evidence-based and uncertainty-aware.
3. **No unsupported disaster prediction claims.**
4. **LLMs may explain measured results, but must not generate the scientific result.**
5. **Do not silently mix incompatible product generations or processing levels.**
6. **Never fabricate evaluation metrics.** Metrics must come from an explicit validation set.
7. **Prefer one excellent use case over a weak "detect everything" platform.**
8. **Preserve data provenance**: source, product, acquisition times, track/frame if applicable, polarization, processing version.
9. **Design for a 48-hour hackathon demo first**, scalable architecture second.
10. **Do not over-engineer.** Preprocess a small number of excellent cases before promising global real-time processing.

## Working MVP

Given two compatible NISAR observations of an area:
- derive a backscatter-change representation;
- classify persistent water / newly inundated / receded water where defensible;
- quantify changed area;
- show confidence and evidence;
- visualize before/after and change layers;
- validate against an independent reference.

## Agent behavior

When uncertain:
- document the uncertainty;
- prefer official NASA/ASF/ISRO documentation;
- add a TODO rather than inventing a scientific rule.

When proposing a model:
- give the physical rationale;
- list required inputs;
- state assumptions;
- state failure modes;
- define how it will be validated.

## Code quality

Prefer:
- small modules;
- explicit schemas;
- deterministic processing;
- cached artifacts;
- testable geospatial functions;
- config-driven case studies.

Avoid:
- giant notebooks as production logic;
- hidden preprocessing steps;
- hard-coded geographic constants in core algorithms;
- unnecessary microservices.


## Verified data status (2026-11-03)

Review `docs/PROJECT_STATUS.md`, `research/kuttanad_2026_09/README.md`, and `research/kuttanad_2026_09/scene_manifest.json` before implementing. The four source products are real and accessible: NISAR Sep 14/26 HDF5 headers and OPERA Sep 15/27 WTR GeoTIFFs. **OPERA statistics are not NISAR results**; no NISAR pixels, classification or accuracy have yet been produced. Keep all credentials out of code and Git. Treat pre-hackathon scripts as research, and check event restrictions before developing a submission.

## Current implementation context — 2026-11-14

- Prioritize validated NISAR GCOV V1 `C3622241360-ASF`, Kuttanad 2026-10-29 and 2026-11-10, with matching `_077_D_084_4005_DHDH_`, processor `P05036`.
- New extraction entry point: `scripts/extract_validated_kuttanad.py`; it was tested in `--self-test` and `--preflight` modes. **Full authenticated remote extraction was NOT run**. Next run: use the user's private local token through getpass, never via version-controlled text, CLI flags, chat, logs or remote connector commands.
- Output should be actual HHHH backscatter (dB) and a difference raster. Do **not** label it water/flood without a separate physically defensible classifier and checks against independent observations.
- October 29 DSWx-HLS and nearby OPERA DSWx-S1 are reference *candidates*, with cloud/quality/temporal limitations. Earlier September OPERA estimates belong only to the earlier reference experiment.
- Relevant docs: `docs/VALIDATED_DATA_EXECUTION.md`, `research/kuttanad_validated_2026_10_11/README.md`, and `docs/PROJECT_STATUS.md`.
