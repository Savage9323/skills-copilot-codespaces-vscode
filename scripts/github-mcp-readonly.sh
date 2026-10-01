#!/usr/bin/env bash
set -euo pipefail

for cmd in gh docker; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "Required command not found: $cmd" >&2
    exit 1
  }
done

TOKEN="$(gh auth token 2>/dev/null || true)"
if [ -z "$TOKEN" ]; then
  echo "GitHub CLI is not authenticated. Run: gh auth login" >&2
  exit 1
fi

exec docker run -i --rm   -e GITHUB_PERSONAL_ACCESS_TOKEN="$TOKEN"   -e GITHUB_TOOLSETS="context,repos,issues,pull_requests"   -e GITHUB_READ_ONLY=1   ghcr.io/github/github-mcp-server
