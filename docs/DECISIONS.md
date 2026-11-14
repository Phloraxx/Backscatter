# Decision Log

## D-001 — Challenge
**Decision:** NASA Space Apps 2026, Dancing with the SARs.

## D-002 — Repository / working product name
**Decision:** Backscatter.

Reason: backscatter is the actual radar measurement concept central to SAR and gives the project a clean technical identity.

## D-003 — Initial vertical
**Decision:** prioritize flood/wetland inundation change.

Reason: strongest combination of scientific fit, social impact, demo quality and 48-hour feasibility.

## D-004 — Primary product family
**Decision:** evaluate GCOV first.

Reason: geocoded, calibrated, terrain-corrected backscatter is a practical basis for a hackathon surface-change pipeline.

## D-005 — AI role
**Decision:** AI may explain results but should not be the scientific measurement engine.

## D-006 — Geography
**Decision:** not locked.

Kerala/Western Ghats is the first candidate, subject to real scene availability and validation quality.

## D-007 — Deployment philosophy
**Decision:** curated preprocessed case studies for MVP, on-demand global processing as roadmap.

## Open decisions

- exact event/region;
- polarization feature set;
- baseline classifier;
- validation reference;
- whether GUNW coherence improves the primary case;
- final tagline and visual identity.


## Update — 2026-11-03

### D-008 — Primary research case
**Decision:** Kuttanad, Kerala, WGS84 bbox `76.42,9.40,76.49,9.47`, with NISAR Sep 14/26 and OPERA Sep 15/27 as candidate observations. Lower Assam is backup. Supersedes the open geography preference in D-006 **for research prioritization only**; final event case is conditional on validated NISAR science.

### D-009 — Evidence boundary
**Decision:** OPERA-only reported change (net −2.0979 km² classified water) cannot be described as NISAR flood detection. Both NISAR sources currently have only authenticated-file-header checks.

### D-010 — Data and secret hygiene
**Decision:** keep token, signed redirect links, HDF5/GeoTIFF source products and local `.netrc` outside Git. Commit small research scripts, manifests, metrics and the OPERA-only figure.

## D-011 — Use validated GCOV for the current scientific demo (2026-11-14)

Prefer **2026-10-29 and 2026-11-10** Kuttanad validated `NISAR_L2_GCOV_V1` observations over provisional September observations. Both have identical track, frame, acquisition mode and processing version identifiers. Maintain the September work as background research and Assam as fallback. The new pair has not yet produced real measurement arrays or flood classification.

## D-012 — No false validation claim

OPERA DSWx-HLS near Oct 29 and DSWx-S1 near Nov 2 are **candidate independent comparison inputs**, not an exact-date Nov 10 reference; do not report numerical model accuracy until proper temporal-quality checks.


## D-013 — Use NASA Harmony to extract validated NISAR GCOV pixels (2026-11-14)

Direct NETCDF-over-/vsicurl GDAL 3.9 raster reading failed on macOS. NASA Harmony variable+spatial subsetting completed for both dates, producing two measured 10 m HHHH GeoTIFFs. Retain full HDF5 source files remotely and run numerical analysis on small downloaded subregions. `scripts/harmony_validated_kuttanad.py` supersedes the experimental direct-GDAL path for this environment.

## D-014 — Measured radar changes do not establish flooding

Record actual paired NISAR HHHH differences (median +0.6231 dB, 594,958 common valid pixels), but do not label any proportion of positive/negative dB change as flood extent until independently checked.

## D-015 — Preserve evidence and failure modes (2026-11-14)

Our first independent product-to-product comparison is informative but mixed. Static water/nonwater NISAR HHHH discrimination is strong on Oct 29; candidate gained/lost water masks show low precision when compared against OPERA with an offset second date. Prioritize an explainable *radar surface-change* product with clearly separated observed measurements vs uncertain interpretations. Do not publish a flood-extent accuracy claim.

## D-016 — Reference quality and temporal validity

Use OPERA DSWx-HLS class 0/1 for strict binary assessment; treat class 2 (partial water) separately, and mask invalid 252/253/254/255. Exclude zero-coverage scenes (Oct 29 S2A, Nov 01 S2B) rather than considering them water-free. Use native 30 m reference cells, not upscaled 10 m pseudo-samples. Identify same-calendar-day vs 5-day-offset comparisons explicitly.


## D-017 — Dual-polarization evidence, not a flood classifier (2026-11-14)

Both validated NISAR scenes now include extracted GCOV frequency-A HVHV, subswath mask and number-of-looks rasters. A weighted HH+HV score improves same-day held-out static open-water F1 from 0.9435 to 0.9533, **but worsens** gain/loss F1 from 0.2022/0.2185 to 0.1053/0.0981 against temporally offset OPERA reference. The mask marks all in-footprint pixels as valid, and a looks threshold did not fix the change problem. Add HVHV **measured radar change** as an evidence layer, but do not promote dual-pol masks as confirmed water gain/loss. Keep the HH change layer primary.


## D-018 — Geographic generalization check

Investigate Lower Assam validated NISAR GCOV Oct 28 / Nov 09 using OPERA Sentinel-1 DSWx-S1 Oct 31 / Nov 10 as a second case. Metadata and source links pass preflight; actual sensor pixels and validation do not yet exist. Never describe this candidate as completed flood detection.

## D-019 — Explicit pre-Nov-12 calibration caution

ASF identifies approximately 1 dB radiometric residuals in some pre-Nov-12 NISAR acquisition modes. The affected status of the selected Kuttanad/Assam granules is not confirmed; a small difference in measured dB may therefore not be physically meaningful on its own.


## D-020 — No single universal darkness threshold (2026-11-14)

The Kerala-trained -10.75 dB rule transfers poorly to Lower Assam: static water F1 0.4275 and water gain/loss F1 0/0 against the OPERA S1 satellite classification. An Assam-fitted -17.75 dB cutoff also has weak change F1 0.0353/0.0336. This is not a controlled cross-region model benchmark because Kerala used HLS and Assam used S1 labels with different temporal offsets. Do not publish physical flood extent based on either threshold.

## D-021 — Real dual-study interface without unmeasured polarizations

A lightweight case selector allows Kuttanad/Assam comparisons, preserving each geographic grid and OPERA class meaning. HV layers are visible only in Kuttanad, because only that case has HVHV measurements; the Assam binary HV slots are NaN and hidden. Explicitly bundle MapLibre v6 worker with Vite worker&url before creating maps so that production tiles and overlays render.

## D-022 — Signal evidence, not flood detection (2026-11-14)

Keep a clearly labeled SIGNAL CLUSTERS visualization of strong HH radar changes with an untuned 3 dB, 3×3 median, 6/9 neighbor spatial rule. It reduces Kuttanad's reference-stable non-water false highlighting (4.303% → 0.319%) but misses all strict OPERA water transitions in Assam. Teal and amber denote radar-signal decrease/increase, never flooded water.

## D-023 — Do not fabricate a multi-date historical baseline

As of November 14, 2026, the selected matched validated NISAR repeat tracks have only two acquisitions each. Older provisional imagery has different product maturity and may carry processing differences. Do not mix it uncritically or claim a validated 3+ date time series.

## D-024 — Different OPERA products are not a common ground truth

NASA JPL explicitly states that DSWx-HLS optical and DSWx-S1 radar products are not harmonized across sensors. OPERA references have different date offsets and class definitions. Our scores measure product agreement, not verified flood accuracy.


## D-025 — Require raster-grid overlap, not just catalog intersection (2026-11-14)

The Cyclone Arnab CMR query returned OPERA tiles T44QPD and T44QND on the same reference dates. Initially T44QPD was selected but its **actual 30 m UTM grid did not overlap** the 10 m NISAR subset (0 strict reference cells). Switch to **T44QND**, which contains the original AOI in projected coordinates. No geographic AOI or NISAR dates were changed. The source correction was based on georeferencing, not detection performance. All future preflights should inspect real raster bounds before comparing pixels.

## D-026 — Treat cyclone event test as independent negative evidence

Validated NISAR Oct22/Nov03 and OPERA Sentinel-1D Oct23/Nov04 provide ~11.2-hour reference offsets around documented Oct28 Cyclone Arnab. However the **unchanged coherent HH rule has F1=0.0 for OPERA new/open-water loss transitions** (842/75 strict reference transitions). Do not present coherent radar change as cyclone flooding. A locally fitted static-water threshold F1=.8987 does not establish water-change reliability. Publish the scientific negative result and retain the stable two-study public viewer.
