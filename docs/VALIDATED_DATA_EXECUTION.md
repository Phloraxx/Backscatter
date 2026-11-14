## Working method — verified November 14, 2026

The older direct-GDAL method described further below failed on the Mac because GDAL 3.9 NETCDF reading via `/vsicurl` is not supported on macOS. **Use Harmony instead**. NASA Harmony can spatially and variable-subset NISAR GCOV to Cloud-Optimized GeoTIFFs, with no full HDF5 download. <https://nisar-docs.asf.alaska.edu/harmony/>

```bash
python3 -m pip install numpy rasterio matplotlib
python scripts/harmony_validated_kuttanad.py submit
# After NASA Harmony marks the jobs successful:
python scripts/harmony_validated_kuttanad.py fetch
python scripts/analyze_harmony_kuttanad.py
```

The first two commands prompt for a NASA Earthdata token with input hidden. The job submission IDs are stored in `~/Downloads/backscatter-validated-kuttanad/harmony_submission_<date>.json`; no credentials are stored. The fetch command can be rerun to check the job states without submitting duplicates.

**Verified outputs on Mac:** two 10 m HHHH raw GeoTIFFs, two dB-transformed GeoTIFFs, `nisar_delta_hhhh_db.tif`, `nisar_pair_summary.json` and `nisar_hhhh_comparison.png`. The report is **not a flood mask**. Both real Harmony jobs succeeded for this study case.

---

# Validated NISAR GCOV: Kuttanad extraction runbook

As of November 14, 2026. This is the first actual measurement step for Backscatter, not a flood classifier.

## Source

NASA Earthdata/ASF collection `NISAR_L2_GCOV_V1`, CMR collection `C3622241360-ASF`.

Pair:
- Oct 29: `NISAR_L2_PR_GCOV_034_077_D_084_4005_DHDH_A_20261029T132026_20261029T132100_P05036_N_F_J_001`
- Nov 10: `NISAR_L2_PR_GCOV_035_077_D_084_4005_DHDH_A_20261110T132027_20261110T132100_P05036_N_F_J_001`

Variable `/science/LSAR/GCOV/grids/frequencyA/HHHH`. WGS84 AOI `[76.42, 9.40, 76.49, 9.47]`.

## Run on the Mac

Use the prior research environment or install `numpy rasterio matplotlib`.

```bash
# From repository root:
python scripts/extract_validated_kuttanad.py --self-test
python scripts/extract_validated_kuttanad.py --preflight
python scripts/extract_validated_kuttanad.py
```

At the final command, enter a NASA Earthdata token at the hidden prompt. Do not put the token in a command, code, commit, or chat. The script uses authenticated HTTP Range to obtain temporary CDN URLs and instructs GDAL `NETCDF` (<3.13) or `HDF5` (>=3.13) to request only the AOI. The script has only been exercised through preflight and self-test; complete remote I/O remains unverified.

**Expected local output directory**: `~/Downloads/backscatter-validated-kuttanad/`

- `nisar_2026-10-29_hhhh_db.tif`: geocoded dB backscatter
- `nisar_2026-11-10_hhhh_db.tif`: geocoded dB backscatter
- `nisar_delta_hhhh_db.tif`: November 10 minus October 29 radar backscatter (NOT a flood mask)
- `nisar_pair_summary.json`: source IDs, grids, validity and numerical change distribution
- `nisar_hhhh_comparison.png`: preview (if matplotlib available)

Both dates are resampled with **nearest neighbor** onto the same EPSG:32643 30 m grid. Only positive finite power is converted with `10*log10(power)`.

## Scientific and operational cautions

1. Similar relative track/frame and processor version are necessary but do not prove perfect pixel-level comparability or geophysical change.
2. Processing and interpretation must inspect nodata, noise, radar shadow, agricultural water, vegetation and incidence geometry. A simple backscatter delta is **not automatically water**.
3. Inspect the numerical and map results for change quality before selecting a classifier. OPERA optical/radar data are secondary reference candidates with nonidentical acquisition dates; do not invent agreement or accuracy.
4. Large HDF5 files stay on NASA servers. Output GeoTIFFs and results stay local; commit only small verified analyses and provenance with clear labels.
5. If remote GDAL requests fail, consider NASA Harmony's current extraction/spatial-subsetting feature: https://nisar-docs.asf.alaska.edu/harmony/ . Do not disable CDN allowlisting or reveal signed download URLs in troubleshooting logs.

The project remains experimental until actual source pixels, interpretation and independent checks succeed.
