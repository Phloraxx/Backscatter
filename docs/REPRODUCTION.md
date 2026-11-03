# Reproducing the Kuttanad research checks

This is a **research-only** workflow to reproduce data-access tests and OPERA-classification comparisons. It **does not perform NISAR change detection** and does not build the NASA Space Apps application.

## Requirements

- Python 3.10+ (validated with the user's macOS Python environment).
- NASA Earthdata Login account and a valid user token; sign up at https://urs.earthdata.nasa.gov/.
- Network access to NASA CMR, ASF, PO.DAAC and their authenticated storage endpoints.
- Roughly 1 MB disk space for two small downloaded `_B01_WTR.tif` products; larger headroom for Python libraries.

## Install and run

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-research.txt

# 1. Validate protected file access using small byte-range HTTP requests.
python scripts/verify_earthdata_access.py

# 2. Download only the two OPERA WTR TIFFs and compare water classifications.
python scripts/compare_opera_dswx.py
```

Both scripts prompt for the bearer token without echoing it. `verify_earthdata_access.py` optionally reads `EDL_TOKEN` from the environment; avoid using the token in shell history. Never paste an access token into GitHub or a script.

## Expected OPERA output

`~/Downloads/backscatter-opera-check/`

- `OPERA_T43PFL_2026-09-15_WTR.tif`
- `OPERA_T43PFL_2026-09-27_WTR.tif`
- `opera_comparison.json`
- `opera_comparison.png`

The same results from the verified run were copied to `research/kuttanad_2026_09/` (except raw TIFFs).

For the bbox `76.42,9.40,76.49,9.47`, expect **59.9067 km²** shared valid pixels, **3.0483 km²** newly classified water, **5.1462 km²** newly dry, **8.4474 km²** classified water both dates, on EPSG:32643 nominal 30 m pixels.

If provider data are revised, the output might differ; record the actual provider filename, product version, processing date, and any changed result.

## Interpretation and safety

- OPERA codes 1 (open water) and 3 (inundated vegetation) are grouped for this preliminary exercise; they may carry different uncertainties.
- Other classes are invalid/excluded in the simple paired comparison.
- The script checks raster georeferencing alignment and counts shared valid pixels.
- It does not claim flooding occurred or compare NISAR radar pixels.
- Local credentials and downloaded source products must stay out of version control; see `.gitignore`.
- Downloader uses an explicit HTTPS host allowlist for known NASA/PO.DAAC/CDN redirects and strips credentials before CDN redirects. If a provider host changes, inspect it before updating the allowlist—do not disable the check.

## Planned next research milestone

Use ASF GDAL/NISAR documentation to subset GCOV measurements; validate numerical values and metadata first. Reference: https://nisar-docs.asf.alaska.edu/gdal/
