---
name: project-memory
description: Load and maintain shared local memory for the user's software-project portfolio. Use before substantial project work, when switching models, when continuing prior work, or when the user expects the agent to remember project state, toolchain, resources, milestones, constraints, or recent verified outcomes.
---

# Project Memory

Use the shared memory layer to orient the active model before substantial project work.

## Memory locations

Global memory root:

```text
~/.config/opencode/memory/
```

Expected files:

- PORTFOLIO.md
- TOOLCHAIN.md
- RESOURCES.md
- projects/<project>.md

Project-specific repository instructions remain in the repository's own `AGENTS.md`.

## Read order

1. Identify the current repository/project.
2. Read `~/.config/opencode/memory/PORTFOLIO.md`.
3. Read `TOOLCHAIN.md` and `RESOURCES.md` when infrastructure, model, quota, or environment decisions matter.
4. Read the current project's memory file if present.
5. Read the repository's `AGENTS.md`.
6. Inspect live Git/repository/cloud/runtime state before acting.

## Authority order

When sources disagree, prefer:

1. live production/runtime/database/provider state
2. current default branch / repository contents
3. recent verified test/deployment evidence
4. project `AGENTS.md`
5. shared memory files
6. model recollection

Memory is orientation, not authority.

## Updating memory

After a meaningful verified milestone, update only durable non-secret facts such as:
- current production revision
- major architecture decision
- verified toolchain capability
- external blocker
- current milestone
- production URL
- repository/default branch
- validated deployment path

Do not store:
- passwords
- API secrets
- PATs
- private keys
- session tokens
- health/financial/personal sensitive data
- volatile values that should be queried live

Use explicit dates for last-verified status.

## Model switching

The active model may change at any time. Treat the memory files and repository state as the continuity layer. Never assume a new model retains another model's hidden context.
