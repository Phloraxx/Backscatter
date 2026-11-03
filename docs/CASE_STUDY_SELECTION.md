# Case Study Selection

## Current geographic hypothesis

Try **Kerala / Western Ghats / west-coast monsoon** first because it provides:
- strong local relevance;
- a natural cloud-cover motivation;
- NASA–ISRO narrative;
- flood/wetland/coastal opportunities.

This is **not yet locked**.

## Selection criteria

A case should have:
1. compatible NISAR observations before/after;
2. meaningful physical change;
3. enough spatial overlap;
4. low ambiguity for the MVP;
5. an independent reference for validation;
6. a strong visual story.

## Preferred set

Aim for:
- one primary India/local case;
- one second case in a different environment;
- optional third demo case.

The same algorithm should operate across cases with limited case-specific tuning.

## Reject a case if

- acquisition metadata are incompatible;
- the event date falls in a data gap;
- the "change" is mostly seasonal vegetation;
- no validation reference exists;
- the pair creates a visually impressive but scientifically ambiguous result.


## Observed research status — 2026-11-03

**Primary candidate:** Kuttanad, Kerala, approx. bbox 76.42–76.49 E / 9.40–9.47 N. Same-track NISAR L2 GCOV products Sep 14 & Sep 26 are catalogued and accessible. Independently, near-date OPERA DSWx-S1 water classifications Sep 15 & Sep 27 have been compared on a common 30 m grid and show a net −2.0979 km² water/inundated vegetation classification change over shared valid cells.

**Not confirmed:** whether the exact NISAR scenes contain a meaningful water change. Maintain Assam backup and avoid choosing a demonstration on the basis of local relevance alone. See `research/kuttanad_2026_09/README.md`.
