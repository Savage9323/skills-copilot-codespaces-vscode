#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INBOX="$ROOT/memory/inbox"

usage() {
  echo "Usage: $0 <source> <project-slug> [id]"
  echo "Reads handoff content from stdin and stores it in the memory inbox."
}

[ "$#" -ge 2 ] || { usage >&2; exit 2; }

SOURCE="$1"
PROJECT="$2"
ID="${3:-manual}"

case "$SOURCE" in
  *[!A-Za-z0-9._-]*|"") echo "Invalid source" >&2; exit 2 ;;
esac
case "$PROJECT" in
  *[!A-Za-z0-9._-]*|"") echo "Invalid project slug" >&2; exit 2 ;;
esac
case "$ID" in
  *[!A-Za-z0-9._-]*|"") echo "Invalid id" >&2; exit 2 ;;
esac

mkdir -p "$INBOX"
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
cat > "$TMP"

if [ ! -s "$TMP" ]; then
  echo "Refusing to import empty memory." >&2
  exit 1
fi

# Conservative secret tripwire. This intentionally catches only high-signal forms.
if grep -Eqi   '-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9_]{20,}|sk-(proj-)?[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|service[_-]?role[^[:space:]]*[=:][[:space:]]*[^[:space:]]+'   "$TMP"; then
  echo "Refusing import: probable credential/private key detected." >&2
  exit 1
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$INBOX/${STAMP}__${SOURCE}__${PROJECT}__${ID}.md"

{
  echo "<!-- memory-inbox"
  echo "source: $SOURCE"
  echo "project: $PROJECT"
  echo "captured_at: $STAMP"
  echo "id: $ID"
  echo "status: candidate"
  echo "-->"
  echo
  cat "$TMP"
} > "$DEST"

echo "$DEST"
