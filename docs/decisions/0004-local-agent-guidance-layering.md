# 0004 Local Agent Guidance Layering

## Status
Accepted

## Date
2026-04-27

## Context
Repo-wide agent rules are necessary, but they are not sufficient for components with specialized constraints such as workflow orchestration, retrieval readiness, ingestion metadata, or API fail-closed behavior.

Putting every local constraint into the root `AGENTS.md` would make the global file too broad and repetitive.

## Decision
Keep the root `AGENTS.md` as the repo-wide operating policy, and add component-local `AGENTS.md` files where specialized guidance is needed.

Local component guidance should refine, not replace, the root rules.

## Consequences
- global policy stays centralized
- component-specific constraints remain close to the code they govern
- agents should read local guidance when working inside a component
- duplication should be minimized by keeping workflow, evaluation, and project-intent rules in their dedicated docs
