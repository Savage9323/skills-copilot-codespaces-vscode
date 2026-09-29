# Savage Agent Skills

Central reusable Agent Skills library for OpenCode and compatible `SKILL.md` agents.

## Goals

- one source of truth for reusable project/build/operations skills
- global OpenCode discovery across all repositories
- local-first execution and shared cloud-credit discipline
- specialist skills remain separate and composable
- project-specific rules stay in each repository's `AGENTS.md`

## Included skills

- local-first-project-operations
- project-plan
- build-skill-v1-1
- build-environment-compatibility
- ui-graphics-process
- web-building-execution-v2
- production-infrastructure-launch-architecture
- ai-development-security-orchestrator
- ui-build-orchestrator
- master-product-build-orchestrator

## Install for OpenCode

Clone this repository in Ubuntu/WSL:

```bash
mkdir -p ~/src
cd ~/src
git clone git@github.com:Savage9323/skills-copilot-codespaces-vscode.git savage-agent-skills
cd savage-agent-skills
./install.sh
./doctor.sh
```

If HTTPS is preferred:

```bash
git clone https://github.com/Savage9323/skills-copilot-codespaces-vscode.git savage-agent-skills
```

The installer creates symlinks in:

```text
~/.config/opencode/skills/<skill-name>
```

OpenCode can then discover each `SKILL.md` globally.

## Update

```bash
cd ~/src/savage-agent-skills
./update.sh
```

## Project-specific instructions

Keep repository-specific requirements in `AGENTS.md` or project-local skills. Do not put secrets, project credentials, or volatile project state in this central library.

## Resource policy

The global default is:

local workstation -> included/student entitlements -> verified free tiers -> existing zero-incremental-cost cloud -> authorized self-hosted automation -> hosted CI credits -> paid resources.

Hosted minutes, free credits, API quotas, and student benefits are treated as shared portfolio resources across projects.
