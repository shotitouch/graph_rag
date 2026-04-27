# Orchestrator Relay

## Purpose
This document defines the relay protocol for a two-chat setup where:
- one chat acts as the coding executor
- another chat acts as the orchestrator or reviewer
- the user relays messages between them

This is separate from the main-agent workflow in `docs/agent_workflow.md`.

## When To Use
Use this document when:
- you want executor work reviewed in a second chat
- you want help deciding what to tell the executor next
- you are testing orchestration behavior before automating it

Do not treat this as the executor's core coding workflow. It is the human relay layer around that workflow.

## Executor Request Template
Use this when sending a task to the coding executor.

```text
Task:
<what should be changed>

Mode:
Show me the plan first.

Task-Specific Constraints:
- <only constraints that are specific to this task and not already covered by repo docs>
```

For more complex tasks, the request may also ask the executor to state:
- workflow type
- affected components
- relevant docs or decisions
- delegation mode
- risks
- validation plan

## What To Relay Back For Review
Paste the executor response into the reviewer or orchestrator chat when you want:
- workflow review
- validation review
- next-step guidance
- stronger follow-up instructions

The most useful executor outputs to relay are:
- plan response
- implementation response
- validation summary
- explanation of blockers

## Reviewer Orchestrator Response Template
When reviewing executor output, the orchestrator should respond with something like:

```text
Status:
<acceptable | needs stronger validation | scope issue | workflow issue | implementation issue>

Workflow Check:
- <did it follow the expected workflow?>
- <did it state delegation mode clearly?>

Validation Check:
- <is the evidence level sufficient for this kind of change?>
- <what is still missing?>

Next Instruction To Executor:
- <exact next step to send back>
```

## Notes
- Use the lightest structure that still makes the workflow auditable.
- Do not force this protocol on trivial tasks if it adds more overhead than clarity.
- For substantial multi-agent or cross-component work, keep the structure explicit and create a run record in `docs/runs/`.

## Relationship To Other Docs
- `docs/agent_workflow.md` defines the executor or main-agent workflow and handoff structure.
- `docs/evaluation.md` defines how to judge evidence strength when reviewing executor validation.
- `docs/runs/README.md` defines how to record substantial workflow executions for later review.
