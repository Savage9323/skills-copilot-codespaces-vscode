# Shared Memory Schema

This repository contains curated/historical Markdown memory and sanitized exports.
The live OpenCode plugin now reads canonical global/project Markdown from
~/.savagedev/memory/, not the older ~/.config/opencode/memory symlink.
Do not treat this repository's legacy memory/projects/<slug>.md as an
additional writable authoritative store; reconcile useful entries against
live state before copying them into the new canonical root.

Automatic M2 candidates are privately staged under
~/.local/share/savage-agent-memory/candidates/, never directly injected
as canonical memory. See M2_LIFECYCLE.md.

## Canonical project memory

Path:

`memory/projects/<slug>.md`

Recommended sections:

- Identity
- Purpose
- Repository / production endpoints
- Architecture
- Operating constraints
- Current milestone
- Verified deployment/runtime state
- External blockers
- Durable decisions
- Last verified date

Canonical memory must stay concise. It is not a transcript archive.

## Inbox naming

`memory/inbox/YYYYMMDDTHHMMSSZ__<source>__<project>__<id>.<ext>`

Examples:

- `20261001T091500Z__opencode__student-benefits-intelligence__ses_abcd.json`
- `20261001T092000Z__chatgpt__student-benefits-intelligence__manual.md`

## Provenance states

- VERIFIED_LIVE — checked against current production/runtime/provider
- VERIFIED_REPO — checked against current repository/default branch
- REPORTED — stated by an AI/user/source but not independently checked
- INFERRED — derived from evidence but not directly observed
- CONFLICT — disagrees with another source and is unresolved
- REJECTED — stale, false, unsafe, secret, or not useful as durable memory

## Volatility

Facts such as revisions, quotas, prices, eligibility, service status, schedules, and deployment state must carry a verification date and should be re-checked before consequential use.

## Sensitive-data rule

Do not promote secrets or sensitive personal data. Sanitized session exports are still treated as untrusted evidence and must be reviewed before promotion.


## Secret references

Canonical memory may record that a secret exists and how to locate it without containing the value.

Allowed examples:

- logical key name: `SBI_SUPABASE_SERVICE_ROLE_KEY`
- provider: `bitwarden`
- owning project: `student-benefits-intelligence`
- vault/project/item reference or UUID
- purpose
- last rotation/verification date

Never store the secret value, recovery code, master password, machine-account access token, or private key material in memory.
