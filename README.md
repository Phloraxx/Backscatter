# Backscatter

**Team Afterimage · NASA Space Apps Challenge 2026 · Dancing with the SARs**

> **See the evidence of Earth's changing waters.**

Backscatter is a proposed interactive, evidence-driven application for investigating changes in floodplain and wetland water coverage using repeat **NASA–ISRO NISAR SAR measurements**. Planned outcome: change maps, measurements, uncertainty, and explanation grounded in observable radar evidence.

**Current phase: research/data-feasibility only. No NISAR-derived inundation mask, validation score, live dashboard, or working flood predictor exists yet.** These preparations do not constitute a completed Space Apps submission.

## Verified data progress — 2026-11-03

- **Kuttanad, Kerala** is the primary candidate, with a small study box at `[76.42, 9.40, 76.49, 9.47]` (longitude/latitude, WGS84).
- Two repeat NISAR **L2 provisional GCOV** products were located (2026-09-14 and 2026-09-26); a local Mac test received HTTP **206** and valid HDF5 file signatures for both.
- Two **OPERA DSWx-S1** surface-water products (2026-09-15 and 2026-09-27) were downloaded, inspected, and compared on their common 30 m grid. These are **independent Sentinel-1 observations**, not NISAR results or definitive ground truth.
- Across **59.9067 km²** of valid compared pixels: **3.0483 km² new water/inundated-vegetation classification**, **5.1462 km² loss**, **8.4474 km² classified water on both dates**; net classified-water change **-2.0979 km²**.
- **Still unverified:** extracting actual NISAR measurement arrays; their scientifically meaningful change; agreement with reference observations; classification accuracy.

![OPERA-only Kuttanad comparison (not NISAR)](research/kuttanad_2026_09/opera_comparison.png)

See [research record](research/kuttanad_2026_09/README.md), [project status](docs/PROJECT_STATUS.md), and [data manifest](research/kuttanad_2026_09/scene_manifest.json).

## Reproduce the preparatory data checks

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-research.txt
python scripts/verify_earthdata_access.py
python scripts/compare_opera_dswx.py
```

A free NASA Earthdata account/token is required; scripts request a token interactively and **never store it**. Downloaded source TIFFs are placed outside the repository in `~/Downloads/backscatter-opera-check/`. Full instructions: [docs/REPRODUCTION.md](docs/REPRODUCTION.md).

## Intended MVP (not yet built)

1. Select a compatible NISAR radar pair.
2. Extract and quality-check matching radar measurements; calculate change features.
3. Classify probable water-extent change with explicit uncertainty.
4. Compare with independent observations and report documented limitations.
5. Show evidence and provenance through an interactive map.

Avoid representing OPERA-derived changes as NISAR detections, or seasonal water changes as confirmed flood damage. No disaster prediction, landslide detection, or unverified AI claims in the MVP.

**Repository index:** [Master context](CONTEXT.md) · [Architecture](docs/ARCHITECTURE.md) · [Scientific plan](docs/DATA_AND_PIPELINE.md) · [Validation](docs/VALIDATION_PLAN.md) · [Hackathon plan](docs/HACKATHON_EXECUTION.md) · [Research status](docs/PROJECT_STATUS.md).

**Security:** Do not commit Earthdata access tokens, `.netrc`, credentials, signed links, or raw multi-GB satellite downloads. Check NASA Space Apps pre-event development rules before using this research preparation as part of a final submission.
