#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEMORY="$ROOT/memory"

echo "== Unified AI Memory =="
echo "Root: $MEMORY"
echo

echo "-- Canonical projects --"
find "$MEMORY/projects" -maxdepth 1 -type f -name '*.md' -printf '%f\n' 2>/dev/null | sort || true

echo
echo "-- Pending inbox --"
find "$MEMORY/inbox" -maxdepth 1 -type f ! -name 'README.md' -printf '%TY-%Tm-%Td %TH:%TM  %f\n' 2>/dev/null | sort || true

echo
echo "-- Conflicts --"
find "$MEMORY/conflicts" -maxdepth 1 -type f ! -name 'README.md' -printf '%TY-%Tm-%Td %TH:%TM  %f\n' 2>/dev/null | sort || true

echo
echo "-- Recent merge history --"
tail -n 20 "$MEMORY/history/MERGELOG.md" 2>/dev/null || true
