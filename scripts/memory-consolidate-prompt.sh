#!/usr/bin/env bash
set -euo pipefail

PROJECT="${1:-}"
if [ -z "$PROJECT" ]; then
  echo "Usage: $0 <project-slug>" >&2
  exit 2
fi

cat <<EOF
Use project-memory and memory-orchestrator.

Project slug: $PROJECT

Review the canonical memory for this project and every pending inbox item that applies to it.

Do not assume any AI handoff is correct merely because it is repeated.

For each candidate claim:
1. classify it as VERIFIED_LIVE, VERIFIED_REPO, REPORTED, INFERRED, CONFLICT, or REJECTED
2. verify volatile or consequential facts with live repository/runtime/provider tools when available
3. deduplicate equivalent claims
4. preserve unresolved contradictions in memory/conflicts/
5. promote only durable, non-secret facts with adequate evidence into memory/projects/$PROJECT.md
6. update verification dates where appropriate
7. append a concise entry to memory/history/MERGELOG.md

Do not store credentials, tokens, private keys, session cookies, or sensitive personal data.
Do not delete raw inbox evidence.
At the end, report exactly what was promoted, rejected, left unresolved, and what still requires human verification.
EOF
