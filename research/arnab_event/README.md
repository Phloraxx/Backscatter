# Cyclone Arnab — event-linked NISAR investigation

**State as of November 14, 2026: source metadata and radar footprints verified; actual event pixels NOT YET analyzed.**

Backscatter's earlier case studies (Kuttanad, Kerala and Lower Assam) demonstrated that simple radar-change thresholds do not reliably detect open-water transitions. This **third candidate** is selected because it brackets a *documented natural hazard*, rather than relying on an unconfirmed assumption that flooding happened during two arbitrary satellite passes.

## Event and location

India Meteorological Department records show that Very Severe Cyclonic Storm **Arnab** crossed the Andhra Pradesh–Yanam coast on **October 28, 2026**, close to **16.45°N, 81.9°E**, east-northeast of Narsapur. The [International Charter, activation 1056](https://disasterscharter.org/activations/flood-in-india-activation-1056-) documents flooding in Andhra Pradesh and Odisha, with published satellite flood-response maps.

**Predeclared test AOI:** longitude **81.82–81.89°E**, latitude **16.58–16.65°N** (coastal Godavari delta, Andhra Pradesh). It was selected using the event location and source coverage **before analyzing any raster pixels**. This is *near*, not at, the reported landfall center; published flood maps do not verify flooding in every cell of this exact AOI.

We will not copy or republish ISRO/Charter imagery marked for official use. Those reports are linked for event context only.

## Four NASA catalog-verified satellite products

| Product | Pre-event | Post-event | Acquisition relationship |
|---|---|---|---|
| NASA–ISRO NISAR validated L-band GCOV V1, frequency-A HHHH | **Oct 22, 2026**, 13:09:52 UTC | **Nov 3, 2026**, 13:09:53 UTC | Same track/frame, same 40 MHz dual-HH configuration and P05036 processing |
| NASA OPERA DSWx-S1 v1.0 WTR, derived from Sentinel-1D C-band | **Oct 23, 2026**, 00:22:01 UTC | **Nov 4, 2026**, 00:22:01 UTC | Same OPERA tile T44QPD, both ~11 hours 12 minutes AFTER their respective NISAR pass |

**This is the closest pair yet found for Backscatter**: the reference observation gaps are **11.2025 and 11.2022 hours**. These are still separate radar instruments with different wavelengths, processing pipelines, and noise characteristics. OPERA WTR is *not* field ground truth.

The NISAR granules are:

- \`G4405748574-ASF\` — \`NISAR_L2_PR_GCOV_033_149_D_080_4005_DHDH_A_20261022T130952_20261022T131027_P05036_N_F_J_001\`
- \`G4405145629-ASF\` — \`NISAR_L2_PR_GCOV_034_149_D_080_4005_DHDH_A_20261103T130953_20261103T131027_P05036_N_F_J_001\`

The OPERA DSWx-S1 granules are:

- \`G4386072092-POCLOUD\` — Oct 23, tile \`T44QPD\`, Sentinel-1D
- \`G4405822836-POCLOUD\` — Nov 4, tile \`T44QPD\`, Sentinel-1D

All four identifiers were verified against NASA CMR; **both NISAR polygons contain all four corners** of the study AOI. The complete names, timestamps, collection IDs, and limits are recorded in the [machine-readable manifest](scene_manifest.json).

## Reproduction

The two NISAR Harmony subset requests **were already submitted** on November 14. Their saved job IDs reside only on the authorized Mac:

\`~/Downloads/backscatter-arnab-validated/nisar/job_2026-10-22_HHHH.json\` and \`job_2026-11-03_HHHH.json\`.

Use these commands from the project root on the Mac (temporary Earthdata credential is entered **only at the hidden prompt**):

\`\`\`bash
python3 scripts/preflight_arnab.py
python3 scripts/harmony_arnab.py fetch
python3 scripts/fetch_opera_arnab.py
~/Downloads/backscatter-venv/bin/python3 scripts/compare_arnab_opera.py
\`\`\`

**Do not rerun \`harmony_arnab.py submit\`**: the saved jobs are already present and should be inspected/fetched. If Harmony reports processing instead of success, use \`fetch\` again when complete.

The comparison reuses the **unchanged, label-free** signal-change methods used in the two other case studies:

- RAW signed ±3 dB HH change;
- 3×3 median-filtered per-date HH change at ±3 dB;
- coherent HH radar changes with at least 6/9 neighboring strong same-direction cells and at least seven valid neighbors.

These rules require **no OPERA labels** to create a candidate signal map. The eventual comparison will report OPERA 0→1 and 1→0 transition agreement separately and preserve OPERA **class 3, inundated vegetation**, as a separate reference class. A local water-threshold fit is an exploratory comparison only and **not** the main event test.

## Evidence standards

This event is **documented**, but we must still establish whether our *particular AOI* has valid, persistent water changes at the NISAR/OPERA times. Floodwaters may have receded by November 3, and standing water can reflect crop irrigation or pre-existing wetlands. Neither a large backscatter change nor OPERA class 1 proves a disaster cause.

The NISAR validated collection was released in November 2026 and our scenes use processing CRID **P05036**. ASF's [release notes](https://hyp3-docs.asf.alaska.edu/nisar-docs/release-notes/) flag residual radiometric errors in some pre-November-12 observations; the precise affected status of these scenes has not been verified. No flood-area, damage, population or prediction accuracy figure is claimed.

**Do not place this event in the public viewer as a completed study until actual pixels and the failed/successful outcomes are verified.**

## Sources

- [IMD hourly bulletin, 28 October](https://mausam.imd.gov.in/backend/assets/cyclone_pdf/10_Hourly_Bulletin_271026_2300UTC.pdf).
- [International Charter for Space and Major Disasters — Cyclone Arnab, activation 1056](https://disasterscharter.org/activations/flood-in-india-activation-1056-).
- [NASA NISAR validated availability](https://nisar-docs.asf.alaska.edu/availability-overview/).
- [NASA OPERA DSWx product suite](https://www.jpl.nasa.gov/go/opera/products/dswx-product-suite/).
- [ASF validated NISAR known issues](https://hyp3-docs.asf.alaska.edu/nisar-docs/release-notes/).
