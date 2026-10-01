#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INBOX="$ROOT/memory/inbox"

usage() {
  echo "Usage: $0 <session-id> <project-slug>"
  echo "Exports an OpenCode session with --sanitize into the memory inbox."
}

[ "$#" -eq 2 ] || { usage >&2; exit 2; }

SESSION_ID="$1"
PROJECT="$2"

case "$SESSION_ID" in
  *[!A-Za-z0-9._-]*|"") echo "Invalid session id" >&2; exit 2 ;;
esac
case "$PROJECT" in
  *[!A-Za-z0-9._-]*|"") echo "Invalid project slug" >&2; exit 2 ;;
esac

command -v opencode >/dev/null 2>&1 || {
  echo "OpenCode is not installed or not on PATH." >&2
  exit 1
}

mkdir -p "$INBOX"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$INBOX/${STAMP}__opencode__${PROJECT}__${SESSION_ID}.json"
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

opencode session export "$SESSION_ID" --sanitize > "$TMP"

if [ ! -s "$TMP" ]; then
  echo "OpenCode export was empty." >&2
  exit 1
fi

mv "$TMP" "$DEST"
trap - EXIT
echo "$DEST"
