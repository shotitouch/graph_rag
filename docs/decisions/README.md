# Decision Log

## Purpose
This directory records important accepted decisions for the project.

These records are for choices that future agents or developers might otherwise revisit without understanding the original context and tradeoffs.

## When To Add A Decision Record
Add a record when a decision is:
- architectural
- durable
- cross-component
- easy to undo accidentally
- likely to affect future tasks or reviews

Do not add records for routine bugfixes, small refactors, or local implementation details.

## Record Structure
Each decision file should include:
- title
- status
- date
- context
- decision
- consequences

## Decision Index
| ID | Title | Read When |
| --- | --- | --- |
| `0001` | Component-First Backend Structure | changing component boundaries, shared ownership, or backend repo layout |
| `0002` | Startup-Time Retrieval Readiness | changing retrieval initialization, Qdrant startup behavior, or import-time side effects |
| `0003` | Fail-Closed Answer Policy | changing abstain behavior, citation validation, or answer safety policy |
| `0004` | Local Agent Guidance Layering | changing how root and component-local `AGENTS.md` files interact |

When adding a new decision record, update this index in the same change.

## How To Use
- Read relevant records before changing established architecture or shared contracts.
- Prefer following accepted decisions unless the task explicitly revisits them.
- If a decision is intentionally changed, create a new record rather than silently overwriting history.

## Relationship To Other Docs
- `AGENTS.md` defines the workflow rule that accepted decisions should be respected unless intentionally revisited.
- `docs/agent_workflow.md` tells the main agent when to consult decision records during planning and integration.
- `docs/project_context.md` explains the broader system goals and heuristics that decision records should support.
