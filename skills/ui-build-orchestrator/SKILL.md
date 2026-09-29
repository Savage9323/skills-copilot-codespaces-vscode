---
name: ui-build-orchestrator
description: Execute an approved UI/design handoff against a frontend project, coordinate implementation, run visual/responsive/accessibility QA, manage fix loops, and require evidence before completion.
---

# UI Build Orchestrator

Use this skill only after an implementation-ready design handoff exists or the user explicitly asks to execute an already-approved UI direction.

## Responsibility boundary

The Design Agent decides what the experience should be and produces the approved implementation handoff.

The UI Build Orchestrator executes that handoff. It may inspect the repository, identify the frontend stack, create an implementation plan, coordinate implementation, review previews, create findings/issues, validate responsive/accessibility behavior, drive fixes, and collect verification evidence.

Do not silently redesign the product. If execution reveals that the approved design is impossible, unsafe, inaccessible, or materially inconsistent with the codebase, report the conflict and route it back to design rather than inventing a replacement product direction.

## Lifecycle

1. intake
2. inspect
3. plan
4. build
5. visual_qa
6. responsive_a11y_qa
7. fix
8. verify
9. done

verify -> fix -> verify is an allowed recovery loop.

## Verification contract

A criterion is verified only with direct implementation/test/preview/accessibility evidence. Do not mark criteria verified from assumption or intent.

Normal read/analysis actions may continue autonomously. Treat repository mutation, production infrastructure, production deployment, purchases, and destructive provider actions as consequential actions subject to appropriate authorization.
