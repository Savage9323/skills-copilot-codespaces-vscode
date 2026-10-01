#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEMORY="$ROOT/memory"
fail=0

required=(
  "$MEMORY/PORTFOLIO.md"
  "$MEMORY/TOOLCHAIN.md"
  "$MEMORY/RESOURCES.md"
  "$MEMORY/SCHEMA.md"
  "$MEMORY/HANDOFF_TEMPLATE.md"
  "$MEMORY/history/MERGELOG.md"
  "$ROOT/skills/project-memory/SKILL.md"
  "$ROOT/skills/memory-orchestrator/SKILL.md"
)

for p in "${required[@]}"; do
  if [ -f "$p" ]; then
    echo "PASS: ${p#$ROOT/}"
  else
    echo "FAIL: ${p#$ROOT/}"
    fail=1
  fi
done

for d in "$MEMORY/projects" "$MEMORY/inbox" "$MEMORY/history" "$MEMORY/conflicts"; do
  if [ -d "$d" ]; then
    echo "PASS: directory ${d#$ROOT/}"
  else
    echo "FAIL: directory ${d#$ROOT/}"
    fail=1
  fi
done

if [ "$fail" -ne 0 ]; then
  echo "Memory doctor: FAIL"
  exit 1
fi

echo "Memory doctor: PASS"
