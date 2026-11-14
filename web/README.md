# Backscatter interactive demo

![Backscatter desktop preview](preview.jpg)

A static React/Vite/MapLibre map displaying **real NASA–ISRO NISAR validated GCOV** measurements from Kuttanad, Kerala.

## Run

```bash
cd web
npm install
npm run dev
```

Visit the local address printed by Vite. No Earthdata token is needed to view the curated, already-prepared sample.

## What it shows

- NISAR 2026-10-29 HHHH backscatter.
- NISAR 2026-11-10 HHHH backscatter.
- Measured change in backscatter, *not* inferred flooding.
- Independent OPERA DSWx-HLS 2026-10-29 optical water classifications.
- A click-to-inspect panel with 30-metre pixel measurements and satellite reference class.
- Quantified agreement with OPERA, including low change-detection F1 values.

The base map requires an internet connection (OpenStreetMap tiles); overlay rasters and pixel measurements are stored locally under `web/public/data`.

## Regenerate source assets

On a machine with the locally downloaded NISAR/OPERA GeoTIFFs from [the research pipeline](../docs/VALIDATED_DATA_EXECUTION.md):

```bash
python scripts/export_demo_assets.py
```

This generates small RGBA PNG layers and a little-endian binary 30-metre measurement grid. It does **not** export large source HDF5/GeoTIFFs or user tokens.

## Science limits

The application is a **radar evidence viewer**, not a validated flood detection tool. A static single-threshold water classifier achieved strong product-to-product agreement (east-half F1 0.9435), but change-mask agreement with temporally offset OPERA was weak (F1 0.2013 gain / 0.2181 loss). Those figures are not flood accuracy or field-ground-truth metrics. Read [the detailed research](../research/kuttanad_validated_2026_10_11/INDEPENDENT_COMPARISON.md).
