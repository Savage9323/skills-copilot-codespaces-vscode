---
name: capability-router
description: Select the smallest safe set of tools, MCP servers, plugins, local CLIs, and specialist skills needed for a software task. Use when deciding whether to use GitHub, Supabase, Azure, Docker, web/docs, Hugging Face, local models, analytics, deployment tools, or other integrations without overloading model context or granting excessive privilege.
---

# Capability Router

Select capabilities by task, not by convenience.

## Principles

1. Use the fewest tools needed.
2. Prefer read-only access for discovery and diagnosis.
3. Elevate to write access only when the task requires mutation and authorization exists.
4. Do not expose every MCP server to every task; tool schemas consume context.
5. Prefer local tools for local state and current vendor MCP/API tools for remote state.
6. Keep production mutation separate from development and diagnostics.
7. Reuse specialist skills rather than recreating their procedures.

## Default profiles

### Core
- filesystem/repository tools
- git
- terminal
- project-memory
- relevant specialist skills

### Repository research
- GitHub read-only MCP
- project-memory
- local git

### Database diagnostics
- project-scoped read-only Supabase MCP
- Supabase skill
- project-memory

### Infrastructure diagnostics
- local-first-project-operations
- Azure CLI
- Docker
- provider docs

### Deployment
- version-controlled deploy scripts
- registry auth
- Azure/provider CLI
- GitHub only if release metadata/PR state is required

### Model evaluation
- Ollama
- NVIDIA tooling
- Hugging Face skills/tools when needed

## Permission escalation

Before changing remote state, determine:
- target
- exact mutation
- rollback path
- whether the current credential scope is necessary
- whether a read-only diagnostic can answer the question first

Keep production database mutation, production deployment, destructive cloud actions, package deletion, and account/billing changes behind explicit authorization or existing project-specific delegation.

## Context budget

If the local model has a constrained context window:
- load only relevant skills
- enable only relevant MCP servers/toolsets
- prefer summaries over dumping full histories
- use project memory for durable context instead of giant prompts
