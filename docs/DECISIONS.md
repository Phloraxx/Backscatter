# Decision Log

## D-001 — Challenge
**Decision:** NASA Space Apps 2026, Dancing with the SARs.

## D-002 — Repository / working product name
**Decision:** Backscatter.

Reason: backscatter is the actual radar measurement concept central to SAR and gives the project a clean technical identity.

## D-003 — Initial vertical
**Decision:** prioritize flood/wetland inundation change.

Reason: strongest combination of scientific fit, social impact, demo quality and 48-hour feasibility.

## D-004 — Primary product family
**Decision:** evaluate GCOV first.

Reason: geocoded, calibrated, terrain-corrected backscatter is a practical basis for a hackathon surface-change pipeline.

## D-005 — AI role
**Decision:** AI may explain results but should not be the scientific measurement engine.

## D-006 — Geography
**Decision:** not locked.

Kerala/Western Ghats is the first candidate, subject to real scene availability and validation quality.

## D-007 — Deployment philosophy
**Decision:** curated preprocessed case studies for MVP, on-demand global processing as roadmap.

## Open decisions

- exact event/region;
- polarization feature set;
- baseline classifier;
- validation reference;
- whether GUNW coherence improves the primary case;
- final tagline and visual identity.


## Update — 2026-11-03

### D-008 — Primary research case
**Decision:** Kuttanad, Kerala, WGS84 bbox `76.42,9.40,76.49,9.47`, with NISAR Sep 14/26 and OPERA Sep 15/27 as candidate observations. Lower Assam is backup. Supersedes the open geography preference in D-006 **for research prioritization only**; final event case is conditional on validated NISAR science.

### D-009 — Evidence boundary
**Decision:** OPERA-only reported change (net −2.0979 km² classified water) cannot be described as NISAR flood detection. Both NISAR sources currently have only authenticated-file-header checks.

### D-010 — Data and secret hygiene
**Decision:** keep token, signed redirect links, HDF5/GeoTIFF source products and local `.netrc` outside Git. Commit small research scripts, manifests, metrics and the OPERA-only figure.
