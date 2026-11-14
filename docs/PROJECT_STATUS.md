# Backscatter status — updated November 14, 2026

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

**Not yet complete:** water/flood classification, source-quality calibration beyond positive-power masking, independent OPERA comparison for this Oct/Nov pair, error metrics, interactive app or competition submission. Different agricultural field conditions could explain much of the radar contrast.

## Next science step

Acquire and quality-screen OPERA DSWx-HLS (Oct 29 optical) and DSWx-S1 (Oct 21 / Nov 2 radar) over same area; check temporal mismatch and assess whether a simple backscatter-change rule provides a defensible water-change indicator. Reject simplistic "red = flooded" interpretations and report failures.

## Historical research

The September provisional NISAR and OPERA work remains documented in `research/kuttanad_2026_09/`; the OPERA-only Sep 15/27 net decrease of 2.0979 km² **does not** validate the newer NISAR Oct/Nov pair.

## Security

Earthdata credentials were used solely on the user's Mac; no token, `.rtf` credential file, signed URL or source GeoTIFF is committed. Rotate any credential previously shared in chat.
