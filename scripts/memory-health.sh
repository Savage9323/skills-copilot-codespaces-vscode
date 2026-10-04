#!/usr/bin/env bash
set -euo pipefail

STATE_ROOT="${SAVAGE_MEMORY_STATE_DIR:-$HOME/.local/share/savage-agent-memory}"
HEALTH="$STATE_ROOT/plugin-health.json"
PROJECT="${1:-}"

echo "== Savage Auto Memory health =="

if [ ! -f "$HEALTH" ]; then
  echo "Plugin health file: MISSING"
  echo "Expected: $HEALTH"
  exit 1
fi

python3 - "$HEALTH" "$PROJECT" <<'PY'
import json, sys, pathlib

health_path = pathlib.Path(sys.argv[1])
project = sys.argv[2] if len(sys.argv) > 2 else ""

with health_path.open(encoding="utf-8") as f:
    data = json.load(f)

safe_keys = [
    "status",
    "plugin",
    "app_version",
    "directory",
    "loaded_at",
    "updated_at",
    "last_prompt_capture_at",
    "last_prompt_session_id",
    "last_prompt_project",
    "last_context_hook_at",
    "last_context_session_id",
    "last_context_project",
    "last_error",
]

for key in safe_keys:
    if key in data:
        print(f"{key}: {data[key]}")

if project:
    recent = health_path.parent / "recent" / project
    count = len(list(recent.glob("*.json"))) if recent.exists() else 0
    print(f"recent_project_files: {count}")
PY
