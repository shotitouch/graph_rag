# 0001 Component-First Backend Structure

## Status
Accepted

## Date
2026-04-27

## Context
The backend originally used a mostly layer-first structure such as `core/`, `graph/`, `router/`, and `utils/`.

That structure worked for single-agent or single-developer changes, but it created weak ownership boundaries for delegated agent work because many tasks crossed shared layer files.

## Decision
Reorganize the backend into component-owned directories such as:
- `server/ask/`
- `server/workflow/`
- `server/retrieval/`
- `server/ingestion/`
- `server/filing_metadata/`
- `server/llm_runtime/`
- `server/shared/`

Each component should own its local logic and, where possible, its local schemas and validation rules.

## Consequences
- component ownership is clearer
- subagent write scopes are easier to define
- cross-component integration becomes more explicit
- some shared concerns must now be handled intentionally through `server/shared/` or the main agent
