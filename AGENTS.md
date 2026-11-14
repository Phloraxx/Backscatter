# AGENTS.md

> **Current-status precedence (2026-11-14):** This file preserves dated historical checkpoints, some of which say experiments were not yet completed. For current facts, use docs/PROJECT_STATUS.md, research/arnab_event/MEASURED_RESULTS.md and the verified per-case JSON. Earlier TODO/status lines below are **historical** and should not override later measured results.

- **Visibility update as of November 14:** GitHub API reports Phloraxx/Backscatter PUBLIC, though historical notes below refer to the earlier private state. No original-work LICENSE is present; do not assume code reuse is authorized merely because the repo is public.


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


## Verified extraction outcome — 2026-11-14

Both real validated NISAR HHHH GeoTIFFs for Oct 29 and Nov 10 have been extracted through **NASA Harmony** and analyzed. Do not reuse the original `scripts/extract_validated_kuttanad.py` NETCDF-over-/vsicurl flow on macOS GDAL 3.9; it failed. Use `scripts/harmony_validated_kuttanad.py` (submit/fetch) and `scripts/analyze_harmony_kuttanad.py`, or the existing local raster results. Results: 594,958 common 10 m pixels; paired median delta +0.6231 dB. No flood inference or accuracy measurement yet. Read `research/kuttanad_validated_2026_10_11/README.md` and the summary JSON first. Never share/copy the Earthdata secret.

## Latest reference experiment (2026-11-14)

Run `scripts/fetch_opera_hls.py`, `scripts/compare_nisar_opera_hls.py`, `scripts/evaluate_change_baseline.py` on the existing local NISAR files. Scientific note: OPERA-derived static water-vs-land labels show ROC-AUC 0.983 and east-half F1 0.944 with a threshold trained on the west. **Actual gain/loss F1 is only 0.201/0.218** against a date-mismatched OPERA change reference. Never describe this as validated flood detection. A water-extent map is not the same as a water-*change* map. See `research/kuttanad_validated_2026_10_11/INDEPENDENT_COMPARISON.md`.

## Latest dual-polarization evidence — 2026-11-14

Scripts: \`scripts/harmony_extra_layers.py\` obtains GCOV frequency-A HVHV, mask and numberOfLooks for both dates; \`scripts/evaluate_dualpol_quality.py\` reproduces OPERA agreement metrics and ablations; \`scripts/export_demo_assets.py\` prepares five web map layers. Native extra TIFFs remain local; compact JSON and figures are in \`research/kuttanad_validated_2026_10_11/\`.

Measured static open-water held-out F1: HHHH 0.9435 vs weighted HH/HV 0.9533. **Change masks worsened**: gain 0.2022→0.1053; loss 0.2185→0.0981. Subswath mask had no invalid in-coverage pixels. Do not confuse these with field-validation scores or flood extent. The OPERA November reference is 5 days earlier than NISAR. Read \`DUAL_POLARIZATION.md\` before implementing classifier claims.


## Next case: Lower Assam and calibration

The second geography is a catalog-confirmed candidate, NOT an analyzed flood event. Run scripts/preflight_assam.py first. Check existing Mac NASA Harmony job state before using scripts/harmony_assam.py submit; run fetch, scripts/fetch_opera_assam.py, then scripts/compare_assam_opera.py only after authenticated source files exist. Never put the Earthdata token or signed URLs in Git. OPERA S1 WTR codes differ from optical HLS: 0 non-water, 1 open water, 3 inundated vegetation; 250/251/254/255 are masked. The NISAR pre-Nov12 calibration caveat remains unresolved for these exact granules. Keep the recovered Backscatter logo in web/public/brand.


## Actual Lower Assam experiment complete (2026-11-14)

Lower Assam contains real validated NISAR HHHH Oct 28/Nov 09 plus OPERA Sentinel-1 DSWx-S1 Oct 31/Nov 10 source GeoTIFFs and actual measured results. Consult research/assam_validated_2026_10_11/MEASURED_RESULTS.md and assam_nisar_opera_diagnostic.json; the earlier catalog-only status is superseded.

Common paired radar area 54.576 km2; median HH change +0.1012 dB. Assam-specific -17.75 dB classifier: static held-out F1 0.6755; gain/loss F1 0.0353/0.0336. Unmodified Kuttanad -10.75 dB threshold: Assam static F1 0.4275, gains/losses F1 0/0. OPERA S1 class 3 is inundated vegetation, not HLS class 2. Field truth absent; OPERA dates offset +3/+1 days; no flooded-area claims.

The website selects study by query URL (?study=assam or ?study=kuttanad). Assets generated from actual locally downloaded satellite images by scripts/export_assam_demo.py. Assam has no measured NISAR HV: do not generate/present an HV layer there. Use MapLibre v6 explicit worker URL import in web/src/main.jsx to ensure production build map tiles work. Preserve the original team Backscatter logo under web/public/brand.

## Latest coherent HH radar change study (2026-11-14)

Run scripts/export_demo_assets.py and scripts/export_assam_demo.py, then scripts/evaluate_signal_coherence.py to rebuild both coherently filtered NISAR signal overlays AND synchronize web metadata, then scripts/check_web_assets.py.

The filter applies 3 dB threshold to HH radar change, 3×3 per-date median, and 6/9-neighbor spatial coherence. It never uses OPERA WTR classes to create candidate overlays. Kuttanad's coherent radar area 8.1108 km² and Assam's 0.4329 km² are NOT flooded-area estimates. Kuttanad reference gain F1 0.42389 (median3 actually higher 0.44509); Assam gain/loss F1 zero. Preserve the negative result.

Original Backscatter logo remains under web/public/brand. The viewer exposes SIGNAL CLUSTERS in both cases (teal HH decrease, amber HH increase, no flood label). Two matching validated acquisitions per site; no valid mature historical multi-date baseline yet. NASA/JPL notes OPERA HLS and S1 are not sensor-harmonized.


## Cyclone Arnab preflight and new public demo (2026-11-14)

- **Predeclared** AOI 81.82..81.89 E, 16.58..16.65 N near the Oct28 cyclone landfall, not performance-selected. NASA CMR: NISAR GCOV Oct22 / Nov03 and OPERA DSWx-S1 (Sentinel-1D) Oct23 / Nov04, each OPERA ~11.2h after NISAR. The NISAR \`149_D_080_4005_DHDH\` polygons contain the whole AOI. Read \`research/arnab_event/README.md\` and \`scene_manifest.json\`.
- Two local NASA Harmony jobs were **already submitted**; saved IDs in \`~/Downloads/backscatter-arnab-validated/nisar/job_*.json\`. **Do not submit again**; check/fetch saved jobs and obtain OPERA WTR with token at hidden prompt. No token is saved to Git.
- \`scripts/compare_arnab_opera.py\` includes predeclared unchanged signal-coherence methods from \`scripts/evaluate_signal_coherence.py\`, plus exploratory reference diagnostics. It has **not yet been run on Arnab pixels**. No claim of detected flooding or validation until actual outputs exist.
- Cloudflare Pages project \`backscatter-afterimage-2026\` was created, linked to private \`Phloraxx/Backscatter\` main with build root \`web\`; **confirm successful production deployment before claiming public URL**.
- NASA Space Apps 2026 closes November 15 23:59 event-local. Official GO Team notes challenge-specific work performed before Nov14 09:00 may jeopardize eligibility; project has earlier commits. Do not falsify the work chronology. See \`docs/SPACE_APPS_SUBMISSION.md\`.


## Completed cyclone Arnab event-linked test (2026-11-14)

- Original AOI 81.82..81.89 E / 16.58..16.65 N remains unchanged; validated NISAR HHHH Oct22/Nov03 is downloaded, plus OPERA DSWx-S1 Sentinel-1D Oct23/Nov04. Actual OPERA reference tile is **T44QND**, NOT the neighboring T44QPD returned by the broad CMR query. First tile failed true raster-grid overlap; switched by georeferencing, *not scores*.
- Correct OPERA source IDs G4386072108-POCLOUD and G4405822843-POCLOUD, approximately 11.2031/11.2025 hours after paired NISAR. Original scene IDs, checksum manifest and actual source data lineage in research/arnab_event/.
- Shared valid NISAR grid: 64,495 30 m cells (58.0455 km²); strict OPERA reference 0/1 both dates: 58,085. OPERA 0→1: 842 cells; 1→0: 75 cells.
- **Unchanged radar signal coherence filter F1 0/0 for both gain/loss.** It highlights 4.4163 km² of HH radar change, **not flood extent**. A separately fitted static-water threshold -14.5 dB scores east-half F1 0.8987, but does not detect changes reliably (gain/loss F1 .1347/.0122). These are satellite product agreements, not field accuracy.
- Source report research/arnab_event/MEASURED_RESULTS.md and metric JSON. Public static research page /research.html is generated by scripts/export_public_research.py, with non-sensitive source metadata only; do not publish Earthdata secrets or large raw GeoTIFFs.
- The interactive map retains two stable studies (Kuttanad and Assam); Arnab is third **research-only** case, not a claimed operational flood map.
