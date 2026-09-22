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
