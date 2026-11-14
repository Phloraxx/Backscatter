# Backscatter status — updated November 14, 2026


## Event study candidate — Cyclone Arnab (October 28, 2026)

A predeclared Godavari-delta AOI (81.82–81.89 E, 16.58–16.65 N) was selected from IMD's October 28 Cyclone Arnab landfall information, not from water-label performance. Exact sources were verified in NASA CMR:

- NISAR validated GCOV HHHH **2026-10-22 / 2026-11-03**, matching \`149_D_080_4005_DHDH\`, P05036; both true footprint polygons contain all four study corners.
- OPERA DSWx-S1 Sentinel-1D \`T44QPD\` **2026-10-23 / 2026-11-04**, ~11.2025 and 11.2022 hours after NISAR.
- Both NASA Harmony NISAR jobs **submitted, saved locally** under \`~/Downloads/backscatter-arnab-validated/nisar/\`. Authenticated TIFF retrieval and all event raster metrics remain **pending**.
- Scripts \`scripts/preflight_arnab.py\`, \`scripts/harmony_arnab.py\`, \`scripts/fetch_opera_arnab.py\`, and \`scripts/compare_arnab_opera.py\` prepared. The event analysis reuses the unchanged RAW, MEDIAN3 and COHERENT signal filters; no post-hoc retuning.

Do not show a third "analyzed" case or flood map in the web app until source rasters and results exist. [Event study](../research/arnab_event/README.md).

---

## Latest research: fixed-rule spatial filtering

Completed real-data radar-change experiments for both cases: RAW (±3 dB), MEDIAN3 (per-date 3×3 median, then ±3 dB), and COHERENT (median-filtered ±3 dB, 6/9 same-direction pixel support). No OPERA water-class labels were used to generate the displayed candidate pixels.

Kuttanad: RAW → COHERENT fraction of OPERA-classified stable non-water flagged falls from 4.303% to 0.319% (~92.6% reduction), but water-gain recall falls from 0.52028 to 0.40699. MEDIAN3 gain F1 0.44509; COHERENT gain F1 0.42389. 8.1108 km² of coherent radar signal changes are NOT a flood-area estimate.

Assam: COHERENT covers 0.4329 km² of radar signal, but detects zero strictly OPERA-classified new/lost open-water transitions; gain/loss F1 both zero. This method is not a general flood detector.

Web viewer: sixth Kuttanad and fifth Assam layers called SIGNAL CLUSTERS; teal=HH signal decreased, amber=HH signal increased. The original Backscatter logo is unchanged. Desktop and mobile tests pass. Validated same-track multi-date (three or more) baseline cannot yet be built from the available 2026-11-14 data.

[Measured experiment](../research/signal_coherence/README.md) · [Reproducing source](../scripts/evaluate_signal_coherence.py).

---


## Two real geographic studies and original-brand app

- Kuttanad: NISAR validated HH/HV and OPERA optical HLS products analyzed. Existing-water held-out F1 0.944; HH-only gain/loss agreement F1 about 0.20/0.22, not reliable flooding estimates.
- Lower Assam: NISAR validated HHHH Oct 28/Nov 09 and OPERA DSWx-S1 Sentinel-1 Oct 31/Nov 10 are downloaded and measured. 60,640 shared 30 m radar-valid cells, 54.576 square km. Paired median HHHH change +0.1012 dB; this is signal, not established environmental change.
- Assam-specific west-half threshold -17.75 dB gives east-half static-water F1 0.6755; gain/loss masks score F1 0.0353/0.0336. Applying unchanged Kuttanad -10.75 dB gives static F1 0.4275 (all strict first-scene cells) and gain/loss 0/0.
- OPERA S1 and optical HLS class schemes differ; Assam has WTR class 3 inundated vegetation. Satellite-product agreement scores are not directly comparable flood accuracy. Assam reference offsets are +3/+1 days from radar.
- React/MapLibre web app now provides switchable real-measurement maps for both regions. Original Backscatter logo stays in header. Vite production bundles MapLibre v6 worker explicitly; desktop and mobile browser tests pass and evidence panels do not overlap.
- Source satellite TIFFs and Earthdata credential stay local. SHA-256 manifests, actual metric JSON and compact visualization assets are stored in Git.
- No independent field validation, flood extent or impact estimate has been achieved.

Measured Assam report: [scientific write-up](../research/assam_validated_2026_10_11/MEASURED_RESULTS.md). Web app: [instructions](../web/README.md).

---

## New status: Lower Assam second-case discovery (November 14, 2026)

NASA CMR preflight confirmed all four scene identifiers and appropriate source assets. NISAR (Oct 28 / Nov 09) is a matching validated 12-day acquisition pair; OPERA DSWx-S1 (Oct 31 / Nov 10) is available for reference with +3/+1 calendar-day offsets. Pixel extraction, classification, and second-case validation remain pending. The Mac submitted the two Harmony jobs but disconnected before completion could be checked. Check existing local job files before making new submissions.

New scripts: [preflight](../scripts/preflight_assam.py), [Harmony retrieval](../scripts/harmony_assam.py), [OPERA retrieval](../scripts/fetch_opera_assam.py), [comparison](../scripts/compare_assam_opera.py).

The OPERA S1 WTR classes differ from OPERA HLS: class 3 is inundated vegetation; classes 0 and 1 distinguish non-water and open water; 250/251/254/255 are masked/invalid. Calibration uncertainty for some pre-Nov-12 NISAR radar modes can be around 1 dB, and our scene-level affected status is unknown.


## Latest experiment: dual-polarization and actual GCOV mask layers

- **Six additional NASA Harmony subsets succeeded:** HVHV cross-pol, valid-subsample mask, and number-of-looks × both Kuttanad acquisitions.
- **Quality:** 594,958 readable in-footprint 10 m pixels per date, all mask=1 (valid); 3,338 out-of-footprint/no-data pixels. Median looks ≈4.502; an arbitrary ≥4-looks sensitivity filter did not improve change agreement.
- **Same-grid OPERA diagnostic:** HH-only east-half static open-water F1 **0.9435**, optimally weighted HH/HV **0.9533** (0.75 HV weight selected on west-half Oct 29).
- **Change masks get worse:** gain F1 **0.2022 → 0.1053**, loss F1 **0.2185 → 0.0981**. A ±2 dB two-channel sign gate increased gain precision to 0.269 but reduced recall to 0.055.
- **Web application:** fifth layer for HVHV dB change and dual-channel pixel inspector; verified on desktop/mobile. No maps of alleged confirmed inundation are published.

**Conclusion:** dual-pol adds useful radar evidence, not a validated flood-change detector. The OPERA second reference remains five days earlier than the second NISAR scene.

[Full research record](../research/kuttanad_validated_2026_10_11/DUAL_POLARIZATION.md).

---


## Interactive demonstration — implemented November 14, 2026

The `web/` Vite/React/MapLibre app builds and runs with real, small local NISAR/OPERA sample assets (no token in browser). Desktop and 390×844 mobile headless Brave checks pass without JavaScript errors; map layer toggles and pixel inspector were tested with actual dB data. It shows before/after HHHH, unclassified dB change, and OPERA Oct 29 classified water. It is **not a validated water-gain/loss detector** and has not been deployed to a public URL. See `web/README.md` and `scripts/export_demo_assets.py`.

---


## Scientific reference evaluation — November 14, 2026 (latest)

- **Verified data:** validated NISAR Oct 29/Nov 10 HHHH radar rasters; OPERA DSWx-HLS WTR on Oct 29 (Sentinel-2B) and Nov 05 (Sentinel-2A). Both reference rasters contain ~90%+ valid classifications in the AOI. Also downloaded 4 other optical observations; two are entirely invalid in our AOI and excluded.
- **Spatial resolution:** NISAR linear-power averages onto OPERA's native 30-metre grid, THEN converted to dB. No artificial multiplication of 30-metre optical reference cells.
- **Same-calendar-day Oct 29:** NISAR backscatter associated with optical class 1 open water had median **−18.0946 dB**; class 0 non-water **−5.0692 dB**; strict class 0/1 ROC-AUC **0.98306**. Two satellites are not simultaneous.
- **Calibrated threshold:** Oct 29 west-half OPERA training picks **−10.75 dB**; testing east-half against OPERA gives **F1 0.9435** (precision 0.9432, recall 0.9439). This is internal satellite-product agreement, not independent ground truth.
- **Nov 10 vs Nov 05:** fixed-threshold F1 **0.8953** against optical labels **five days older**, not date-matched validation.
- **Change detection fails a naive baseline:** precision **0.2087**, F1 **0.2013** for gain; precision **0.1669**, F1 **0.2181** for loss; evaluated on 30-metre cells valid for both optical dates with 5-day final offset. It would be misleading to call it a good flood map.
- **Evidence despite failure:** in strict optical non-water→open-water transitions (715 cells) NISAR HHHH decreased in **89.51%**; in open-water→non-water (1,314 cells) it increased in **89.65%**. Directional consistency does NOT imply high precision across all cells.
- **Scientific interpretation:** water/land backscatter contrast is strong. Land-cover, vegetation, management and 5-day mismatch can confound change masks. Next: quality filtering, dual-polarization and independent case/date checks. Prioritize honest radar-change explorer as MVP.

Complete report: [independent comparison](research/kuttanad_validated_2026_10_11/INDEPENDENT_COMPARISON.md), [diagnostic metrics](research/kuttanad_validated_2026_10_11/nisar_opera_diagnostic.json), [baseline metrics](research/kuttanad_validated_2026_10_11/change_baseline.json).

---



## What is actually working now

The first **real NISAR measurement workflow** for Kuttanad, Kerala is proven for a small study AOI (WGS84 bbox `76.42,9.40,76.49,9.47`).

1. **NASA CMR:** validated NISAR L2 GCOV V1 scenes Oct 29 and Nov 10 discovered, matching track/frame `077_D_084_4005_DHDH`.
2. **NASA Harmony:** authenticated variable+spatial subset jobs completed for both scenes, outputting HHHH GeoTIFFs.
3. **Local Rasterio:** two real 10 m rasters were downloaded, opened and confirmed on identical EPSG:32643 grids (776×771).
4. **Scientific math:** common positive pixels converted from gamma0 power to dB using `10*log10`. Difference = Nov 10 minus Oct 29 at the same pixel; GeoTIFFs, JSON and preview saved locally.
5. **Provenance:** exact source granules and the numeric research report are recorded in `research/kuttanad_validated_2026_10_11/`.

## Verified measured values

| Quantity | Result |
|---|---:|
| Shared positive pixels | 594,958 |
| Shared valid area | 59.4958 km² |
| Oct 29 median HHHH | -15.1419 dB |
| Nov 10 median HHHH | -13.803 dB |
| Paired median change | +0.6231 dB |
| Pixels with delta below −3 dB | 14.02% |
| Pixels with delta above +3 dB | 24.50% |

**Historical status after first radar extraction (before later tests above):** Independent OPERA product comparisons, quality-layer checks, and the interactive app have since been completed. **Still not complete:** reliable flood-change classification, field validation or competition submission. Different agricultural field conditions could explain much of the radar contrast.

## Next science step (after current experiments)

Test a second independent NISAR interval or a better-aligned reference, including more than one geography. Improve quality analysis and surface-change interpretation without turning HHHH/HVHV threshold transitions into unsupported flood-extent estimates. Keep the 5-day OPERA reference mismatch visible.

## Historical research

The September provisional NISAR and OPERA work remains documented in `research/kuttanad_2026_09/`; the OPERA-only Sep 15/27 net decrease of 2.0979 km² **does not** validate the newer NISAR Oct/Nov pair.

## Security

Earthdata credentials were used solely on the user's Mac; no token, `.rtf` credential file, signed URL or source GeoTIFF is committed. Rotate any credential previously shared in chat.
