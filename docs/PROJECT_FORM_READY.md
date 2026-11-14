# Backscatter: copy-ready NASA Space Apps submission fields

Team: AfterImage (six official members). Challenge: Dancing with the SARs.
Status: DRAFT ONLY. This document does not submit or save anything on the NASA site.
Before submission confirm all team members' eligibility/age, participation form, license, and earlier-work disclosure.

## Project Title

Backscatter — Read the Surface, Question the Signal

## High-Level Project Summary

Backscatter is an interactive, evidence-first application that lets people explore actual NASA–ISRO NISAR L-band synthetic aperture radar observations over changing landscapes. It compares measured radar returns across two dates, visualizes HH/HV signals and their changes, and provides a separate NASA OPERA water-classification reference for context. We tested Kuttanad in Kerala and Lower Assam, and independently investigated a documented Cyclone Arnab event near the Godavari delta. Simple radar-change thresholds can highlight physical signal variation, but they do not consistently detect water-class transitions. Rather than presenting an unreliable flood map, Backscatter makes the measurements, uncertainty, and failed generalization visible and reproducible.

## Final Project Link

https://backscatter-afterimage-2026.pages.dev/

## Project Demo Link — seven slides

https://backscatter-afterimage-2026.pages.dev/backscatter-demo.pdf

## Public supporting research

https://backscatter-afterimage-2026.pages.dev/research.html

## Detailed Project Description — what we built and why

Radar can image Earth's surface through cloud cover and at night, making it useful for studying environmental change. Yet a darker pixel or changing backscatter is not automatically flooding: vegetation, wet soil, surface roughness, cropping patterns, radar geometry and calibration uncertainty also affect the return.

We built a responsive React and MapLibre browser viewer with NASA–ISRO NISAR Level-2 GCOV measurements for Kuttanad and Lower Assam. Users can swipe interactively between before/after NISAR radar observations, switch signal-change and OPERA reference layers, and click georeferenced 30 m samples to inspect the actual HH/HV measurements and independent reference dates. Users can export a source-backed text evidence note with measurements, provenance and limitations. We show independent NASA OPERA DSWx-HLS and DSWx-S1 reference classifications without treating these as field truth. The viewer includes an optional spatially coherent signal overlay computed with a fixed 3 dB change threshold, per-date 3×3 median filtering and a 6-of-9 neighborhood agreement rule. The overlay's teal and amber colors mean radar signal decrease and increase, never confirmed flooding.

The underlying Python pipeline uses actual calibrated NISAR source raster data, aggregates linear radar power before converting to dB, aligns geospatial grids, and evaluates scientific claims with reproducible confusion matrices. It avoids reporting flood areas without independent evidence.

## Scientific Findings and Validation

In Kuttanad, the spatial coherence rule reduced the fraction of OPERA-classified stable non-water pixels falsely highlighted from 4.303% (raw) to 0.319%. It also missed some reference water-class transitions; the simpler 3×3 median rule had higher water-gain F1.

In Lower Assam, the unchanged rule failed to identify strict OPERA open-water gain/loss transitions (F1 = 0 for both). A separate cyclone-linked study, with validated NISAR scenes October 22 and November 3 and Sentinel-1D OPERA references approximately 11.2 hours after each NISAR acquisition, reproduced the failure (F1 = 0 for both gain/loss). The OPERA data contained 842 reference non-water-to-open-water and 75 reverse transitions, but these are satellite product classifications, not field-confirmed flood extents.

A separately fitted threshold can classify static water relatively well in particular conditions but does not reliably infer change. These results show why open scientific evidence, negative results, and uncertainty matter. This is a scientific demonstration, not an operational flood warning, forecast or damage assessment system.

## Community Benefit and Future Work

Students, researchers and interested communities can explore what radar actually measures and understand uncertainty instead of treating maps as unquestionable predictions. The current viewer is educational and investigative. Future work needs documented events, independent field or high-quality reference labels, additional comparable same-track NISAR observations and stronger, physically justified signal interpretation.

## Technology and Tools

Frontend: React, MapLibre GL JS, proj4js, Vite. Research: Python, NumPy, Rasterio/GDAL, Pillow and Matplotlib. Data discovery and retrieval: NASA Earthdata Common Metadata Repository (CMR), Alaska Satellite Facility (ASF) and NASA Harmony. Hosting: Cloudflare Pages. Basemap: OpenStreetMap contributors. Version control: Git/GitHub. The original Backscatter logo was provided by the team.

## NASA Data and Space Agency Resources

- NASA–ISRO NISAR L-band Level-2 validated GCOV (HHHH; HVHV for Kuttanad), distributed via NASA ASF/Earthdata. Used to measure radar backscatter at before/after dates. Exact source granules and versions are documented in the public research page and repository source manifests.
- NASA OPERA DSWx-HLS and DSWx-S1, distributed by PO.DAAC. Used as independent satellite-based reference water classes with documented temporal offsets and differences in sensor/class semantics.
- NASA Earthdata Search / ASF Search and NISAR GCOV product documentation. Used for product discovery, understanding and processing.

## Other References and Source Attribution

- India Meteorological Department (IMD), Cyclone Arnab report for October 28, 2026, near coastal Andhra Pradesh and Yanam: https://mausam.imd.gov.in/Forecast/mcmarq/mcmarq_data/Press%20Release%20Dtd%2028.10.2026.pdf
- International Charter for Space and Major Disasters, activation 1056. Used for independent event context only: https://disasterscharter.org/activations/flood-in-india-activation-1056-
- OpenStreetMap contributors; React, MapLibre GL JS, proj4js, Vite, NumPy, Rasterio/GDAL, Pillow and Matplotlib. See docs/ATTRIBUTION_AND_RELEASE.md for original-source credits and license checks.

## AI / SI Tools — disclose explicitly

ChatGPT by OpenAI was used for early research synthesis, implementation planning, coding assistance, debugging, scientific-evaluation scripts, documentation, and preparing the website and slide deck. The satellite data, numerical metrics and plotted radar data are genuine and were computed by deterministic code; AI-generated predictions are not presented as ground truth. Additional AI tools should be added only if team members actually used them, and the project's earlier research/code history must be disclosed accurately.

## Before clicking Submit for Judging

- Verify original work licensing and any publication permissions, including branding.
- Verify all six participants' NASA/Thrissur confirmations and under-18 rules.
- Clarify earlier project-specific work with organizers as needed; do not represent pre-event work as post-event.
- Put both public links in the correct fields, optionally add public research, and verify they work in a private browser.
- Include required NASA references and AI usage. Save progress, have exactly one authorized person submit, and verify the final confirmation.
