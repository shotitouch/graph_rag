# AGENTS.md

## Purpose
This component owns graph orchestration, state transitions, routing, retries, and grading flow.

## Scope
- `graph.py`
- `state.py`
- `nodes.py`
- `edges.py`
- `schemas.py`

## Rules
- Keep graph control flow explicit in nodes and edges.
- Keep state mutations explicit and traceable through `state.py` fields and node returns.
- Do not hide routing or retry decisions only inside prompts when they affect orchestration behavior.
- Preserve fail-closed answer behavior when changing generation, grading, or rewrite loops.
- Do not move API transport concerns into this component.

## Validation
- Run compile or import validation on this component after edits.
- Verify `/ask/` end-to-end when routing, retrieval flow, retries, or grading behavior changes.
- Confirm state fields still align with downstream consumers such as `ask/service.py`.
- Use `docs/evaluation.md` when judging evidence strength for grounding, abstain behavior, or workflow-quality changes.
