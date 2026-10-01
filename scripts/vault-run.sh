#!/usr/bin/env bash
set -euo pipefail

CONFIG="${SAVAGE_VAULT_CONFIG:-$HOME/.config/savage-agent/vault-projects.json}"

usage() {
  echo "Usage: $0 <project-slug> -- <trusted command> [args...]" >&2
}

[ "$#" -ge 3 ] || { usage; exit 2; }
PROJECT="$1"
shift
[ "${1:-}" = "--" ] || { usage; exit 2; }
shift

command -v bws >/dev/null 2>&1 || {
  echo "Bitwarden Secrets Manager CLI (bws) is not installed." >&2
  exit 1
}

[ -n "${BWS_ACCESS_TOKEN:-}" ] || {
  echo "BWS_ACCESS_TOKEN is not loaded in this shell." >&2
  echo "Load the machine-account token outside AI-visible prompts, then retry." >&2
  exit 1
}

[ -f "$CONFIG" ] || {
  echo "Vault project config not found: $CONFIG" >&2
  echo "Copy secrets/vault-projects.example.json to that path and add non-secret project UUIDs." >&2
  exit 1
}

PROJECT_ID="$(python3 - "$CONFIG" "$PROJECT" <<'PY'
import json, sys
p, slug = sys.argv[1], sys.argv[2]
with open(p, encoding="utf-8") as f:
    data = json.load(f)
if data.get("provider") != "bitwarden":
    raise SystemExit("Configured vault provider is not bitwarden")
entry = data.get("projects", {}).get(slug)
if not entry or not entry.get("project_id"):
    raise SystemExit(f"No Bitwarden project mapping for {slug}")
print(entry["project_id"])
PY
)"

exec bws run --project-id "$PROJECT_ID" -- "$@"
