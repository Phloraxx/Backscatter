# Backscatter — NASA Space Apps 2026 submission preparation

**Team:** Afterimage

**Challenge:** Dancing with the SARs

**Deadline:** November 15, 2026, 11:59 PM local event time (verify your registered event).

**Status:** Draft for review. NOT submitted.

## Copy-ready form and release review

Use [the fully drafted NASA project fields](PROJECT_FORM_READY.md) and [attribution/release checklist](ATTRIBUTION_AND_RELEASE.md) to avoid omitting required credits. The repository is private and has no team-approved source license yet; this is an **unresolved team decision**, not a completed compliance check.

## Official team roster

The six names below are taken verbatim from the [AfterImage team page on NASA Space Apps](https://www.spaceappschallenge.org/2026/find-a-team/afterimage/) on November 14, 2026. They appear on the title slide of the seven-slide demo PDF; no member roles are invented.

- Karthik Krishna M S
- Ann Maria Johny
- Sourav P Bijoy
- Aradhana Rose
- Ishan Sudarsan
- YadhuKrishna T M

**Demo requirement checked:** Project title, team name, names of all six members, and challenge "Dancing with the SARs" are on slide 1. Original team logo is retained; total slides = 7.

## Title and concise project description

**Backscatter — Read the Surface, Question the Signal**

Backscatter is an interactive satellite-radar evidence explorer using actual NASA–ISRO NISAR observations. Users can compare two dates, inspect calibrated HH/HV backscatter, explore spatially consistent radar changes, and view a separate NASA OPERA surface-water classification for context.

The app currently includes two independently measured Indian landscapes: Kuttanad in Kerala and Lower Assam. The results demonstrate why dark radar pixels or changing radar returns cannot automatically be called flooding: a Kuttanad-trained water threshold fails to transfer to Assam. We also tested median filtering and spatial coherence, which reduce noisy radar-change highlights in one scene but miss reference-classified water transitions in another.

Backscatter deliberately separates **measured radar evidence**, **satellite-derived reference interpretation**, and **unresolved uncertainty**. The goal is to communicate what NISAR can and cannot reveal about surface changes—not to claim a validated flood detector or provide operational flood warnings.

## What is actually working

- React + MapLibre two-region website with the team's own original logo and labeled raster overlays.
- Real validated NISAR L-band GCOV HHHH imagery, Kuttanad HVHV cross-polarization evidence, and a click-to-inspect 30 m measurement grid.
- Radar before/after, raw difference and optional coherent-signal overlay (teal decrease, amber increase; **not water colors**).
- Independent NASA OPERA DSWx-HLS optical and DSWx-S1 Sentinel-1 C-band reference classes with acquisition dates displayed.
- Reproducible Earthdata extraction, raster processing, tests and documented negative scientific results.

A **third independent research test is completed** using validated NISAR observations before/after documented Cyclone Arnab and OPERA Sentinel-1 water references ~11.2 hours later. The unchanged coherent radar-signal rule still fails to identify the strict OPERA water-class transitions (gain/loss F1 **0.0000/0.0000**). The event is a scientific negative-result study, **not a confirmed flood map**. See the [public research page](https://backscatter-afterimage-2026.pages.dev/research.html).

## Suggested 7-slide demonstration

1. **Problem & title:** Backscatter logo; Why a radar change isn't necessarily a flood.
2. **NASA data:** NISAR mission, real GCOV dates and correct radar source citation.
3. **Explore the map:** Screenshot showing before/after radar layers in Kuttanad.
4. **Understand the evidence:** Screenshot showing HH/HV pixel inspector and OPERA class labels.
5. **Careful change visualization:** Screenshot showing coherent signal clusters and explicit "not flooded area."
6. **Actual scientific findings:** Show Kuttanad false-highlight reduction and the failure to generalize to Assam.
7. **Impact, limits & independent event test:** The documented Cyclone Arnab comparison also failed to validate the unchanged water-change rule; next step is more robust field/event-based labels.

Keep the demo within **seven slides**, including title and closing slides. Alternatively, provide a **30-second video**. Host the demo on a public link accessible without requesting access.

## Public links — verify before submitting

- **Verified production website:** https://backscatter-afterimage-2026.pages.dev/ — published, independently tested for both geographic studies.
- **Public demonstration deck:** https://backscatter-afterimage-2026.pages.dev/backscatter-demo.pdf — a visually verified, exactly seven-page landscape PDF, accessible in a browser.
- **Public scientific methods/results:** https://backscatter-afterimage-2026.pages.dev/research.html — includes all three studies, raw-source identifiers, metrics and caveats.
- **Code repository:** https://github.com/Phloraxx/Backscatter — currently **private**; reviewers cannot access it without permission. Do not list this as the only public final-project link.
- **Official submission:** https://www.spaceappschallenge.org/2026/ — Project tab on Team Afterimage's page; submitting is a separate user action.

## Source and tool credits

**NASA primary data:** NASA–ISRO NISAR validated L-band Level-2 GCOV V1 via ASF/Earthdata; NASA OPERA DSWx-HLS and DSWx-S1 via PO.DAAC. Include the individual source granule IDs from the repository's study manifests.

**Other context:** OpenStreetMap basemap contributors; JPL OPERA documentation, NASA/ASF GCOV documentation; original Backscatter team logo; relevant original author(s). If included as contextual evidence, cite IMD and the International Charter.

**Software:** Python, NumPy, Rasterio/GDAL, Pillow, Matplotlib, React, Vite, MapLibre, proj4js. Verify exact license obligations before publishing source.

**AI assistance:** Disclose **ChatGPT/OpenAI** assistance with research synthesis, code prototyping, debugging, analysis and documentation. Add any other AI systems actually used by the team; do not claim that none were used.

## Eligibility caution — important

NASA's 2026 organizing-team guidance states that challenge-specific development **before 9:00 AM local time on November 14** can cause disqualification. Backscatter's repository/project preparation visibly predates this. **Do not suggest all work was developed during the event.** Transparently distinguish earlier preparation/research from work on November 14–15 and ask the GO Team/local organizer whether the submission is eligible. Do not conceal, backdate or rewrite prior commits.

## Final check before the deadline

- Public deployment serves both study regions and loads all NISAR/OPERA imagery; verify in a private browser window.
- Demo file or video is also publicly accessible, correctly credited, and within the 7-slide/30-second limit.
- Link the live final project and demo separately on NASA's project form.
- Cite at least one NASA challenge resource, disclose AI tools, comply with original-logo/third-party licensing.
- Confirm the user's registered event/team, then submit through NASA's portal before 11:59 PM on November 15.

**Reference:** [NASA's 2026 event and deadline](https://www.spaceappschallenge.org/2026/); [Space Apps official organizer clarification about pre-event work](https://github.com/nasa/spaceapps/discussions/1827); [2026 hosting and demo clarifications](https://github.com/nasa/spaceapps/discussions/1991).
