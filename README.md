# Savage Agent Skills

Central reusable Agent Skills, shared memory, and capability-routing library for OpenCode and compatible `SKILL.md` agents.

## Goals

- one source of truth for reusable project/build/operations skills
- shared persistent memory across interchangeable Ollama/OpenCode/cloud models
- controlled import of ChatGPT and other AI handoffs
- global OpenCode discovery across repositories
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
- memory-orchestrator

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
- a candidate-memory inbox
- conflict records
- an append-only merge log

Live repository, runtime, database, and provider state always outrank memory.

## Automatic shared memory

The installed `savage-auto-memory.js` global OpenCode plugin automatically:

- injects canonical portfolio/toolchain/resource/project memory into each model request
- preserves canonical memory during OpenCode compaction
- captures a redacted candidate snapshot on `session.idle`
- flags pending project memory for automatic reconciliation
- blocks direct reads of common plaintext secret/private-key files

Candidate session memory remains evidence, not canonical truth. Promotion still follows the authority rules in `memory-orchestrator`.

## Unified AI memory workflow

The memory pipeline is:

```text
AI/session
   |
   v
sanitized candidate inbox
   |
   v
memory-orchestrator
   |
   +--> verify against live/repo state
   +--> deduplicate
   +--> preserve conflicts
   |
   v
canonical project memory
   |
   v
all future models
```

A claim is never promoted merely because multiple models repeated it.

### Capture an OpenCode session

List sessions:

```bash
opencode session list
```

Capture one in sanitized form:

```bash
cd ~/src/savage-agent-skills
bash scripts/memory-capture-opencode.sh <session-id> student-benefits-intelligence
```

OpenCode supports sanitized session export, so the raw evidence is retained without intentionally carrying normal transcript secrets into the shared store.

### Import a ChatGPT or other AI handoff

Create a handoff using `memory/HANDOFF_TEMPLATE.md`, then:

```bash
cd ~/src/savage-agent-skills
bash scripts/memory-import.sh chatgpt student-benefits-intelligence < handoff.md
```

Other source examples:

```bash
bash scripts/memory-import.sh claude project-slug < handoff.md
bash scripts/memory-import.sh gemini project-slug < handoff.md
bash scripts/memory-import.sh manual project-slug < notes.md
```

The import script refuses several high-signal credential/private-key patterns.

### Review pending memory

```bash
bash scripts/memory-status.sh
bash scripts/memory-doctor.sh
```

Generate the standard consolidation prompt:

```bash
bash scripts/memory-consolidate-prompt.sh student-benefits-intelligence
```

Paste that prompt into OpenCode. The active model should use `project-memory` + `memory-orchestrator`, verify consequential/volatile facts, then update canonical memory and the merge log.

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

## Secret vault

Secrets are intentionally separate from AI memory.

Recommended long-term free setup:

- Bitwarden Password Manager for human logins/passwords
- Bitwarden Secrets Manager for API keys, database credentials, deployment tokens, and other machine secrets
- a project-scoped read-only Bitwarden machine account for OpenCode

Initialize the local non-secret configuration:

```bash
cd ~/src/savage-agent-skills
bash scripts/setup-bitwarden-secrets.sh
```

After Bitwarden account/project/machine-account setup and after loading `BWS_ACCESS_TOKEN` directly into your terminal:

```bash
bash scripts/vault-doctor.sh
```

Run a trusted command with project secrets injected without putting them in memory:

```bash
bash scripts/vault-run.sh student-benefits-intelligence -- pnpm run some-command
```

Only logical names and vault references belong in memory. Secret values never do.

See `secrets/README.md` and the `secret-vault` skill.

## Update

```bash
cd ~/src/savage-agent-skills
bash update.sh
```

## Project-specific instructions

Keep repository-specific requirements in `AGENTS.md` or project-local skills. Do not put secrets, project credentials, sensitive personal information, or volatile project state in canonical shared memory.

## Resource policy

The global default is:

local workstation -> included/student entitlements -> verified free tiers -> existing zero-incremental-cost cloud -> authorized self-hosted automation -> hosted CI credits -> paid resources.

Hosted minutes, free credits, API quotas, and student benefits are treated as shared portfolio resources across projects.
