# Lower Assam — independent validated NISAR candidate

**Status: actual NISAR and OPERA data processed, 14 November 2026.** NISAR before/after and OPERA Sentinel-1 WTR reference rasters were downloaded and compared. Locally fitted open-water held-out F1 was 0.6755, and gained/lost-water F1 was only 0.0353/0.0336. The unchanged Kuttanad threshold gave first-date static F1 0.4275 and gain/loss F1 0/0.

See [Measured scientific report](MEASURED_RESULTS.md), [actual metrics](assam_nisar_opera_diagnostic.json), [radar preview](assam_radar_change.jpg), and [full source checksums](source_checksums.json).

## Why this second case?

The primary Kuttanad research has real NISAR HHHH/HVHV measurements and an OPERA optical comparison. To check whether the observations generalize, we identified a second distinct geography: **Lower Assam, India**, WGS84 bounding box `90.28,26.16,90.35,26.23` (about 7 × 8 km). The initial metadata candidate has now been processed; the original preflight records remain below.

NASA CMR confirms two validated NISAR GCOV observations with matching geometry `069_A_015_4005_DHDH` and processing release `P05036`:

- 28 Oct 2026: `NISAR_L2_PR_GCOV_034_069_A_015_4005_DHDH_A_20261028T232206_20261028T232240_P05036_N_F_J_001` — `G4410147621-ASF`.
- 09 Nov 2026: `NISAR_L2_PR_GCOV_035_069_A_015_4005_DHDH_A_20261109T232206_20261109T232241_P05036_N_F_J_001` — `G4409018076-ASF`.

Candidate **OPERA DSWx-S1 v1.0** reference products from independent Sentinel-1 C-band radar:

- 31 Oct 2026: `OPERA_L3_DSWx-S1_T46RBQ_20261031T235432Z_20261101T200652Z_S1D_30_v1.0` — **3 calendar days after NISAR**.
- 10 Nov 2026: `OPERA_L3_DSWx-S1_T46RBQ_20261110T120427Z_20261110T210338Z_S1D_30_v1.0` — **1 calendar day after NISAR**.

These product identifiers and their WTR asset URLs were verified using `scripts/preflight_assam.py`, which passes without an Earthdata token. Actual pixels and classification agreement are now evaluated, but no physically verified flooding or field-validated change-accuracy claim exists.

## Reproduce measured work

On a trusted Earthdata-authenticated host with Python 3:

```bash
python scripts/preflight_assam.py
python scripts/harmony_assam.py submit
# Once the two NASA Harmony jobs have succeeded:
python scripts/harmony_assam.py fetch
python scripts/fetch_opera_assam.py
# Install numpy, rasterio and optionally matplotlib before the final step:
python scripts/compare_assam_opera.py
```

**Avoid re-submitting** Harmony jobs if a previous run already wrote `~/Downloads/backscatter-assam-validated/nisar/job_*.json`. Both Harmony jobs subsequently completed and were downloaded. Check saved job IDs first to avoid redundant submissions.

The source TIFFs and private Earthdata token must stay outside Git. The comparison script has already created the outputs below. On rerun, it will update `~/Downloads/backscatter-assam-validated/analysis/` only after both NISAR and OPERA inputs exist.

## Critical reference-class difference

OPERA **DSWx-S1** WTR codes are *not* the same as the previous Kuttanad **DSWx-HLS** optical codes. For S1, **0=not water, 1=open water, 3=inundated vegetation**; 250/251/254/255 represent masks/no data. Strict open-water comparison uses **only 0/1**. Class 3 is reported separately. See [OPERA S1 class documentation](https://developers.google.com/earth-engine/datasets/catalog/OPERA_DSWX_L3_V1_S1).

## Calibration and scientific limitations

ASF [validated-release notes](https://hyp3-docs.asf.alaska.edu/nisar-docs/release-notes/) state that **approximately 30% of data collected in certain 40M05 radar modes before 12 Nov 2026 may have ~1 dB calibration residuals** and polarimetric phase inconsistencies. Our selected NISAR scenes are before that date and use a 4005 dual-polarization acquisition family. **We have not independently verified their RCID or whether these specific granules are affected.** Accordingly, small observed dB changes should not be attributed unconditionally to land or water change.

OPERA dates are offset from NISAR acquisitions; OPERA S1 is an independent radar classification product but **not** field truth. This case cannot by itself establish flood damage, impact or classification reliability.

[Machine-readable source manifest](scene_manifest.json).
