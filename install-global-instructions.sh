#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$HOME/.config/opencode/AGENTS.md"
SNIPPET="$ROOT/GLOBAL_AGENTS_SNIPPET.md"

mkdir -p "$(dirname "$TARGET")"

START="<!-- SAVAGE_SHARED_AGENT_START -->"
END="<!-- SAVAGE_SHARED_AGENT_END -->"

python3 - "$TARGET" "$SNIPPET" "$START" "$END" <<'PY'
from pathlib import Path
import sys

target = Path(sys.argv[1])
snippet = Path(sys.argv[2]).read_text()
start, end = sys.argv[3], sys.argv[4]

existing = target.read_text() if target.exists() else ""

block = f"{start}\n{snippet.rstrip()}\n{end}\n"

if start in existing and end in existing:
    before, rest = existing.split(start, 1)
    _, after = rest.split(end, 1)
    updated = before.rstrip() + "\n\n" + block + after.lstrip()
else:
    if existing.strip():
        backup = target.with_name(target.name + ".backup")
        backup.write_text(existing)
        updated = existing.rstrip() + "\n\n" + block
    else:
        updated = block

target.write_text(updated)
print(f"Updated {target}")
PY
