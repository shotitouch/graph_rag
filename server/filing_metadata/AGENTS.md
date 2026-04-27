# AGENTS.md

## Purpose
This component owns 10-Q filing metadata extraction and normalization.

## Scope
- `extractor.py`
- `normalizer.py`
- `schemas.py`

## Rules
- Keep raw extraction and normalization responsibilities explicit.
- Preserve canonical metadata fields such as ticker, year, and period unless a coordinated contract change is intended.
- Prefer deterministic extraction where reliable, and use model-based extraction as a bounded fallback.
- Do not move ingestion transport or retrieval behavior into this component.
- Keep normalization conservative; do not guess unsupported metadata values.

## Validation
- Run compile or import validation after changes here.
- Verify extracted ticker, year, and period on representative sample filings when behavior changes.
- Verify downstream ingestion still receives the metadata shape it expects.
- Use `docs/evaluation.md` when judging evidence strength for metadata quality changes.
