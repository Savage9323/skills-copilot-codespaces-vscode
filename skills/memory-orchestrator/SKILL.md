---
name: memory-orchestrator
description: Capture, reconcile, and promote durable facts from multiple AI agents and sessions into shared model-independent project memory. Use when preserving work across OpenCode/Ollama/cloud models, importing a ChatGPT handoff, consolidating session exports, resolving conflicting memories, or updating canonical memory after verified milestones.
---

# Memory Orchestrator

The shared memory system is model-independent. Models contribute candidate memories; they do not automatically become canonical truth.

## Goals

- preserve continuity across OpenCode, Ollama, cloud models, and ChatGPT handoffs
- keep provenance for every imported memory
- prevent hallucinated or stale facts from silently becoming canonical
- keep secrets and sensitive personal data out of shared memory
- make live repository/runtime/provider state authoritative

## Memory layers

### 1. Inbox

`~/.config/opencode/memory/inbox/`

Raw or sanitized candidate material from:
- OpenCode session exports
- ChatGPT handoffs
- other agents/models
- manual notes

Inbox items are evidence, not truth.

### 2. Canonical memory

`~/.config/opencode/memory/projects/<project>.md`

Contains only durable, useful, non-secret facts that survived reconciliation.

### 3. History/conflicts

`~/.config/opencode/memory/history/`
`~/.config/opencode/memory/conflicts/`

History records promotions. Conflicts preserve unresolved contradictory claims until verified.

## Source authority

When claims conflict, prefer:

1. live production/runtime/database/provider state
2. current default branch/repository contents
3. recent verified tests/deployment evidence
4. project AGENTS.md
5. canonical memory
6. session exports / AI handoffs
7. unsupported model recollection

Never resolve a contradiction solely by majority vote among models.

## Capture rules

Every candidate should record:
- source system/model
- project slug
- capture timestamp
- session/conversation ID if available
- whether the source was sanitized
- claims/decisions/blockers/next actions
- verification evidence when available

Never store:
- passwords
- API keys
- PATs
- private keys
- session cookies/tokens
- service-role secrets
- sensitive personal/health/financial information

## Consolidation workflow

1. Load canonical project memory.
2. Read pending inbox items.
3. Deduplicate equivalent claims.
4. Classify each candidate:
   - VERIFIED_LIVE
   - VERIFIED_REPO
   - REPORTED
   - INFERRED
   - CONFLICT
   - REJECTED
5. Verify volatile facts live when practical.
6. Promote only durable facts with adequate evidence.
7. Put unresolved contradictions in `memory/conflicts/`.
8. Update `last verified` dates for promoted volatile facts.
9. Append a short entry to `memory/history/MERGELOG.md`.
10. Never delete raw inbox evidence merely because it disagrees with canonical memory.

## Cross-model behavior

All models should read the same canonical memory before substantial work.

A new model must not assume hidden context from another model. It should use:
- project-memory
- memory-orchestrator when continuity/merging is needed
- repository AGENTS.md
- live tools/MCP where available

## ChatGPT bridge

ChatGPT account memory is not assumed to be directly readable by OpenCode/Ollama.

To transfer useful ChatGPT context:
1. Ask ChatGPT for a structured memory handoff using `memory/HANDOFF_TEMPLATE.md`.
2. Import it with `scripts/memory-import.sh chatgpt <project-slug>`.
3. Consolidate it before promotion.

Do not treat a ChatGPT handoff as verified merely because it came from ChatGPT.
