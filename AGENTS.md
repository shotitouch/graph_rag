# AGENTS.md

## Purpose
This repo uses an agentic coding workflow for AI-assisted development.

## Approval Rule
If a task requires code changes, the agent must first present the implementation plan, affected components, and expected scope to the user, and get approval before editing code.

After approval, the agent may implement within that approved scope. If the scope or approach changes materially, the agent must ask for approval again.

## Working Style
- Prefer small, reviewable changes.
- Understand the current code path before proposing edits.
- Do not revert unrelated local changes.
- Keep changes aligned with the repo's existing architecture unless a redesign is explicitly approved.
- Respect accepted architectural decisions recorded in `docs/decisions/` unless the task explicitly revisits them.

## Workflow Loop
For non-trivial tasks, follow this iterative workflow:

1. Intake
Classify the request as a bugfix, feature, refactor, architecture change, or verification-only task.

2. Codebase Research
Inspect the current implementation to understand where the behavior lives, which components are involved, and what constraints already exist.

3. Approach Research
When needed, research the best implementation approach using official docs, framework guidance, library guidance, or established patterns.

4. Plan
Define the concrete problem to solve, the affected components, the intended approach, and any expected risks.

5. Approval
Follow the Approval Rule before making code changes.

6. Implementation
Make changes within the approved scope.

7. Integration
Resolve cross-component issues and ensure the final behavior is coherent.

8. Verification
Run the narrowest relevant checks and record what passed, failed, or was not run.

9. Loop
If verification fails, assumptions change, or the chosen approach proves insufficient, return to the appropriate earlier step and iterate.

10. Close
Summarize what changed, what was verified, and any remaining risks.
For substantial multi-agent or cross-component work, create or update a run record in `docs/runs/`.
If durable unresolved issues or deferred work remain, add or update entries in `docs/followups.md`.

## Core Roles

### Main Agent
- Owns planning, user communication, delegation, cross-component integration, and final review.
- Combines codebase research and approach research into an implementation plan.
- Assigns bounded work to subagents only after the task is sufficiently scoped.
- Presents the plan for approval before implementation begins.
- Handles shared contracts and integration work unless explicitly delegated.
- Before implementation, state whether the task will use subagents or remain a single main-agent run. If subagents are used, report their roles and scopes. If not, state that explicitly and briefly why.

### Architecture Explorer
- Focuses on codebase research.
- Identifies where the relevant behavior lives, which components are involved, and what constraints or ownership boundaries apply.
- Does not make implementation decisions by itself.

### Approach Researcher
- Focuses on solution research.
- Investigates official docs, framework guidance, library guidance, and established implementation patterns when needed.
- Helps determine whether the task should optimize the current approach or adopt a new one.

### Validation Explorer
- Focuses on verification, regression detection, and validation of affected behavior.
- Runs the narrowest relevant checks and reports what passed, failed, or was not run.
- Highlights regressions, integration gaps, and residual risks.
- Does not sign off on correctness alone; final review remains with the main agent.

## Component Roles
When a component directory contains its own `AGENTS.md`, follow the repo-wide rules here first and then apply the local component guidance for work inside that component.

### Ask Worker
- Owns `server/ask/**`.
- Handles request schemas, route behavior, response shaping, and API-facing answer behavior.
- Should not implement workflow logic, retrieval logic, or ingestion logic inside this component.

### Workflow Worker
- Owns `server/workflow/**`.
- Handles graph assembly, state transitions, nodes, edges, retries, and workflow-local orchestration behavior.
- Should not own HTTP transport behavior or retrieval engine internals.

### Retrieval Worker
- Owns `server/retrieval/**`.
- Handles retrieval logic, reranking, metadata filtering, and retrieval-specific contracts.
- Should not own workflow orchestration or ingest pipeline behavior.

### Ingestion Worker
- Owns `server/ingestion/**`.
- Handles upload flow, chunking orchestration, parsing mode selection, and ingest pipeline behavior.
- Should not own question-answering logic.

### Filing Metadata Worker
- Owns `server/filing_metadata/**`.
- Handles metadata extraction, normalization, and filing identity rules.
- Should not own ingestion transport behavior or retrieval engine behavior.

### LLM Runtime Worker
- Owns `server/llm_runtime/**`.
- Handles model client setup, prompts, chains, and structured output wiring.
- Should be used carefully because prompt or schema changes here may affect multiple components.

### Shared Surface
- `server/shared/**` is not a normal component worker ownership area.
- Shared files should stay small and stable.
- Changes to shared contracts, configuration, or logging should usually be handled by the main agent during integration unless explicitly delegated.

## Delegation Rules
- Use subagents only for bounded tasks with a clear objective and a clear ownership scope.
- A subagent task should belong to a workflow step, but the task name should describe the concrete work to be done.
- Do not delegate vague mandates such as "improve this" without first defining the specific problem, target, or failure mode.
- Do not assign overlapping write scopes to multiple workers in parallel.
- If a task spans multiple components, split it into separate component-owned tasks and let the main agent handle integration.
- If a task requires changes in `server/shared/**`, the main agent should usually make or coordinate those changes during integration.
- If the scope expands materially during implementation, follow the Approval Rule again before continuing.

## Parallel Work
- Parallel work is appropriate only when tasks have non-overlapping write scopes and stable interfaces.
- Prefer parallel research over parallel implementation when the task is still ambiguous.
- Prefer serialized implementation when changes affect shared contracts, prompts, schemas, or other cross-component behavior.
- If there is doubt about task overlap or interface stability, serialize the work.

## Subagent Outputs
Each subagent should report:
- what it changed or found
- assumptions it made
- external contracts or data shapes it depends on
- checks it ran
- open risks or follow-up items

## Verification Expectations
- Run the narrowest relevant checks for the components that changed.
- Do not claim verification that was not actually run.
- If verification could not be run, say so explicitly and explain why.
- Prefer targeted validation before broad full-repo checks unless the change affects shared behavior or cross-component contracts.
- Use `docs/evaluation.md` to judge evidence strength for behavior-sensitive changes.
- Do not make broad quality claims from weak evidence levels.

### Verification Examples
- Backend logic changes: run relevant backend tests, syntax checks, or targeted API validation.
- Frontend changes: run relevant lint, type-check, build, or UI-specific checks.
- Cross-component changes: validate the affected integration path, not just the individual files.
- Refactors without intended behavior change: run checks that can detect regressions in the touched area.
