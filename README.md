# Backscatter

## Public 7-slide NASA Space Apps demonstration

**Public demo:** [View the seven-slide PDF](https://backscatter-afterimage-2026.pages.dev/backscatter-demo.pdf) · [Live interactive map](https://backscatter-afterimage-2026.pages.dev/)

The demo shows real NISAR data, the original team logo, two finished study areas, a conservative signal overlay, and both the improvement and failure cases. It does **not** claim field-validated flood detection.



## Third measured case — Cyclone Arnab (October 28, 2026)

We tested the same unchanged radar signal-clustering rule near the documented October 28 cyclone landfall in the Godavari delta, Andhra Pradesh. Actual validated NISAR GCOV HHHH observations **October 22 / November 3** were compared against OPERA Sentinel-1D DSWx-S1 water classifications **October 23 / November 4**, only **~11.2 hours** after each NISAR acquisition.

The original AOI remained unchanged; a neighboring OPERA tile initially returned by the catalog did not overlap in raster coordinates. We corrected the reference tile to **T44QND** based on real georeferencing, **not classification results**.

- **58.0455 km²** of common radar-valid area and **58,085** strict 0/1 reference cells.
- OPERA reference classes changed non-water → open-water in **842 cells** and the reverse in **75 cells**. These are product-class transitions, **not confirmed flood area**.
- The fixed 3 dB / 3×3 median / six-neighbor coherent method scored **F1 0.0000** for both reference water gain and loss. A locally fitted *static*-water threshold reached held-out F1 **0.8987** but still failed to track water changes reliably.

The additional event test **strengthens the negative conclusion**: even closer-timed independent satellite classifications do not make simple HH change rules reliable flood detectors. This third case is available as documented research, not as a fabricated flood overlay.

[Public research and evidence page](https://backscatter-afterimage-2026.pages.dev/research.html) · [Full measured case study](research/arnab_event/MEASURED_RESULTS.md) · [Actual confusion matrices](research/arnab_event/arnab_nisar_opera_diagnostic.json) · [Source checksums](research/arnab_event/source_checksums.json) · [Submission preparation](docs/SPACE_APPS_SUBMISSION.md).

---

## Latest science: coherent radar signal regions (November 14, 2026)

Backscatter now provides a SIGNAL CLUSTERS overlay for both Kuttanad and Lower Assam, displaying actual HH radar-signal changes—not flood extents. This reproducible no-training filter requires a 3 dB change, spatial 3×3 median filtering, and 6/9 neighboring pixels supporting the same change direction.

- Kuttanad: 8.1108 km² of coherent **radar signal** (not water area). OPERA-classified stable non-water falsely highlighted: 4.303% with raw threshold versus 0.319% with spatial coherence (~92.6% reduction). OPERA gain F1: 0.42389 with coherence; simple median filtering scored 0.44509.
- Assam: 0.4329 km² of coherent radar signal, but **zero strict OPERA open-water gains or losses detected**. Spatial filtering does not generalize as a reliable flood detector.
- Each study's selected repeat track has only two validated acquisitions as of November 14. Mixing older provisional products would require careful calibration checks.

![Kuttanad — coherent radar-signal changes, not flooding](web/preview-signal-kuttanad.jpg)

[Lower Assam signal-change preview](web/preview-signal-assam.jpg) · [Scientific protocol and limitations](research/signal_coherence/README.md) · [Kerala metrics](research/signal_coherence/kuttanad_metrics.json) · [Assam metrics](research/signal_coherence/assam_metrics.json) · [Working web viewer](web/README.md).

---


**NISAR radar backscatter evidence for water mapping in Kuttanad, Kerala, and Lower Assam, India.** A NASA Space Apps Challenge 2026 project (Team Afterimage) asking a narrow question: what can L-band SAR tell you about water on the ground, and where does it fail?

The answer so far: NISAR separates existing water from non-water in some scenes, but simple radar-only change detection is unreliable, and the threshold learned in Kuttanad fails to transfer to Assam. Every number is linked to a real satellite source and its particular reference product.

- **Static water, same-day reference** — ROC-AUC **0.983** against OPERA DSWx-HLS open-water labels; a threshold calibrated on the west half scored F1 **0.944** on the spatially separated east half.
- **Change detection** — agreement with OPERA for new and lost water was F1 **0.201 / 0.218**. The classifier is not a flood map, and the app does not present it as one.
- **What ships** — an interactive MapLibre evidence viewer over real NISAR HHHH and HVHV subsets, a pixel inspector, and the evaluation scripts behind every number above.
- **Independent Assam case** — fitted static-water F1 0.676 on the east-half holdout, gain/loss F1 0.035/0.034. The unchanged Kerala cutoff scores static F1 0.428, gain/loss F1 0/0 on the Assam Sentinel-1 reference. Different reference methods mean these are not directly comparable field-accuracy scores.

![Backscatter evidence viewer](web/preview.jpg)

The original Backscatter logo appears in both views. Kuttanad and Assam can be selected in the local web application.

![Measured Lower Assam study in the evidence viewer](web/preview-assam.jpg)

[Run the viewer](web/README.md) · [Scientific evaluation and failure analysis](research/kuttanad_validated_2026_10_11/INDEPENDENT_COMPARISON.md) · [Metrics JSON](research/kuttanad_validated_2026_10_11/change_baseline.json)

> An evidence viewer, not a flood detector. Every claim is scoped to the acquisition dates and the OPERA reference it was compared against.

## Log

Newest first. Each entry is a dated record of what was measured.

### Second study measured: Lower Assam (November 14, 2026)

Validated NISAR HHHH from October 28 and November 9 and OPERA Sentinel-1 DSWx-S1 WTR from October 31 and November 10 have been downloaded and analyzed. The reference dates lag the NISAR observations by +3/+1 days.

Measured common radar area is **54.576 km2**, with paired median NISAR signal difference **+0.1012 dB**. A new Assam-specific water threshold achieves held-out static F1 **0.6755**, but gain/loss F1 is only **0.0353/0.0336**; an unchanged Kerala cutoff is worse. These are satellite-product agreements, not field-confirmed floods.

[Full results and failure analysis](research/assam_validated_2026_10_11/MEASURED_RESULTS.md) · [Actual metrics JSON](research/assam_validated_2026_10_11/assam_nisar_opera_diagnostic.json) · [Source checksums](research/assam_validated_2026_10_11/source_checksums.json).

**Calibration caveat:** [ASF's validated NISAR release notes](https://hyp3-docs.asf.alaska.edu/nisar-docs/release-notes/) warn of approximately 1 dB residuals in about 30% of observations in certain pre-November-12 radar modes. Whether our individual granules are affected is not established. Kuttanad's +0.6231 dB median paired signal difference is a measurement, not proof of environmental change.


**Team identity:** The web app now uses our original Backscatter logo (globe, radar beam, returning echoes and wordmark), preserved unchanged in [web/public/brand/backscatter-original.png](web/public/brand/backscatter-original.png). The logo mark also powers the site header and favicon.


### Dual-polarization study and evidence viewer — November 14, 2026

The web app now has an **HVHV cross-polarization change layer** and HH/HV pixel inspector, based on actual NISAR subsets for October 29 and November 10.

Adding HV improved held-out **existing open-water** agreement with OPERA (F1 **0.9435 → 0.9533**) but **worsened** gain/loss masks (F1 **0.2022/0.2185 → 0.1053/0.0981**). We preserve both the useful evidence and the failure cases. The validity mask marks every readable in-footprint pixel as valid; it did not remove false positives.

![Dual-polarization layer in the web map](web/preview-dualpol.jpg)

[Experiment details](research/kuttanad_validated_2026_10_11/DUAL_POLARIZATION.md) · [Experimental metrics](research/kuttanad_validated_2026_10_11/dualpol_quality_evaluation.json) · [Runnable app](web/README.md).


### Interactive evidence map — 14 November 2026

**The first working Backscatter web demo now exists.** Built in React + MapLibre, it displays real validated NISAR HHHH before/after imagery, a measured radar-difference overlay, and the independently classified OPERA October 29 water layer over Kuttanad. Click map cells to inspect actual before/after dB values and the OPERA class. Works on desktop and mobile.

![Working Backscatter interactive map](web/preview.jpg)

Run locally (no token needed for the prepared curated dataset):

```bash
cd web
npm install
npm run dev
```

The website is an **evidence viewer, not a flood detector**. The current simple gain/loss classifier has poor OPERA agreement (F1 about 0.20/0.22), and the map deliberately does not display those experimental masks as confirmed flooding. [App instructions](web/README.md) · [Science and limitations](research/kuttanad_validated_2026_10_11/INDEPENDENT_COMPARISON.md).


### November 14: Independent water-reference experiment

**Current verified position: NISAR water/land discrimination works on this limited example; robust gain/loss detection does not.**

- Same-calendar-day Oct 29 NISAR HHHH versus clear OPERA DSWx-HLS (Sentinel-2B) open-water/non-water labels: **ROC-AUC 0.983** (descriptive, not ground truth).
- A single dB cutoff calibrated on the west half of Oct 29 (-10.75 dB) gave **F1 0.944** on east-half, spatially separated OPERA labels.
- On Nov 10 radar against **Nov 05 optical observations**, static-water F1 was **0.895**; the **five-day mismatch** limits inference.
- Using the same threshold to derive change masks, agreement with OPERA Oct 29 → Nov 05 was only **gain F1 0.201**, **loss F1 0.218**. **Do not call this accurate flood mapping.**
- Pixels that OPERA classifies as new open water show negative NISAR changes in **89.5%** of cases; open-water-loss pixels show positive NISAR changes in **89.6%**. These are conditional directional associations, not a reliable NISAR-only change mask.

![OPERA and NISAR change-map diagnostic; not same-date validation](research/kuttanad_validated_2026_10_11/change_baseline_preview.jpg)

[Scientific evaluation and failure analysis](research/kuttanad_validated_2026_10_11/INDEPENDENT_COMPARISON.md) · [Metrics JSON](research/kuttanad_validated_2026_10_11/change_baseline.json) · [Reproducible code](scripts/evaluate_change_baseline.py).

The MVP should show observed radar change **and** provenance/uncertainty, not claim every radar change represents flooding.


### Verified breakthrough — November 14, 2026

**Actual validated NISAR radar pixels have now been extracted for Kuttanad, Kerala.** NASA Harmony produced HHHH GeoTIFFs for **2026-10-29 and 2026-11-10**. Both rasters share an identical EPSG:32643 grid at **10 m resolution** (776 × 771 pixels).

Our first unclassified paired backscatter comparison covers **594,958** shared valid radar pixels (**59.4958 km²**), with a **+0.6231 dB median pixel-wise change**. These numbers show measured radar response, **not** water extent or flood detection.

![Real NISAR before-and-after and measured HHHH change](research/kuttanad_validated_2026_10_11/nisar_hhhh_comparison_preview.jpg)

[Verified research report](research/kuttanad_validated_2026_10_11/README.md) · [Scientific metrics](research/kuttanad_validated_2026_10_11/nisar_pair_summary.json) · [Reproducible Harmony retrieval](scripts/harmony_validated_kuttanad.py) · [Comparison script](scripts/analyze_harmony_kuttanad.py).


**Team Afterimage · NASA Space Apps Challenge 2026 · Dancing with the SARs**

> **See the evidence of Earth's changing waters.**

Backscatter is a proposed interactive, evidence-driven application for investigating changes in floodplain and wetland water coverage using repeat **NASA–ISRO NISAR SAR measurements**. Planned outcome: change maps, measurements, uncertainty, and explanation grounded in observable radar evidence.

**Current phase: verified scene inventory and an initial NISAR extraction implementation. No NISAR-derived inundation mask, validation score, live dashboard, or working flood predictor exists yet.**

### November 14, 2026 — validated GCOV study pair (current priority)

The November 6 validated NISAR release includes Kuttanad observations **2026-10-29** and **2026-11-10**, matching track/frame `077_D_084_4005_DHDH` and processor `P05036`. These replace the *September provisional pair as our primary candidate*; the earlier OPERA-only September analysis remains useful preliminary research, not a NISAR validation result.

- **Verified today:** NASA CMR collection `C3622241360-ASF` returns both exact granules; the Mac preflight and synthetic numerical tests passed.
- **Not yet verified:** authenticated retrieval of actual radar arrays from the *new* validated files; aligned HHHH measurements; water classification; accuracy.
- **New tool:** `scripts/extract_validated_kuttanad.py` discovers the granules, prompts locally for an Earthdata token, reads only an AOI, produces aligned 30 m HHHH backscatter GeoTIFFs plus an **unclassified** dB-difference raster and JSON. Its remote GDAL read remains untested until run with credentials.
- **Follow-up validation candidates:** OPERA DSWx-HLS optical products including 2026-10-29; OPERA DSWx-S1 2026-10-21/11-02. These are **not date-matched reference pairs** for 10/29 and 11/10.

See [validated data execution](docs/VALIDATED_DATA_EXECUTION.md) and [new scene manifest](research/kuttanad_validated_2026_10_11/scene_manifest.json).

### Earlier research — 2026-11-03

- **Kuttanad, Kerala** is the primary candidate, with a small study box at `[76.42, 9.40, 76.49, 9.47]` (longitude/latitude, WGS84).
- Two repeat NISAR **L2 provisional GCOV** products were located (2026-09-14 and 2026-09-26); a local Mac test received HTTP **206** and valid HDF5 file signatures for both.
- Two **OPERA DSWx-S1** surface-water products (2026-09-15 and 2026-09-27) were downloaded, inspected, and compared on their common 30 m grid. These are **independent Sentinel-1 observations**, not NISAR results or definitive ground truth.
- Across **59.9067 km²** of valid compared pixels: **3.0483 km² new water/inundated-vegetation classification**, **5.1462 km² loss**, **8.4474 km² classified water on both dates**; net classified-water change **-2.0979 km²**.
- **Still unverified:** extracting actual NISAR measurement arrays; their scientifically meaningful change; agreement with reference observations; classification accuracy.

![OPERA-only Kuttanad comparison (not NISAR)](research/kuttanad_2026_09/opera_comparison.png)

See [research record](research/kuttanad_2026_09/README.md), [project status](docs/PROJECT_STATUS.md), and [data manifest](research/kuttanad_2026_09/scene_manifest.json).

## Reproduce the preparatory data checks

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-research.txt
python scripts/verify_earthdata_access.py
python scripts/compare_opera_dswx.py
```

A free NASA Earthdata account/token is required; scripts request a token interactively and **never store it**. Downloaded source TIFFs are placed outside the repository in `~/Downloads/backscatter-opera-check/`. Full instructions: [docs/REPRODUCTION.md](docs/REPRODUCTION.md).

## MVP scope

The original scope, kept for reference. Steps 1, 2 and 5 are implemented in the web viewer. Step 3 exists but does not meet an acceptable standard for change detection. Step 4 is implemented for the two acquisition dates only.

1. Select a compatible NISAR radar pair.
2. Extract and quality-check matching radar measurements; calculate change features.
3. Classify probable water-extent change with explicit uncertainty.
4. Compare with independent observations and report documented limitations.
5. Show evidence and provenance through an interactive map.

Avoid representing OPERA-derived changes as NISAR detections, or seasonal water changes as confirmed flood damage. No disaster prediction, landslide detection, or unverified AI claims in the MVP.

**Repository index:** [Master context](CONTEXT.md) · [Architecture](docs/ARCHITECTURE.md) · [Scientific plan](docs/DATA_AND_PIPELINE.md) · [Validation](docs/VALIDATION_PLAN.md) · [Hackathon plan](docs/HACKATHON_EXECUTION.md) · [Research status](docs/PROJECT_STATUS.md).

**Security:** Do not commit Earthdata access tokens, `.netrc`, credentials, signed links, or raw multi-GB satellite downloads. Check NASA Space Apps pre-event development rules before using this research preparation as part of a final submission.
