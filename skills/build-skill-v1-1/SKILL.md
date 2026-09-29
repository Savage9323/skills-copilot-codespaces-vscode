---
name: build-skill-v1-1
description: Execute software builds through a gated lifecycle from intake to production verification. Use for end-to-end implementation where work must be protected, architected, routed, implemented, tested, secured, released, and verified with evidence.
---

# Build Skill v1.1

Lifecycle:

Intake -> Protect -> Architect -> Route -> UI/UX -> Implement -> Compatibility -> Security -> Quality -> Release -> Post-Launch.

Completion states:

BUILT -> TESTED -> VERIFIED -> DEPLOYED -> PRODUCTION_VERIFIED.

## Rules

- Inspect existing work before changing it.
- Git is the source of truth.
- Preserve recoverable checkpoints and isolate non-trivial changes on branches/worktrees.
- Prefer local/existing/free tools first.
- Route specialist work to dedicated skills instead of duplicating their instructions.
- Require maker/checker review for high-risk or production-impacting changes.
- Never mark a gate passed without evidence.
- Failures create a repair loop and return to the relevant gate.
- Stop only for genuine owner-only blockers such as credentials, legal acceptance, unavailable permissions, or unresolved critical security risk.

## Required gates

- build/install reproducibility
- automated tests
- security
- compatibility where applicable
- quality
- release/rollback
- production verification

Report PASS / FAIL / UNTESTED honestly.
