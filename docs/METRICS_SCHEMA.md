# Metrics and Provenance Schema

Each case-study result should be serializable into a small stable JSON object.

Suggested fields:

```json
{
  "case_id": "string",
  "aoi": {},
  "observation_a": {
    "granule_id": "string",
    "acquired_at": "ISO-8601",
    "product": "GCOV",
    "polarizations": []
  },
  "observation_b": {},
  "algorithm": {
    "name": "string",
    "version": "string",
    "config_hash": "string"
  },
  "results": {
    "new_inundation_km2": 0,
    "receded_water_km2": 0,
    "persistent_water_km2": 0
  },
  "validation": {
    "reference": "string",
    "iou": null,
    "f1": null,
    "precision": null,
    "recall": null
  },
  "limitations": []
}
```

Never put invented values into production demo metadata.
