# AGENTS.md

## Purpose
This component owns PDF upload flow, metadata extraction handoff, chunk construction, and vectorstore writes.

## Scope
- `router.py`
- `service.py`
- `schemas.py`

## Rules
- Keep the router thin. Upload validation and transport should stay in `router.py`; ingestion logic should stay in `service.py`.
- Preserve file-type and mode validation unless API requirements change.
- Keep metadata extraction and normalization explicit.
- Preserve chunk metadata fields required by retrieval and ask flows.
- Do not move question-answering behavior into this component.

## Validation
- Verify `/ingest/` with a sample PDF when behavior changes here.
- Check extracted metadata fields such as ticker, year, period, and metadata completeness.
- Check chunk counts or vectorstore write behavior when chunking logic changes.
- Use `docs/evaluation.md` when judging evidence strength for ingestion or metadata quality changes.
