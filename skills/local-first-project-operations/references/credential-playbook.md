# Credential Playbook

Classify credentials as public configuration, publishable/low-privilege, server secret, or privileged database/admin credentials.

## Rules

- never ask the user to paste a secret into chat
- never commit server/admin secrets
- never expose them to browser code
- prefer .env.local for local runtime secrets only when gitignored
- prefer ephemeral shell variables for deployment tokens
- prefer managed identity/OIDC/secret references in production
- test provider identity/authentication before debugging downstream service permissions
- rotate credentials on suspected exposure

For GHCR, test GitHub identity first, then package scope, then docker login.

For Supabase, keep secret/service-role credentials server-only and enforce RLS for exposed data.

For Azure, diagnostics may show resource names and secret-reference names, never secret values.
