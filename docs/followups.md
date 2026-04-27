# Follow-Ups

## Purpose
This document tracks durable open issues, deferred work, and known gaps that should be revisited beyond a single workflow run.

Use it when:
- a task ends with unresolved product or engineering issues
- a later phase is intentionally deferred
- a known weakness should influence future task selection

Do not use it for transient notes that only matter inside one run record.

## How To Use
- Consult relevant follow-ups during planning when a new task overlaps an existing gap or deferred item.
- Add or update follow-ups during closeout when a task reveals durable unresolved issues.
- Mark follow-ups as closed when a later task resolves them.

## Entry Template
Use this structure for each item:

```md
### <short title>
- source: <run record, task, or file>
- priority: <high | medium | low>
- status: <open | deferred | closed>
- next action: <recommended next step>
- notes: <optional context>
```

## Open

### Computation-Heavy Branch Not Reached Reliably Through `/ask/`
- source: `docs/runs/2026-04-27-single-filing-coverage-routing.md`
- priority: high
- status: open
- next action: improve live coverage classification so representative arithmetic questions reliably reach `computation_heavy` through `/ask/`
- notes: branch logic has narrower runtime evidence, but live analyzer behavior still routes example arithmetic prompts to `focused_lookup` or `default_technical`

### Citation Policy Allows Missing Required Bracket Citations
- source: `docs/runs/2026-04-27-single-filing-coverage-routing.md`
- priority: high
- status: open
- next action: tighten answer validation so responses that require bracket citations fail when those citations are missing
- notes: current validator rejects invalid IDs but still allows some answered responses with sparse or non-bracket citation formatting

## Deferred

### Cross-Company And Multi-Filing Coverage Routing
- source: `docs/runs/2026-04-27-single-filing-coverage-routing.md`
- priority: medium
- status: deferred
- next action: design a later-phase workflow for cross-company and multi-filing comparison instead of extending the first-pass single-filing coverage router
- notes: intentionally kept out of scope for the first-pass coverage-type implementation

## Closed
- Add resolved follow-ups here if you want a lightweight history. Otherwise, delete resolved items instead of keeping this section populated.
