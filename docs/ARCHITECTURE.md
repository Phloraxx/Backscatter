# Proposed Architecture

## Hackathon architecture

### Frontend
- React
- TypeScript
- MapLibre GL
- Deck.gl only for overlays that benefit from it

### API
- FastAPI
- Pydantic schemas
- endpoints serving case metadata, metrics and artifact URLs

### Processing
- Python
- NumPy
- Xarray
- Rasterio
- GDAL
- scikit-learn only where justified

### Storage
For the hackathon:
- static object/file storage for preprocessed rasters;
- small JSON metadata catalog;
- optional lightweight database for case metadata.

Avoid introducing a heavy distributed geospatial database unless the demo genuinely needs it.

## Suggested repository structure

```text
apps/
  web/
  api/
packages/
  processing/
  schemas/
data/
  catalog/
  samples/
docs/
scripts/
tests/
```

## API concepts

`GET /cases`
Returns curated case studies.

`GET /cases/{id}`
Returns AOI, dates, source granules, available layers.

`GET /cases/{id}/summary`
Returns metrics and interpretation evidence.

`GET /cases/{id}/artifacts`
Returns URLs for before/after/change/mask rasters.

## Processing philosophy

Expensive geospatial processing should happen before the live demo.

The UI must remain fast even if upstream NISAR files are large.

## Scalability story

Future:
- on-demand job queue;
- AOI-based Harmony/subsetting;
- tiled COG access;
- cloud processing;
- cached scene-pair products.

Do not implement this infrastructure before the analysis works.
