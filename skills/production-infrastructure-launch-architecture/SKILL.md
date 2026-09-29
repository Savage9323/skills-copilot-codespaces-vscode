---
name: production-infrastructure-launch-architecture
description: Select and design production infrastructure and launch architecture with free/student-first cost control, least privilege, auditable CI/CD, backups, monitoring, and minimal attack surface. Use when choosing hosting, databases, DNS/CDN, email, analytics, payments, CI/CD, secrets, monitoring, or deployment architecture.
---

# Production Infrastructure & Launch Architecture

Objective: maximum practical capability with minimum cost, minimum complexity, and minimum attack surface.

## Principles

- Use project-specific selection; never force one standard stack.
- Prefer local, already-included, student-entitled, and verified-free services first.
- Use the smallest practical architecture.
- Avoid duplicated services and surprise billing.
- Git is the source of truth.
- Prefer managed identity/OIDC and least privilege over stored credentials.
- Isolate production from development.
- Make CI/CD auditable.
- Document infrastructure decisions and rollback.

## Candidate ecosystem

Use only when justified: Docker, GitHub/GitHub Actions, Azure/Azure DevOps, Cloudflare, PostgreSQL/Supabase/Firebase, Resend/Zoho, PostHog/Google Analytics/Search Console, UptimeRobot or equivalent, Stripe/payment providers, 1Password/Key Vault, BrowserStack/LambdaTest, Google AI Studio/Google Cloud, app-store infrastructure, and local Ollama/GPU.

## Deliverables

Produce an architecture matrix, environment boundaries, identity/secrets model, deployment flow, data/storage plan, backup/restore plan, monitoring/alerting plan, cost/quota guardrails, release/rollback design, and unresolved human/admin dependencies.
