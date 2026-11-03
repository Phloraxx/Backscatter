# Product Vision

## One-line concept

**Backscatter turns NISAR radar observations into explainable maps of how Earth's surface changed.**

## Primary user story

A user selects a known case-study region and two compatible observation dates.

Backscatter shows:
- observation A;
- observation B;
- radar-change layer;
- inferred water/inundation change;
- newly inundated area;
- receded area;
- confidence;
- measurement evidence;
- relevant context.

## Core interaction

The map should make the science legible in seconds.

Suggested controls:
- date A / date B;
- swipe or temporal slider;
- layer toggles: `SAR`, `CHANGE`, `WATER`, `COHERENCE`;
- click-to-inspect evidence;
- concise "Why?" explanation.

## Fictional example result card (illustration only, not a measured output)

Surface change detected

- Probable new inundation: 14.2 km²
- Observation interval: 12 days
- Median backscatter change: -5.8 dB
- Coherence: 0.27 (if available/applicable)
- Confidence: High
- Interpretation: Radar response is consistent with expansion of open/smooth surface water in this region.

Wording must remain cautious: "consistent with", "probable", "evidence suggests" when ground truth is incomplete.

## Why this wins over a viewer

A viewer shows pixels.
Backscatter shows:
- measured change;
- classified meaning;
- uncertainty;
- provenance;
- validation.

## Future product expansion

After a robust inundation MVP:
- flooded vegetation;
- agricultural change;
- forest disturbance;
- shoreline change;
- deformation/inSAR;
- multi-band L/S comparison where practical.

Do not implement these until the first workflow is validated.


## Evidence status (2026-11-03)

The example result card above is **fabricated UX placeholder data**, not a real NISAR measurement or accuracy finding. The only measured results in this repository are from an independent OPERA water-classification comparison; see `research/kuttanad_2026_09/`. Do not use placeholder numbers in a presentation.
