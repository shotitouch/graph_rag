# Run Records

## Purpose
This directory stores workflow run records for substantial agentic tasks.

A run record captures what actually happened during a task, including planning, delegation, integration, validation, and workflow friction.

Use run records to review and improve the agentic workflow over time.

## When To Create A Run Record
Create a run record when work is:
- multi-agent
- cross-component
- long-lived enough to involve multiple handoffs
- useful for workflow review afterward

Do not create a run record for every trivial or highly localized change.

## Ownership
The main agent owns the run record.

Subagents contribute through structured handoffs, but the main agent writes the integrated record because it has the full view of:
- the plan
- approval scope
- delegation
- handoffs
- integration
- validation
- outcome

## What A Run Record Should Capture
A good run record should make it easy to review:
- what task was attempted
- which roles were used
- what was approved
- what happened during execution
- what validation was performed
- what friction or coordination issues appeared
- what should change in the workflow next time

## Suggested Naming
Use one file per substantial run.

Examples:
- `2026-04-27-retrieval-fix.md`
- `2026-04-27-cross-component-citation-change.md`
- `2026-04-27-ingestion-metadata-review.md`

## Run Record Template
Use this as the default shape for a run record.

```md
# Run Record

## Task
- <short task description>

## Date
- <YYYY-MM-DD>

## Workflow Type
- <bugfix | feature | refactor | architecture change | validation-only>

## Components
- <component>
- <component>

## Roles Used
- <Main Agent>
- <subagent role>
- <subagent role>

## Plan
- <initial scoped plan>

## Approval Scope
- <what the user approved>

## Execution Summary
- <major step or change>
- <major step or change>

## Handoffs
- <key handoff or finding>
- <key handoff or finding>

## Validation
- <checks run>
- <evidence level if relevant>
- <what was not validated>

## Outcome
- <result>

## Friction
- <coordination issue, ambiguity, or workflow weakness>

## Follow-Up Improvements
- <workflow or documentation improvement to consider>
```

## Relationship To Other Docs
- `AGENTS.md` defines the repo-wide operating model.
- `docs/agent_workflow.md` defines the expected execution pattern and handoff templates.
- `docs/evaluation.md` defines how evidence strength should be judged when validation is reported.
- `docs/decisions/` records durable decisions that may be referenced in a run.
- `docs/followups.md` records durable open issues or deferred work that should be revisited after the run.

Run records are different from those docs because they describe what happened in one real workflow execution.

## Follow-Up Promotion
When a run ends with unresolved issues, decide whether they should:
- stay only in the run record because they are local to that run
- be promoted to `docs/followups.md` because they matter beyond the current run

Promote issues when they are:
- durable
- likely to affect future task selection
- important enough that they should not depend on someone rereading the run record later
