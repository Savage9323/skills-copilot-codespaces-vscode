# Savage Agent Secret Vault

This directory contains documentation and non-secret registry templates only.

**Secret values never belong in this repository or shared memory.**

## Recommended provider

Bitwarden:
- Password Manager for human logins
- Secrets Manager for developer/machine secrets
- one read-only machine account for the local OpenCode agent where practical

## Runtime pattern

```text
OpenCode agent
    |
    | logical project name only
    v
vault-run.sh
    |
    | scoped machine credential
    v
Bitwarden Secrets Manager
    |
    | injects environment for child process
    v
trusted command
```

The model should not receive the secret value.

## Local non-secret configuration

Create:

```text
~/.config/savage-agent/vault-projects.json
```

Example:

```json
{
  "provider": "bitwarden",
  "projects": {
    "student-benefits-intelligence": {
      "project_id": "BITWARDEN_PROJECT_UUID"
    },
    "juniors-product-co": {
      "project_id": "BITWARDEN_PROJECT_UUID"
    },
    "nextgenbabyplay": {
      "project_id": "BITWARDEN_PROJECT_UUID"
    }
  }
}
```

Bitwarden project UUIDs are identifiers, not secret values. Keep the file private anyway.

## Bootstrap credential

Bitwarden Secrets Manager CLI uses a machine-account access token.

Do not:
- commit it
- put it in memory
- put it in AGENTS.md
- paste it into an AI prompt

For initial setup, load it into the shell as `BWS_ACCESS_TOKEN` without echoing it.

A later hardening step may place this bootstrap token behind an OS credential broker. Even then, keep machine-account permissions read-only and project-scoped.

## Secret naming

Use stable environment-variable-compatible keys, for example:

```text
SBI_SUPABASE_SERVICE_ROLE_KEY
SBI_AZURE_CLIENT_ID
JPC_CLOUDFLARE_API_TOKEN
NGP_AMAZON_PARTNER_TAG
```

Do not use ambiguous names such as `API_KEY`.
