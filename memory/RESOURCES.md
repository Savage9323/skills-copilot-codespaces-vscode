# Shared Resource Policy

Last reviewed: 2026-10-01

Treat free tiers, student entitlements, hosted CI minutes, API quotas, cloud credits, and GPU resources as shared portfolio resources.

## Default priority

1. Local workstation
2. Included/student-entitled services
3. Verified always-free/free-tier services
4. Existing cloud resources with no meaningful incremental cost
5. Authorized self-hosted automation
6. Hosted CI/build credits
7. Paid services

## Azure

Before choosing an Azure service:
- verify current free/student offer
- verify actual subscription eligibility
- verify region/quota
- understand paid threshold
- prefer consumption/serverless and scale-to-zero where practical

Do not assume a service is free solely because it appears on a generic free-services page.

## Hosted CI

Do not shift workload from exhausted Azure DevOps minutes to GitHub Actions merely to consume another shared quota.

Use local lint/typecheck/tests/build/Docker validation whenever practical.

## Security

Do not store secrets in this memory directory.
