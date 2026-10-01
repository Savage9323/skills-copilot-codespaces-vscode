#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEMORY="${OPENCODE_MEMORY_DIR:-$ROOT/memory}"
PROJECT="${1:-}"

if [ -z "$PROJECT" ]; then
  echo "Usage: $0 <project-slug>" >&2
  exit 2
fi

DIR="$MEMORY/recent/$PROJECT"

echo "== Recent OpenCode memory =="
echo "Project: $PROJECT"
echo "Directory: $DIR"
echo

if [ ! -d "$DIR" ]; then
  echo "No captured recent-conversation directory yet."
  exit 0
fi

find "$DIR"   -maxdepth 1   -type f   -name '*.json'   -printf '%TY-%Tm-%Td %TH:%TM  %f\n'   | sort -r   | head -20
