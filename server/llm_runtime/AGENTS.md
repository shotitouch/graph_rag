# AGENTS.md

## Purpose
This component owns model client setup, prompt definitions, and structured-output chains.

## Scope
- `client.py`
- `chains.py`
- `prompts.py`

## Rules
- Treat prompt and chain changes as cross-component sensitive.
- Keep model client initialization stable and avoid unnecessary side effects.
- Preserve structured output contracts unless downstream consumers are updated together.
- Do not hide orchestration policy in prompts alone when explicit workflow logic is more appropriate.
- Keep prompt changes targeted and aligned with project grounding and evaluation goals.

## Validation
- Run compile or import validation after changes here.
- Verify affected downstream flows such as `/ask/` or `/ingest/` when prompt or chain behavior changes.
- Check for regressions in structured outputs relied on by workflow, filing metadata, or ask components.
- Use `docs/evaluation.md` when judging evidence strength for prompt- or chain-driven quality changes.
