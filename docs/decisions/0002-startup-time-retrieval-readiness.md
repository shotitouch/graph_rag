# 0002 Startup-Time Retrieval Readiness

## Status
Accepted

## Date
2026-04-27

## Context
The backend previously initialized Qdrant-sensitive retrieval objects too early, which made imports brittle and caused failures when the retrieval backend was unavailable during module import.

At the same time, fully deferring retrieval setup until the first user request would have shifted readiness cost and failure discovery into the request path.

## Decision
Avoid import-time network side effects for retrieval initialization.

Keep retrieval readiness at startup time by:
- creating Qdrant-sensitive objects lazily
- ensuring Qdrant collection readiness during FastAPI startup
- initializing the retriever during startup rather than on first user request

## Consequences
- backend imports are safer
- startup still fails early if retrieval infrastructure is unavailable
- user-facing request latency is not increased by first-request initialization
- retrieval component changes should preserve this separation between import time and startup time
