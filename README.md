# Savage Agent Skills

Central reusable Agent Skills, shared memory, and capability-routing library for OpenCode and compatible `SKILL.md` agents.

## Goals

- one source of truth for reusable project/build/operations skills
- shared persistent memory across interchangeable Ollama/OpenCode models
- global OpenCode discovery across all repositories
- local-first execution and shared cloud-credit discipline
- least-privilege external capabilities through MCP
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
- project-memory
- capability-router

## Shared memory

The installer links:

```text
~/.config/opencode/memory/
```

to this repository's `memory/` directory.

Memory contains:
- portfolio orientation
- local toolchain state
- shared resource policy
- per-project durable state

Live repository, runtime, database, and provider state always outrank memory.

## Install for OpenCode

Clone this repository in Ubuntu/WSL:

```bash
mkdir -p ~/src
cd ~/src
git clone git@github.com:Savage9323/skills-copilot-codespaces-vscode.git savage-agent-skills
cd savage-agent-skills
bash install.sh
bash doctor.sh
```

If HTTPS is preferred:

```bash
git clone https://github.com/Savage9323/skills-copilot-codespaces-vscode.git savage-agent-skills
```

The installer:
- links skills into `~/.config/opencode/skills/`
- links memory into `~/.config/opencode/memory/`
- installs an idempotent shared block into `~/.config/opencode/AGENTS.md`
- backs up conflicting real directories/files before replacing managed content

## MCP capability setup

### Global GitHub read-only

Uses the official GitHub MCP Docker image and the existing authenticated GitHub CLI token at runtime. The token is not written into the OpenCode config.

```bash
cd ~/src/savage-agent-skills
bash scripts/setup-github-mcp.sh
```

Default GitHub MCP toolsets:
- context
- repos
- issues
- pull_requests

The server runs in read-only mode.

### SBI Supabase read-only

Run this from the SBI repository:

```bash
cd ~/src/student-benefits-intelligence
bash ~/src/savage-agent-skills/scripts/setup-sbi-supabase-mcp.sh
```

The connection is:
- scoped to the SBI Supabase project
- read-only
- limited to database, debugging, development, and docs feature groups
- authenticated through the Supabase/OpenCode browser OAuth flow

After setup:

```bash
opencode mcp list
```

If Supabase shows that authentication is needed, start OpenCode and authenticate the server from `/mcps`.

## Update

```bash
cd ~/src/savage-agent-skills
bash update.sh
```

## Project-specific instructions

Keep repository-specific requirements in `AGENTS.md` or project-local skills. Do not put secrets, project credentials, or volatile project state in this central library.

## Resource policy

The global default is:

local workstation -> included/student entitlements -> verified free tiers -> existing zero-incremental-cost cloud -> authorized self-hosted automation -> hosted CI credits -> paid resources.

Hosted minutes, free credits, API quotas, and student benefits are treated as shared portfolio resources across projects.
