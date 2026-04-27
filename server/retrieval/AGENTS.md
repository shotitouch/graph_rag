# AGENTS.md

## Purpose
This component owns vector retrieval, reranking, and retrieval readiness behavior.

## Scope
- `service.py`
- `reranker.py`
- `schemas.py`

## Rules
- Preserve startup-time retrieval readiness. Avoid import-time network side effects.
- Keep metadata keys stable for downstream consumers unless a coordinated contract change is intended.
- Keep reranker fallback safe when the model is unavailable.
- Keep retrieval behavior separate from workflow policy and API response shaping.
- Do not move Qdrant-sensitive logic into unrelated components.

## Validation
- Run compile or import validation after changes here.
- Verify backend startup still succeeds when Qdrant is available.
- Verify `/ingest/` plus `/ask/` flow when retrieval behavior or metadata assumptions change.
- Use `docs/evaluation.md` when judging evidence strength for retrieval quality changes.
