# Context for Code / Science Reviewers

When reviewing Backscatter, focus on:

## Scientific correctness
- Are compared observations compatible?
- Are unit conversions correct?
- Are nodata and invalid values handled?
- Are thresholds learned/calibrated or arbitrary?
- Are claims appropriately cautious?
- Is validation independent?

## Geospatial correctness
- CRS preserved?
- raster transforms correct?
- resampling method appropriate to data type?
- area metrics computed in an appropriate projected/equal-area CRS?
- masks aligned before comparison?

## Architecture
- Can the live demo work without downloading full scenes?
- Are expensive operations cached/preprocessed?
- Are provenance and algorithm versions preserved?

## Product
- Can a judge understand one result in under 60 seconds?
- Is NISAR visibly central?
- Does the UI show evidence rather than just conclusions?

A review should prioritize high-impact correctness bugs over stylistic rewrites.
