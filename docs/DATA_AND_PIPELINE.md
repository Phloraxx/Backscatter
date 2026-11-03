# Data and Processing Pipeline

## Goal

Turn two compatible NISAR observations into a reproducible, inspectable surface-water change product.

## Proposed pipeline

### 1. Discover
Search NISAR observations by:
- AOI;
- date window;
- product type;
- orbit/track/frame where necessary.

### 2. Select compatible pair
Reject pairs with incompatible geometry or product configuration.

### 3. Subset
Crop to AOI early to reduce HDF5/raster processing cost.

### 4. Load measurement layers
Start with GCOV backscatter channels/polarizations available for the selected case.

### 5. Quality mask
Handle:
- nodata;
- invalid pixels;
- layover/shadow if relevant layers exist;
- water/terrain masks only when methodologically justified.

### 6. Transform
For valid positive power values:
`db = 10 * log10(power)`

### 7. Change features
Candidate features:
- dB difference;
- linear-power ratio;
- polarization ratios/differences;
- neighborhood texture/statistics;
- optional GUNW coherence;
- contextual elevation/slope;
- optional precipitation/historical-water context.

### 8. Classification
Begin with an interpretable baseline:
- adaptive thresholding / calibrated rule set;
- logistic regression / random forest if labelled data justify ML.

Do not jump directly to deep learning without adequate training data.

### 9. Morphological cleanup
Remove isolated noise only with documented parameters.

### 10. Vectorize / summarize
Generate:
- newly inundated polygons;
- receded polygons;
- persistent water;
- area metrics.

### 11. Confidence
Confidence should reflect actual evidence:
- classifier probability/calibration;
- agreement across features;
- data quality;
- distance from threshold;
- validation behavior.

### 12. Export
- Cloud Optimized GeoTIFF(s)
- optional PMTiles/vector tiles
- summary JSON
- provenance JSON

## Reproducibility

Every generated artifact should record:
- source granule IDs;
- acquisition timestamps;
- product/version;
- processing parameters;
- git commit;
- algorithm version.


## Verified input and next technical test — 2026-11-03

- NISAR GCOV collection `C2854338529-ASF`: same-track product headers accessed via Earthdata bearer auth for Sep 14 and Sep 26. HTTP 206 valid HDF5; actual calibration arrays, nodata layers and polarization datasets **not extracted**.
- OPERA DSWx-S1 collection `C2949811996-POCLOUD`: WTR tiles for Sep 15 and Sep 27 downloaded and compared over Kuttanad.
- Next: extract a small AOI from each GCOV HDF5, verify rasters align, inspect available polarizations and unit conventions, then produce a **measured** radar delta before interpreting possible inundation. Prefer small subsets/remote GDAL access; never assume a quick-look PNG is adequate scientific evidence.
- Reproducible preparatory scripts: `scripts/verify_earthdata_access.py` and `scripts/compare_opera_dswx.py`; docs in `docs/REPRODUCTION.md`.
