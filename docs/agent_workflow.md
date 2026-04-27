# Agent Workflow

## Purpose
This document turns the repo's agentic coding model into a repeatable execution workflow.

Use [AGENTS.md](c:/Users/Nitiw/Desktop/projects/graph_rag/AGENTS.md) for policy, ownership, and delegation rules.
Use this document for task briefs, handoffs, and validation reporting during real work.
Use [project_context.md](c:/Users/Nitiw/Desktop/projects/graph_rag/docs/project_context.md) for system intent, [evaluation.md](c:/Users/Nitiw/Desktop/projects/graph_rag/docs/evaluation.md) for evidence standards, and [decisions/README.md](c:/Users/Nitiw/Desktop/projects/graph_rag/docs/decisions/README.md) plus relevant decision records for accepted design choices.
Use [runs/README.md](c:/Users/Nitiw/Desktop/projects/graph_rag/docs/runs/README.md) when the task is substantial enough to warrant a workflow run record.
Use [followups.md](c:/Users/Nitiw/Desktop/projects/graph_rag/docs/followups.md) when planning overlaps an existing known gap or when closeout leaves durable unresolved issues.

## Operating Pattern
For non-trivial work, follow this loop:

1. Intake
2. Codebase research
3. Approach research
4. Plan
5. Approval
6. Implementation
7. Integration
8. Verification
9. Loop if needed
10. Close

## Spawn Decision
Stay single-agent when:
- the task is small and localized
- the next step is obvious
- multiple components are not meaningfully involved
- parallel work would add coordination overhead without saving time

Spawn subagents when:
- the task is large enough to benefit from separation
- a component boundary is clear
- research can run in parallel with other work
- validation can happen independently after implementation

Avoid spawning when:
- the task is still vague
- ownership boundaries are unclear
- multiple workers would need the same files
- the task depends on shared contracts that are still moving

## Main Agent Checklist
Before delegation:
- identify the workflow step
- define the concrete problem
- identify the owned component or components
- read any component-local `AGENTS.md` files for the components involved
- read any relevant records in `docs/decisions/` when the task touches established architectural or contract choices
- check `docs/followups.md` when the task may overlap a known gap, deferred item, or active follow-up
- decide whether this is optimization or redesign
- state whether subagents will be used for this task or whether it will remain a single main-agent run
- note risks and approval boundaries

After delegation:
- review subagent outputs
- resolve contract mismatches
- integrate cross-component changes
- ensure validation results are explicit
- use `docs/evaluation.md` when the task affects behavior-sensitive quality areas such as retrieval, grounding, citations, abstain behavior, or metadata quality
- create or update a run record for substantial multi-agent or cross-component work
- triage durable unresolved issues into `docs/followups.md` and close or update overlapping follow-ups when the task resolves them

## Task Brief Template
Use this when assigning work to a subagent.

```md
Task Name: <concrete task name>
Workflow Step: <codebase research | approach research | implementation | verification | integration>
Role: <Architecture Explorer | Approach Researcher | Ask Worker | Workflow Worker | Retrieval Worker | Ingestion Worker | Filing Metadata Worker | LLM Runtime Worker | Validation Explorer>
Owned Scope: <component directory or explicit file scope>
Objective: <specific problem to solve>
Context: <current behavior or relevant repo facts>
Constraints:
- <behavioral constraints>
- <follow local component guidance if an `AGENTS.md` exists in the owned scope>
- <do not touch files outside scope>
- <preserve or change specific contracts>
Success Criteria:
- <observable outcome 1>
- <observable outcome 2>
Deliverables:
- <what the subagent should return>
```

## Research Output Template
Use this for codebase or approach research.

```md
Summary:
- <short answer>

Findings:
- <current behavior or recommended pattern>
- <current behavior or recommended pattern>

Affected Areas:
- <component or files>

Risks:
- <risk or ambiguity>

Recommendation:
- <preferred next step>
```

## Implementation Output Template
Use this when a worker completes a code change.

```md
Changes Made:
- <what changed>
- <what changed>

Assumptions:
- <assumption>

External Contracts or Data Shapes Relied On:
- <API field, schema, metadata key, response shape, or function contract>

Checks Run:
- <command or check>

Open Risks:
- <risk, follow-up, or unresolved question>
```

## Delegation Visibility Rule
Before implementation, explicitly state one of the following:

- `Subagents used`
  - list each role
  - list each owned scope
  - summarize the key handoff from each subagent

- `Single main-agent run`
  - state that no subagents are being used
  - briefly explain why the task is being handled locally

## Validation Report Template
Use this for verification results.

```md
Evaluation Categories:
- <retrieval | grounding | citations | abstain behavior | ingestion/metadata | other>

Evidence Level:
- <Level 0 | Level 1 | Level 2 | Level 3 | Level 4>

Checks Passed:
- <check>

Checks Failed:
- <check and short failure note>

Checks Not Run:
- <check and reason>

Residual Risk:
- <remaining uncertainty>
```

## Integration Note Template
Use this when the main agent resolves cross-component work.

```md
Components Integrated:
- <component>
- <component>

Contract Decisions:
- <decision>

Conflicts Resolved:
- <conflict and resolution>

Final Verification Needed:
- <follow-up checks>

Decision Records Consulted:
- <decision id if relevant>
```

## Common Task Flows

### Bugfix
1. Codebase research traces the failing path.
2. Approach research is optional unless the fix pattern is unclear.
3. Main agent scopes the fix and gets approval.
4. One component worker implements the fix.
5. Validation explorer checks the affected behavior.
6. Main agent closes with risk summary.

### Feature
1. Codebase research maps affected components.
2. Approach research checks framework or library guidance.
3. Main agent decides whether the feature is incremental or architectural.
4. Approved component workers implement within owned scopes.
5. Main agent integrates.
6. Validation explorer verifies the feature path.

### Refactor
1. Codebase research identifies the current dependency surface.
2. Main agent defines what must stay behaviorally identical.
3. Workers refactor within component boundaries.
4. Validation explorer focuses on regression detection.

### Cross-Component Change
1. Codebase research identifies all touched components.
2. Approach research confirms the contract strategy.
3. Main agent splits the work into component-owned tasks.
4. Workers implement in parallel only if interfaces are stable.
5. Main agent handles integration and shared-surface decisions.
6. Validation explorer checks the end-to-end path and reports evidence strength using `docs/evaluation.md`.

## Task Naming Guide
Good task names:
- Trace current 10-Q metadata extraction flow
- Find the recommended FastAPI pattern for this response behavior
- Add quarter normalization fallback in filing metadata extraction
- Validate citation response handling after retrieval changes

Avoid vague task names:
- Research
- Implementation
- Improve metadata
- Fix system

## Review Rule
The user should approve plan and scope before code changes begin.
Subagents may implement within that approved scope.
If scope or approach changes materially, pause and get approval again.

## Follow-Up Triage Rule
At closeout:
- keep run-specific notes in the run record
- promote durable product or engineering gaps into `docs/followups.md`
- update existing follow-ups when a task changes their status or priority

## Expected Main-Agent Plan Response
For non-trivial tasks, the main agent should respond in a structure like:

```text
Workflow Type:
<bugfix | feature | refactor | architecture change | validation-only>

Affected Components:
- <component>
- <component>

Relevant Docs or Decisions:
- <doc or decision id>
- <doc or decision id>

Delegation Mode:
<single main-agent run | subagents used>

Plan:
- <step>
- <step>

Risks:
- <risk>

Validation Plan:
- <check>
- <check>
```

### Expected Main-Agent Implementation Response
After implementation or validation, the main agent should report in a structure like:

```text
Delegation Mode Used:
<single main-agent run | subagents used>

Files Changed:
- <file>
- <file>

Change Summary:
- <what changed>
- <what changed>

Checks Passed:
- <check>

Checks Failed:
- <check and failure note>

Checks Not Run:
- <check and reason>

Evidence Level:
<Level 0 | Level 1 | Level 2 | Level 3 | Level 4>

Open Risks:
- <risk or follow-up item>
```

If subagents were used, the executor should also report:
- roles used
- owned scopes
- key handoff summaries
