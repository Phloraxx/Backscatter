# GitHub Copilot Instructions — Backscatter

Backscatter is a NASA Space Apps 2026 NISAR/SAR project.

Before generating code, use the repository docs as source of truth:
- `CONTEXT.md`
- `AGENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_AND_PIPELINE.md`
- `docs/SCIENCE_AND_SAR.md`

Engineering style:
- Python processing functions should be deterministic and unit-testable.
- Keep geospatial CRS/transform/nodata metadata explicit.
- Never invent scientific thresholds without documenting their source or calibration method.
- Keep frontend copy scientifically cautious.
- Preserve observation provenance in API responses.
- Treat AI/LLM features as explanation interfaces, not measurement engines.
