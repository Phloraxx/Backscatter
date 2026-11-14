# Backscatter status — updated November 14, 2026

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
