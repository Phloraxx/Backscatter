# Kuttanad validated NISAR pair — November 2026

**Research/implementation scope as of 2026-11-14.** No validated NISAR flood result exists yet.

Primary AOI (WGS84 lon/lat): `[76.42,9.40,76.49,9.47]`. NASA Earthdata CMR confirms two L-band **validated** NISAR L2 GCOV granules:

- 2026-10-29: `NISAR_L2_PR_GCOV_034_077_D_084_4005_DHDH_A_20261029T132026_20261029T132100_P05036_N_F_J_001`
- 2026-11-10: `NISAR_L2_PR_GCOV_035_077_D_084_4005_DHDH_A_20261110T132027_20261110T132100_P05036_N_F_J_001`

Both have common `077_D_084_4005_DHDH` geometry identifiers. Source products are around 5 GB each, so process a **small window** rather than downloading both whole files.

The new `scripts/extract_validated_kuttanad.py` has passed scene-discovery `--preflight` and local numerical `--self-test` checks on the Mac. Authenticated pixel extraction is pending.

## Planned independent context

- OPERA DSWx-HLS tile T43PFL from **2026-10-29** (Sentinel-2) and nearby dates: optical water candidate; quality/cloud masking and usable pixel coverage must be inspected.
- OPERA DSWx-S1 tile T43PFL from **2026-10-21** and **2026-11-02** (Sentinel-1): radar water candidate; not same-date validation for Oct 29/Nov 10.
- The prior September OPERA analysis belongs under `research/kuttanad_2026_09/` and does not substantiate any water finding for this new pair.

See [execution instructions](../../docs/VALIDATED_DATA_EXECUTION.md) and [machine-readable source list](scene_manifest.json).

Official documentation:
- https://nisar-docs.asf.alaska.edu/availability-overview/
- https://nisar-docs.asf.alaska.edu/gdal/
- https://nisar-docs.asf.alaska.edu/harmony/
