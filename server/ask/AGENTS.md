# AGENTS.md

## Purpose
This component owns the request and response boundary for question answering.

## Scope
- `router.py`
- `schemas.py`
- `service.py`

## Rules
- Keep the router thin. Route handlers should delegate to service logic.
- Keep request and response contract changes explicit.
- Keep citation validation in this component, not inside workflow internals.
- Preserve fail-closed safe-response behavior unless an API policy change is explicitly intended.
- Do not move retrieval logic or workflow control flow into this component.

## Validation
- Verify `/ask/` with a valid request when behavior changes here.
- Check that citation validation still works when sources are returned.
- Check abstain behavior when answerability or citations fail.
- Use `docs/evaluation.md` when judging evidence strength for answer quality, citations, or abstain behavior changes.
