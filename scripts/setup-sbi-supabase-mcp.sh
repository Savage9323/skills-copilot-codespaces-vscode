#!/usr/bin/env bash
set -euo pipefail

command -v opencode >/dev/null 2>&1 || {
  echo "OpenCode is not installed or not on PATH." >&2
  exit 1
}

PROJECT_REF="etfcbzhiiinilahaofmo"
URL="https://mcp.supabase.com/mcp?project_ref=${PROJECT_REF}&read_only=true&features=database%2Cdebugging%2Cdevelopment%2Cdocs"

echo "Adding project-scoped read-only Supabase MCP for SBI..."
opencode mcp add supabase-sbi-readonly --url "$URL"

echo
echo "If authentication is required, run OpenCode, open /mcps, select supabase-sbi-readonly, and authenticate in the browser."
echo
opencode mcp list
