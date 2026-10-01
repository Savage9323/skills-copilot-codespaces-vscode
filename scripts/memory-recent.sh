#!/usr/bin/env bash
set -euo pipefail

STATE_ROOT="${SAVAGE_MEMORY_STATE_DIR:-$HOME/.local/share/savage-agent-memory}"
PROJECT="${1:-}"

if [ -z "$PROJECT" ]; then
  echo "Usage: $0 <project-slug>" >&2
  exit 2
fi

DIR="$STATE_ROOT/recent/$PROJECT"

echo "== Recent OpenCode memory =="
echo "Project: $PROJECT"
echo "Private state: $DIR"
echo

if [ ! -d "$DIR" ]; then
  echo "No captured recent-conversation directory yet."
  exit 0
fi

find "$DIR"   -maxdepth 1   -type f   -name '*.json'   -printf '%TY-%Tm-%Td %TH:%TM  %f\n'   | sort -r   | head -20
