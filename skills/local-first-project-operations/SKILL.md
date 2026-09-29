---
name: local-first-project-operations
description: Audit, configure, validate, and release software projects with a local-first, free-tier-aware operations workflow. Use when setting up developer environments, choosing cloud resources, managing .env credentials, validating Docker/Azure/Supabase/Ollama/GitHub access, handling exhausted CI minutes, preparing releases, or deploying safely with rollback while minimizing shared cloud-credit usage across projects.
---

# Local-First Project Operations

Default flow:

inspect -> establish baseline -> classify risks -> fix locally -> validate locally -> use cloud only where justified -> release safely -> verify production -> record blockers and next actions.

## Core rules

1. Prefer local execution before hosted execution.
2. Treat hosted CI minutes, cloud credits, free-tier quotas, student entitlements, and API quotas as shared resources across all projects.
3. Do not spend hosted minutes merely to repeat checks already passed locally unless independent hosted execution adds real value.
4. Prefer existing/included and verified free tiers before paid infrastructure.
5. Verify current vendor documentation for quotas, authentication, pricing, and eligibility.
6. Never expose secrets in chat, logs, screenshots, Git, shell history, or browser-facing variables.
7. Never merge or deploy code that failed a relevant quality gate.
8. Keep optional external integrations non-critical.
9. Favor simple modular architecture over premature microservices.
10. Keep rollback available.

## Resource order

local workstation -> included/student services -> verified free tiers -> existing zero-incremental-cost cloud -> authorized self-hosted automation -> hosted CI -> paid services.

Do not shift work from exhausted Azure DevOps minutes to GitHub-hosted minutes merely to consume another shared quota.

## Local preflight

Check Git, repository state, runtime/package manager, Python when needed, VS Code CLI, WSL2/Linux, Docker/Compose, Azure CLI/auth/resource access, NVIDIA GPU, Ollama/model inventory/GPU inference, runtime env presence, database/public API connectivity, and configured external APIs.

Emit PASS / WARN / FAIL without secret values.

## Release gate

Before release run the authoritative local gate: data validation where applicable, lint, typecheck, tests, production build, Docker build/smoke, critical-route checks, and deep preflight.

## Azure/CI rule

If hosted CI fails before checkout because minutes are exhausted, classify it as quota failure rather than code failure. Do not retry repeatedly or spill into another project's shared hosted quota. Use local gates and controlled manual deployment when appropriate.

## Safe deployment

Sync default branch, verify intended commit and clean tree, verify registry/cloud auth, build an immutable SHA-tagged image, smoke-test locally, push, record prior production image, deploy, verify origin/custom domain/revision, run integrity checks, and roll back automatically on verification failure.

## Stop conditions

Continue until a genuine human-only step is required: interactive login/MFA, obtaining a secret, accepting legal/financial terms, or changing permissions the user does not control.
