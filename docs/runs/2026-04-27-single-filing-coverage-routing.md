# Run Record

## Task
- Add first-pass single-filing coverage routing for question handling in the LangGraph workflow.

## Date
- 2026-04-27

## Workflow Type
- feature

## Components
- `server/ask`
- `server/workflow`
- `server/retrieval`
- `server/llm_runtime`

## Roles Used
- Main Agent

## Plan
- Extend the existing technical analysis step with explicit first-pass coverage typing.
- Route technical questions into single-filing paths for focused lookup, retrieval-heavy, token-heavy, and computation-heavy work.
- Preserve the current technical path as `default_technical` fallback.
- Keep fail-closed answer behavior and shared post-generation safety gates intact.

## Approval Scope
- single-filing coverage types only
- conservative fallback to `default_technical`
- no cross-company or multi-filing branch logic

## Execution Summary
- Added `coverage_type` to the technical analysis contract and normalized unsupported values to `default_technical`.
- Added explicit technical routing in the workflow graph after `analyze_query`.
- Split retrieval into profile-based branch nodes with broader retrieval budgets only for supported specialized paths.
- Added context preparation for retrieval-heavy and token-heavy paths.
- Added deterministic computation preparation for supported numeric questions, with fallback to `default_technical` when extraction or computation is unsafe.
- Reset new workflow state fields in `ask` request initialization to avoid branch-state leakage across threaded requests.

## Handoffs
- No subagent handoffs were used in this run.

## Validation
- Structural checks:
- `python -m compileall -q server\ask server\workflow server\retrieval server\llm_runtime`
- imported `workflow.graph.agent_app` successfully
- Narrow targeted checks:
- Python assertions for analysis normalization, conservative fallback rules, route selection, and deterministic computation helpers
- Live validation environment:
- started an isolated backend on `127.0.0.1:8010`
- used isolated Qdrant collection `pdf_chunks_coverage_validation_20260427`
- ingested `goog-10-q-q1-2025.pdf` and `nvidia-10q.pdf` in `fast` mode
- Live `/ask/` validation results:
- `focused_lookup`: `What was NVIDIA revenue in the quarter ended October 26, 2025?`
- analyzer selected `focused_lookup`
- route resolved to `focused_lookup`
- request answered with sources and valid square-bracket citation IDs
- `retrieval_heavy`: `What evidence in NVIDIA's filing explains the quarter's revenue growth across major businesses? Cite the relevant sources.`
- analyzer selected `retrieval_heavy`
- route resolved to `retrieval_heavy`
- `prepare_retrieval_heavy_context` executed before generation
- request answered with sources and valid square-bracket citation IDs
- `token_heavy`: `Give a detailed overview of NVIDIA's results of operations in this filing, including the major revenue, margin, and profit trends.`
- analyzer selected `token_heavy`
- route resolved to `token_heavy`
- `prepare_token_heavy_context` executed before generation
- request answered with sources and valid square-bracket citation IDs
- Out-of-scope conservative fallback:
- `Compare Google Cloud revenue in this filing with Nvidia data center revenue.`
- analyzer selected `default_technical` with `scope_type=multi_company_comparison`
- route stayed on `default_technical`
- request abstained after retries with `failure_reason=answer_not_useful`
- Weak-support fail-closed path:
- `What was Apple's iPhone revenue in this filing?`
- retrieval found no support
- request abstained after retries with `failure_reason=answer_not_useful`
- Citation findings:
- representative validated live answers for focused, retrieval-heavy, and token-heavy scenarios used source IDs that were present in the returned `sources`
- exploratory Google scenarios earlier in validation exposed a separate weakness: some answered responses used non-bracket or sparse citations that still passed the current API validator because it only rejects invalid IDs, not missing required citations
- Computation-heavy live blocker:
- multiple real `/ask/` arithmetic prompts on NVIDIA were answered successfully but the analyzer consistently routed them to `focused_lookup` or `default_technical`, so the `computation_heavy` branch was not reached in live `/ask/` validation
- Strongest narrower runtime evidence for computation-heavy:
- directly invoked `retrieve_computation_heavy_node -> grade_documents_node -> prepare_computation_context_node -> generate_node` against real NVIDIA filing documents in the isolated collection
- branch produced deterministic prepared context, computed `62.4936 %`, and generated a cited answer from filing evidence
- Evidence level:
- Level 2 for live focused/retrieval-heavy/token-heavy routing, out-of-scope fallback, and fail-closed abstain behavior
- Level 2 narrower runtime evidence for computation-heavy branch internals
- still not Level 3 because this was not a comparative benchmark over a stable question set

## Outcome
- The workflow now supports explicit first-pass single-filing coverage paths with conservative fallback to the baseline technical route.
- Live validation confirmed `focused_lookup`, `retrieval_heavy`, and `token_heavy` can be reached through `/ask/` and preserve fail-closed behavior.
- Live validation did not confirm `computation_heavy` through `/ask/` because the analyzer did not emit that coverage type for tested arithmetic prompts, even though the branch works when invoked directly on real retrieved evidence.
- Durable unresolved issues from this run are also tracked in `docs/followups.md`, including the computation-heavy live-classification gap and the citation-policy gap.

## Friction
- `python -m compileall server` was noisy and non-actionable because the repo-local virtualenv is present under `server/venv`, so structural validation had to be rerun on the owned component directories only.
- The current retrieval layer does not have a filing ID filter, so "single filing" still relies on the existing metadata and user scoping assumptions.
- Alphabet/Google questions often normalize to both `GOOG` and `GOOGL`, which triggers the conservative fallback because the current routing rule rejects more than one ticker for specialized single-filing branches.
- The live analyzer did not route tested arithmetic questions into `computation_heavy`, making that branch effectively unreachable through `/ask/` in this validation pass.
- Citation validation in `ask` currently checks only that referenced square-bracket IDs exist; it does not fail answers that omit citations or use a different citation format.

## Follow-Up Improvements
- Add a small repeatable test harness for routing and fallback behavior.
- Add targeted end-to-end `/ask/` validation cases for each supported coverage type.
- Consider adding a filing-identity filter in retrieval if the product needs stronger single-filing isolation.
- Tune the analysis schema or prompt so single-filing arithmetic questions can reliably emit `computation_heavy`.
- Revisit the strict `len(query_tickers) > 1` fallback rule for known single-filing dual-class issuers such as Alphabet.
- Strengthen citation validation so grounded factual answers fail closed when required bracket citations are missing.
- Track durable unresolved items in `docs/followups.md` when they should survive beyond this run record.
