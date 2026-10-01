# Shared Agent Continuity

For substantial project work:

1. Use the `project-memory` skill to load durable portfolio/project context.
2. Use the `capability-router` skill to select the smallest safe tool/MCP/skill set.
3. Read the repository's own `AGENTS.md`.
4. Verify live Git/repository/runtime/cloud state before acting.
5. Treat live state as authoritative over memory.
6. Use `memory-orchestrator` when importing, reconciling, or promoting context from another AI/session.
7. Update durable project memory only after verified milestones.
8. Never store secrets or sensitive personal data in shared memory.
9. Never promote a claim solely because multiple models repeated it.

For infrastructure, credentials, quotas, deployment, or cloud-resource choices, use `local-first-project-operations`.

Treat hosted CI minutes, cloud credits, student entitlements, API quotas, and other limited resources as shared across projects.
