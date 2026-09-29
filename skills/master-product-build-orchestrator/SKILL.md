---
name: master-product-build-orchestrator
description: Coordinate the full product build lifecycle by routing work to planning, implementation, UI, compatibility, security, infrastructure, and local-operations specialist skills. Use for substantial end-to-end product builds or recoveries spanning multiple engineering disciplines.
---

# Master Product Build Orchestrator

This is the top-level coordinator. Specialist skills remain separate and separately callable.

## Lifecycle

Intake -> Protect -> Inspect -> Architect -> Route -> Design/UI -> Implement -> Secure -> Test -> Compatibility -> Release -> Production Verify -> Monitor -> Handoff.

Equivalent gate framing:
Intake -> Protect -> Architect -> Route -> UI/UX Gate -> Implement -> Compatibility Gate -> Security Gate -> Quality Gate -> Release Gate -> Post-Launch Observe.

## Specialist routing

Use as needed:
- project-plan
- build-skill-v1-1
- local-first-project-operations
- web-building-execution-v2
- ui-graphics-process
- ui-build-orchestrator
- build-environment-compatibility
- ai-development-security-orchestrator
- production-infrastructure-launch-architecture

Do not copy specialist instructions into the master. Load the specialist when its domain becomes active.

## Evidence gates

Use PASS / FAIL / UNTESTED.

Critical/high-risk work requires maker/checker separation.

Parallel edits should use separate branches/worktrees when practical.

## Mandatory stop conditions

Stop for:
- risk of overwriting unrecoverable work
- missing secret/credential/permission/legal authorization
- unresolved critical security issue
- build/test failure blocking a claimed target
- ambiguous production target affecting live users/data
- unauthorized production or third-party changes

Otherwise continue autonomously from the latest verified checkpoint.

## Completion states

BUILT -> TESTED -> VERIFIED -> DEPLOYED -> PRODUCTION_VERIFIED.

Never collapse these states into "done" without evidence.
