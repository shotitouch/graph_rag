# 0003 Fail-Closed Answer Policy

## Status
Accepted

## Date
2026-04-27

## Context
This project is intended to be a grounded, production-minded filing assistant rather than a generic chatbot.

That means unsupported but fluent answers are more harmful than narrower or abstaining behavior.

## Decision
Prefer fail-closed answer behavior when evidence, grounding, or citations are insufficient.

This includes preserving explicit abstain or safe-response paths when:
- generation is empty
- citations are invalid
- grounding checks fail
- answer usefulness checks fail

## Consequences
- trustworthiness is prioritized over answer coverage
- API-safe response behavior is part of correctness
- changes to workflow, ask logic, prompts, or retrieval should not silently weaken abstain behavior
