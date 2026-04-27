# Evaluation Guide

## Purpose
This document defines how quality should be judged for this project.

It does not assume a full automated evaluation framework already exists. Instead, it provides:
- evaluation categories
- important failure modes
- practical validation guidance for current work
- direction for future evaluation infrastructure

The goal is to improve system quality with evidence where possible, and to avoid unsupported claims where evidence does not yet exist.

## Evaluation Principles
- Do not claim quality improvements that were not actually validated.
- Prefer observable evidence over intuition alone.
- When only limited validation is possible, state the limitation explicitly.
- Evaluate changes against project goals such as grounding, citations, abstain behavior, and component correctness.
- Treat manual validation, targeted checks, and automated evaluation as different strengths of evidence.

## Current Evaluation Maturity
The project currently has:
- real backend flows that can be exercised
- sample PDFs for manual end-to-end validation
- targeted runtime checks
- component-local validation guidance
- some fail-closed behavior in the application logic

The project does not yet have a mature evaluation framework for:
- retrieval relevance measurement
- grounding quality measurement across a dataset
- citation quality measurement across many examples
- abstain behavior benchmarking
- regression benchmarking across workflow changes

Because of this, many changes can currently be validated only partially.

## Evidence Levels
Use these evidence levels when describing results.

### Level 0: No Validation
No meaningful validation was run.

Example:
- code changed, but no relevant check or sample flow was run

### Level 1: Structural Validation
The system compiles, imports, or starts correctly.

Example:
- compile checks
- import checks
- backend startup checks

This is necessary but weak evidence for behavioral quality.

### Level 2: Targeted Functional Validation
A specific path or scenario was exercised successfully.

Example:
- ingesting a sample PDF succeeded
- `/ask/` returned a citation-backed answer for a sample question
- a fail-closed path returned a safe response

This is useful but narrow evidence.

### Level 3: Comparative Validation
A change was evaluated against a prior behavior or against multiple representative cases.

Example:
- before/after behavior on a small question set
- comparing retrieval results on known examples
- validating more than one representative filing or question type

This is stronger evidence, but still may not be broad enough for system-wide claims.

### Level 4: Framework-Based Evaluation
A repeatable evaluation process, dataset, or metric suite was used.

Example:
- a retrieval benchmark
- a grounding evaluation set
- a citation correctness test suite
- regression checks over a stable corpus

This is the target maturity, but it does not fully exist yet in this repo.

## Evaluation Categories

### Retrieval Quality
Questions:
- Are the retrieved chunks relevant to the question?
- Do they come from the correct filing, company, and period?
- Is irrelevant or mismatched evidence being mixed in?
- Does reranking improve or degrade the top evidence?

Common failure modes:
- correct answer exists but top chunks are irrelevant
- wrong filing or wrong company is retrieved
- relevant evidence exists but is pushed too low
- metadata mismatch causes cross-document contamination

Current acceptable validation:
- inspect retrieved sources for representative queries
- validate end-to-end behavior on sample filings
- compare before/after retrieval behavior when possible

What should not be claimed without stronger evidence:
- "retrieval is better overall"
- "precision improved system-wide"
- "recall improved across filings"

### Grounding and Hallucination Resistance
Questions:
- Does the answer stay within the retrieved evidence?
- Does it introduce unsupported claims?
- Does it preserve entity, filing, and period consistency?
- Does it abstain when support is weak?

Common failure modes:
- fluent unsupported synthesis
- answering from general world knowledge instead of filing evidence
- mixing companies, periods, or filings
- overly confident unsupported claims

Current acceptable validation:
- inspect answer plus cited sources on sample queries
- verify fail-closed behavior in weak-evidence paths
- check whether graders and workflow gates still align with intended policy

What should not be claimed without stronger evidence:
- "hallucinations are reduced overall"
- "grounding quality is improved across the system"

### Citation Quality
Questions:
- Are citation IDs valid?
- Do cited sources actually support the claims made?
- Are citations stable and useful to the user?
- Does the answer avoid inventing source references?

Common failure modes:
- invalid citation IDs
- citations that do not support the nearby claim
- citations omitted for factual claims
- duplicate or low-value citations

Current acceptable validation:
- verify citation IDs exist in the returned sources
- inspect sample answers against source chunks
- verify fail-closed behavior when citation validation fails

What should not be claimed without stronger evidence:
- "citation quality is improved overall"
- "sources are more useful across all answer types"

### Abstain and Safe-Response Behavior
Questions:
- Does the system refuse or abstain when support is insufficient?
- Does it avoid turning weak retrieval into a confident answer?
- Does it return a safe response when citations or grounding fail?

Common failure modes:
- answering when it should abstain
- weak evidence being treated as sufficient
- invalid-citation answers still being returned
- fallback behavior weakening safety guarantees

Current acceptable validation:
- test weak or mismatched questions on sample filings
- verify safe-response paths still trigger
- inspect metadata in abstained responses

What should not be claimed without stronger evidence:
- "abstain behavior is robust across all edge cases"

### Ingestion and Metadata Quality
Questions:
- Are ticker, year, and period extracted correctly?
- Are chunks created and written consistently?
- Does ingestion preserve metadata required by retrieval and answer generation?

Common failure modes:
- incorrect ticker/year/period
- missing metadata completeness signals
- chunk metadata not matching downstream expectations
- ingestion success masking poor metadata quality

Current acceptable validation:
- ingest representative sample PDFs
- inspect extracted metadata
- verify downstream retrieval still works

What should not be claimed without stronger evidence:
- "metadata extraction is reliable across all filings"

## How Agents Should Use This Doc
When making or reviewing a change:
1. Identify which evaluation categories the change affects.
2. Run the strongest realistic validation available.
3. State clearly what evidence level was achieved.
4. Avoid system-wide quality claims unless supported by stronger evidence.
5. Call out evaluation gaps explicitly.

## Validation Reporting Guidance
When reporting validation:
- say what was tested
- say what was not tested
- say how strong the evidence is
- separate observed behavior from inference
- identify next evaluation work if confidence is still limited

Good example:
- "Validated ingestion and `/ask/` on one sample 10-Q. Citation IDs were valid and the answer was grounded in returned sources. This is targeted functional validation only; broader retrieval quality is still not benchmarked."

Bad example:
- "Retrieval is better now."

## Next Evaluation Assets To Build
The next useful evaluation assets for this repo are:
- a small representative question set for sample filings
- retrieval spot-check cases with expected relevant sections
- citation correctness spot checks
- abstain-path examples
- repeatable regression checks for `/ingest/` and `/ask/`

## Relationship To Other Docs
- `docs/project_context.md` explains why evaluation matters and what quality dimensions the project values.
- `AGENTS.md` defines verification expectations at the workflow level.
- component-local `AGENTS.md` files define validation guidance for specific backend components.
- `docs/agent_workflow.md` defines how evaluation evidence should be reported in validation handoffs.

This document defines how to think about evidence and quality in the current maturity stage of the project.
