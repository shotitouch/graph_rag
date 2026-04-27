# Project Context

## Purpose
This repo is a full-stack agentic RAG system for grounded question answering over uploaded PDF documents, with a current emphasis on SEC 10-Q style financial filings.

The system is intended to behave like a production-minded assistant rather than a generic chatbot. It should prefer grounded, traceable, source-backed behavior over fluent but weakly supported answers.

## Product Goal
The primary goal is to help a user upload a filing, ask questions about it, and receive answers that are:

- grounded in retrieved evidence
- citation-aware
- safe when evidence is weak
- explicit about uncertainty or missing support

The system should fail closed when it cannot justify an answer from the available document context.

## Primary User Experience Goals
- Answer questions using uploaded filing content, not generic world knowledge when document grounding is expected.
- Return source-aware answers with stable citations.
- Avoid unsupported synthesis when retrieval is weak or mismatched.
- Preserve a fast enough workflow for upload and question answering without hiding correctness tradeoffs.
- Improve answer quality and safety in ways that can be evaluated, not only described.

## System Boundaries
This system currently focuses on:
- uploaded PDF documents
- filing-oriented retrieval and answering
- evidence-backed responses through retrieval, grading, and citations

This system is not designed to be:
- a general-purpose financial advisor
- a forecasting or speculative analysis engine
- a broad document platform optimized equally for every PDF domain

## Non-Goals
- This system is not intended to make forecasts or speculative claims from filings unless that behavior is explicitly designed.
- It is not intended to optimize for the most verbose or most conversational answer style at the expense of grounding.
- It is not intended to weaken evidence requirements to improve answer coverage.
- It is not intended to treat all architectural shortcuts as acceptable if they reduce trustworthiness.

## Current System Shape
The backend is organized by component:

- `server/ask/`
  API-facing question-answering request and response handling

- `server/workflow/`
  LangGraph orchestration, routing, retries, grading, and state transitions

- `server/retrieval/`
  Qdrant-backed retrieval and reranking

- `server/ingestion/`
  PDF ingestion, chunking, metadata handoff, and vectorstore writes

- `server/filing_metadata/`
  10-Q metadata extraction and normalization

- `server/llm_runtime/`
  model client setup, prompts, and LLM chains

- `server/shared/`
  stable shared configuration, logging, and cross-component types

The frontend provides upload and chat interfaces against the backend API.

## Architectural Intent
This system separates concerns on purpose:

- `ask` owns API transport and final response policy
- `workflow` owns orchestration decisions
- `retrieval` owns evidence access
- `ingestion` owns document indexing
- `filing_metadata` owns canonical filing identity extraction
- `llm_runtime` owns prompt and model wiring
- `shared` should remain small and stable

This separation exists to improve maintainability, reduce overlap during agentic coding, and make component ownership clear.

## Key Invariants
- Grounded answers are more important than fluent unsupported answers.
- Citation behavior is part of correctness, not just presentation.
- Retrieval metadata is part of correctness, not just indexing detail.
- API safe-response behavior should remain explicit and fail closed.
- Import-time network side effects should be avoided when possible.
- Cross-component contracts should remain explicit and stable.
- Component-local logic should stay inside its owned boundary unless there is a clear integration reason not to.
- Changes to retrieval, workflow, or answer policy should be judged by observable evaluation outcomes when possible.

## Decision Heuristics
When making changes, prefer:
- improving the current approach before replacing it entirely
- explicit orchestration over hidden behavior
- smaller, reviewable changes over broad refactors
- local component changes over shared-surface churn
- targeted validation over assumed correctness

A change is likely aligned if it improves:
- grounding quality
- citation reliability
- evidence validation
- component clarity
- operational safety
- testability or verification

A change is likely misaligned if it:
- weakens evidence requirements
- hides important decisions in prompts alone
- spreads logic across unrelated components
- increases shared coupling without a clear payoff
- improves convenience at the cost of trustworthiness

## Evaluation Direction
The system should move toward stronger evaluation in areas such as:
- retrieval relevance and ranking quality
- grounding and hallucination resistance
- citation correctness and usefulness
- abstain behavior in weak-evidence cases
- end-to-end regression detection for workflow changes

Evaluation should become a regular part of system improvement, not only ad hoc manual inspection.

## Current Maturity
The system already supports:
- PDF ingestion
- filing metadata extraction
- vector retrieval
- reranking
- graph-based QA orchestration
- source-aware answers
- abstain behavior in weak cases

The system is still evolving in areas such as:
- deeper filing-scope validation
- more mature answerability gating
- richer retrieval planning by question type
- stronger evaluation for retrieval, grounding, citations, and regressions
- stronger component-local documentation and testing conventions

## Relationship To Other Docs
- `README.md` explains the repo and stack at a high level.
- `AGENTS.md` defines the agentic coding operating model.
- `docs/agent_workflow.md` defines execution templates for multi-agent work.
- `docs/evaluation.md` defines the current evidence model and evaluation expectations for judging system quality.
- `docs/decisions/` records accepted architectural and workflow decisions that future work should respect unless intentionally revised.
- `docs/followups.md` records active known gaps, deferred work, and durable issues that should influence future task selection.
- `ideal_system.md` captures aspirational system-design thinking and future-state ideas.

This file is the stable reference for what the project is, what it values, and how to judge whether a change fits its intent.
