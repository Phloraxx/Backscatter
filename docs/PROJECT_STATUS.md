# Backscatter status — updated November 14, 2026

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
