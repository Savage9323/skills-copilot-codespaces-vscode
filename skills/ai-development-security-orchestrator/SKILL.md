---
name: ai-development-security-orchestrator
description: Coordinate AI-assisted software implementation and security validation across local and cloud models, Git branches, tests, review agents, containers, and authorized security tooling. Use for AI coding workflows that need maker/checker separation, least privilege, secure review, and controlled escalation.
---

# AI Development & Security Orchestrator

## Role

Route work to the smallest effective model/tool combination while preserving independent review and security gates.

Possible model/tool families include local Ollama models and approved cloud assistants. Do not assume every provider is available.

## Workflow

1. Inspect and protect existing work.
2. Create isolated branch/worktree for non-trivial changes.
3. Route implementation to a capable coding agent/model.
4. Run automated tests and local checks.
5. Use an independent checker/reviewer for critical changes.
6. Run security checks appropriate to risk.
7. Create repair issues/findings for failures.
8. Repeat until gates pass.
9. Use PR review before production-impacting release.
10. Production deployment remains human-authorized unless already explicitly delegated and safe.

## Security boundaries

- least privilege
- no production credentials for sandboxed/local worker agents
- no secret exposure in prompts/logs
- no destructive or invasive security testing without explicit authorization
- Kali/ZAP/active testing only inside authorized scope
- dependency, secret, container, and static-analysis checks when relevant

Prefer local execution first; escalate to cloud models for difficult/high-stakes work when justified.
