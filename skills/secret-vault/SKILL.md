---
name: secret-vault
description: Use secure external vaults for passwords, API keys, tokens, database credentials, certificates, and deployment secrets while keeping secret values out of AI memory, Git, logs, prompts, and source code. Use for Bitwarden Secrets Manager, Bitwarden Password Manager, 1Password CLI, runtime secret injection, secret migration, credential rotation, and agent access design.
---

# Secret Vault

Secrets and memory are separate systems.

## Default architecture

### Human credentials
Store human login credentials, passwords, passkeys, recovery codes, and secure notes in a password manager.

Preferred free long-term option:
- Bitwarden Password Manager

### Developer / machine secrets
Store API keys, database credentials, deployment tokens, OAuth client secrets, service credentials, and machine-readable configuration in a dedicated secrets manager.

Preferred free long-term option:
- Bitwarden Secrets Manager

Supported alternate:
- 1Password + 1Password CLI

## Never store secret values in

- canonical memory
- memory inbox
- AGENTS.md
- SKILL.md
- source code
- committed .env files
- chat prompts
- screenshots
- logs
- issue/PR descriptions

Memory may store only:
- logical secret name
- owning project
- vault/provider name
- vault/project/item reference
- purpose
- rotation/verification date
- whether the secret is required

## Runtime use

Prefer secret injection over secret retrieval.

Good:
- `bws run --project-id ... -- <trusted command>`
- `op run --env-file=... -- <trusted command>`

Avoid:
- printing a secret
- `echo $SECRET`
- `printenv`
- `env`
- copying vault values into prompts
- writing resolved .env files unless a trusted tool strictly requires a temporary file

## Agent access

Agents should receive the minimum secret scope required for the current project.

Use read-only machine/service accounts where possible.

Production write/deploy credentials should be isolated from general research/coding agents.

For unattended automation, a bootstrap credential is still required. Protect it outside AI memory and scope it narrowly. A vault does not eliminate the need for a root trust credential.

## Bitwarden

Routine agent work should use `scripts/vault-run.sh`, not direct `bws secret get`.

The Bitwarden machine account should normally have read-only access to only the project(s) needed by the local agent.

## 1Password

Use secret references and `op run` / shell plugins so values are injected into a subprocess rather than copied into files or prompts.

## Credential discovery

When finding credentials already present locally:
1. never print values
2. identify only variable/key names and source locations
3. migrate values directly from trusted local source to vault without model-visible output when possible
4. replace local plaintext with a vault reference or documented runtime injection path
5. verify the target command works
6. remove obsolete plaintext only after verification
