#!/usr/bin/env bash
# Bounded, non-promoting M2 sweep of locally captured OpenCode sessions.
set -euo pipefail
umask 077
SOURCE_ROOT="${SAVAGE_MEMORY_STATE_DIR:-$HOME/.local/share/savage-agent-memory}"
JOURNAL_ROOT="$SOURCE_ROOT/recent"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCANNER="$SCRIPT_DIR/memory-lifecycle.py"
mkdir -p "$SOURCE_ROOT"
chmod 700 "$SOURCE_ROOT"
exec 9>"$SOURCE_ROOT/m2-scan.lock"
/usr/bin/flock -n 9 || exit 0
if [[ ! -d "$JOURNAL_ROOT" ]]; then
  echo '{"status":"no-private-journals"}'
  exit 0
fi
shopt -s nullglob
for dir in "$JOURNAL_ROOT"/*; do
  [[ -d "$dir" && ! -L "$dir" ]] || continue
  project="$(basename "$dir")"
  [[ "$project" =~ ^[a-z0-9][a-z0-9._-]{0,63}$ && "$project" != *..* ]] || continue
  python3 "$SCANNER" scan --project "$project" --recent-root "$JOURNAL_ROOT" --state-root "$SOURCE_ROOT" --identity-map "${SAVAGE_PROJECT_REGISTRY:-$HOME/.savagedev/project-identities.json}" --write
done
