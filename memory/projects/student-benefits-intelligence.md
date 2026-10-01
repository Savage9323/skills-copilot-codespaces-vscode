# Student Benefits Intelligence Memory

Last verified production state: 2026-09-28

## Identity

- Repo: Savage9323/student-benefits-intelligence
- Default branch: main
- Production: https://studentbenefitsintel.com
- Azure Container App: student-benefits-intelligence
- Azure resource group: Student-Benefits-rg

## Verified production release

- Revision: c735bafbed63698df7f2c426051f3a3ee2d60c72
- Image: ghcr.io/savage9323/student-benefits-intelligence:sha-c735baf
- Health endpoint returned healthy with the matching revision

Always query live `/api/health` before relying on this revision.

## Local environment

A deep preflight previously passed:
- Git/GitHub
- Node/pnpm
- Python
- VS Code CLI
- WSL2 Ubuntu
- Docker/Compose
- Azure CLI / Container Apps access
- NVIDIA GPU
- Ollama GPU inference
- Supabase public connectivity
- production-style Docker build/smoke

The repository quality gate previously passed lint, typecheck, tests, and production build. Re-run current gates after new code changes.

## Supabase

- Project ref: etfcbzhiiinilahaofmo
- Production MCP access should default to project-scoped read-only mode
- Prefer database/debugging/development/docs feature groups for diagnostics
- Mutations require a separately authorized write path

## Amazon Creators API

- Partner tag: studentbenefitsintel-20
- OAuth authentication succeeded previously
- Product access may return AssociateNotEligible depending on current Associates eligibility
- Keep Amazon optional/non-core
- Never let commission influence neutral benefit eligibility/ranking

## Release behavior

When hosted CI is unavailable:
- retain normal CI config
- run authoritative local quality/deep preflight
- deploy current main through version-controlled local script
- immutable GHCR image
- rollback on failed production verification
