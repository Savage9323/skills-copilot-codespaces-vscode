#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

command -v opencode >/dev/null 2>&1 || {
  echo "OpenCode is not installed or not on PATH." >&2
  exit 1
}

command -v gh >/dev/null 2>&1 || {
  echo "GitHub CLI is not installed or not on PATH." >&2
  exit 1
}

if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI is not authenticated. Run: gh auth login" >&2
  exit 1
fi

echo "Adding global read-only GitHub MCP..."
opencode mcp add github-readonly --global -- bash "$ROOT/scripts/github-mcp-readonly.sh"

echo
opencode mcp list
