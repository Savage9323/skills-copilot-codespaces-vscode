#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${OPENCODE_SKILLS_DIR:-$HOME/.config/opencode/skills}"
MEMORY_TARGET="${OPENCODE_MEMORY_DIR:-$HOME/.config/opencode/memory}"
GLOBAL_AGENTS="$HOME/.config/opencode/AGENTS.md"
fail=0
count=0

echo "== Savage Agent Skills doctor =="

if command -v opencode >/dev/null 2>&1; then
  echo "PASS: OpenCode found: $(command -v opencode)"
else
  echo "WARN: OpenCode CLI not found on PATH"
fi

for skill_dir in "$ROOT"/skills/*; do
  [ -d "$skill_dir" ] || continue
  name="$(basename "$skill_dir")"
  count=$((count + 1))

  if [ ! -f "$skill_dir/SKILL.md" ]; then
    echo "FAIL: $name missing SKILL.md"
    fail=1
    continue
  fi

  if ! head -n 1 "$skill_dir/SKILL.md" | grep -Fxq -- '---'; then
    echo "FAIL: $name missing YAML frontmatter opener"
    fail=1
    continue
  fi

  if ! grep -q '^name:' "$skill_dir/SKILL.md"; then
    echo "FAIL: $name missing frontmatter name"
    fail=1
    continue
  fi

  if ! grep -q '^description:' "$skill_dir/SKILL.md"; then
    echo "FAIL: $name missing frontmatter description"
    fail=1
    continue
  fi

  if [ -L "$TARGET/$name" ]; then
    echo "PASS: $name installed"
  else
    echo "WARN: $name not linked into $TARGET"
  fi
done

if [ -L "$MEMORY_TARGET" ]; then
  echo "PASS: shared memory installed"
else
  echo "WARN: shared memory not linked into $MEMORY_TARGET"
fi

for required in PORTFOLIO.md TOOLCHAIN.md RESOURCES.md; do
  if [ -f "$MEMORY_TARGET/$required" ]; then
    echo "PASS: memory/$required"
  else
    echo "WARN: memory/$required unavailable"
  fi
done

if [ -f "$GLOBAL_AGENTS" ] && grep -Fq '<!-- SAVAGE_SHARED_AGENT_START -->' "$GLOBAL_AGENTS"; then
  echo "PASS: global AGENTS shared block installed"
else
  echo "WARN: global AGENTS shared block not installed"
fi

echo
echo "Skills checked: $count"
if [ "$fail" -ne 0 ]; then
  echo "Doctor: FAIL"
  exit 1
fi
echo "Doctor: PASS"
