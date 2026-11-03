# Backscatter — Master Context

## Challenge

NASA Space Apps Challenge 2026  
Challenge: **Dancing with the SARs**

The challenge centers on using NASA–ISRO NISAR Synthetic Aperture Radar data to reveal and communicate changes at Earth's surface.

## Core project thesis

Backscatter should turn difficult SAR measurements into transparent, useful evidence of change.

The product should answer:

1. **What changed?**
2. **Where did it change?**
3. **How much did it change?**
4. **What measurements support that interpretation?**
5. **How confident are we?**
6. **What can the user see directly in the source observations?**

## Current MVP hypothesis

Focus first on **surface-water / flood / wetland inundation change**.

Why:
- strong physical fit for SAR;
- cloud independence is easy to explain;
- monsoon/disaster relevance;
- measurable area change;
- possible independent validation;
- excellent before/after demo.

## Product principle

Do not build:
- a generic map portal;
- a layer dump;
- an LLM chatbot over NISAR docs;
- a "predict disasters with AI" demo;
- a system claiming every SAR change corresponds to flooding.

Build:
- a constrained analytical workflow;
- scientifically defensible outputs;
- uncertainty-aware interpretation;
- a polished interactive map;
- a clear data lineage from pixels to conclusion.

## Current technical direction

Primary:
- NISAR L-band GCOV for geocoded, terrain-corrected backscatter.

Potential secondary:
- GUNW coherence as evidence of surface disturbance/change.
- precipitation, elevation, historical water or optical imagery as context, not as a substitute for NISAR.

## Architecture concept

Frontend:
- React
- MapLibre GL
- Deck.gl where necessary

Backend:
- FastAPI
- Python scientific stack
- Rasterio / GDAL / Xarray / NumPy

Data access:
- NASA Earthdata / ASF
- Harmony / Vertex / earthaccess where appropriate

Output:
- preprocessed Cloud Optimized GeoTIFFs / tiles
- vectorized change polygons where useful
- metrics and provenance JSON

## Branding

Repository/product working name: **Backscatter**

"Backscatter" is technically native to SAR: the system measures radar energy scattered back toward the sensor.

Possible descriptor:
**Backscatter — Radar intelligence for a changing Earth.**


---

## Research update — 2026-11-03

Kuttanad (Kerala) is now the **primary research candidate** and Lower Assam remains a backup. Two NISAR L2 provisional GCOV product headers (Sep 14/26, 2026) passed authenticated HTTP range access checks. A separate OPERA DSWx-S1 Sentinel-1 water comparison (Sep 15/27) yielded 59.9067 km² common valid coverage, 3.0483 km² newly classified water/inundated vegetation, 5.1462 km² lost classification, net −2.0979 km². No NISAR radar array has yet been extracted or interpreted. See `docs/PROJECT_STATUS.md` and `research/kuttanad_2026_09/`. Do not promote OPERA results to NISAR-derived detection claims.
