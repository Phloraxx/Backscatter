# Risks and Failure Modes

## Scientific risks

### Speckle
SAR has multiplicative speckle. Filtering may improve readability but can destroy small features.

### Geometry
Incidence angle, terrain and viewing geometry affect backscatter.

### Flooded vegetation
Flooded forests/crops may not appear dark like open water.

### Wind
Wind-roughened water can have higher backscatter.

### Urban areas
Double-bounce effects can complicate urban flood detection.

### Temporal decorrelation
Low coherence is not uniquely caused by flooding.

### Product maturity
Current NISAR datasets may be provisional and have documented quality limitations.

## Engineering risks

- large HDF5 files;
- slow remote access;
- complex CRS;
- tile generation bottlenecks;
- frontend rendering of large rasters.

Mitigation:
preprocess curated AOIs and serve optimized artifacts.

## Product risk

A beautiful viewer with no real analysis will score poorly on scientific value.

## Narrative risk

Do not claim:
"Backscatter predicts floods."

Current project is:
"Backscatter detects and explains surface changes observed between SAR acquisitions."
