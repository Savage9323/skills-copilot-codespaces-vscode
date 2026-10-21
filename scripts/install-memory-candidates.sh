#!/usr/bin/env bash
# Reproducible user-level deployment of the M2 private candidate scanner.
set -euo pipefail
umask 077
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$HOME/.local/lib/savagedev"
UNITS="$HOME/.config/systemd/user"
ENABLE="${1:-}"
if [[ -n "$ENABLE" && "$ENABLE" != "--enable" ]]; then
  echo "Usage: $0 [--enable]" >&2
  exit 2
fi
if ! systemctl --user is-system-running >/dev/null 2>&1; then
  echo "User systemd is not running; scanner not installed." >&2
  exit 1
fi
python3 -m unittest discover -s "$ROOT/tests" -p 'test_memory_lifecycle.py' -q
mkdir -p "$TARGET" "$UNITS"
chmod 700 "$TARGET"
install -m 755 "$ROOT/scripts/memory-lifecycle.py" "$TARGET/memory-lifecycle.py"
install -m 755 "$ROOT/scripts/memory-lifecycle-scan-all.sh" "$TARGET/memory-lifecycle-scan-all.sh"
install -m 644 "$ROOT/systemd/savagedev-memory-candidates.service" "$UNITS/savagedev-memory-candidates.service"
install -m 644 "$ROOT/systemd/savagedev-memory-candidates.timer" "$UNITS/savagedev-memory-candidates.timer"
systemd-analyze verify "$UNITS/savagedev-memory-candidates.service" "$UNITS/savagedev-memory-candidates.timer"
systemctl --user daemon-reload
if [[ "$ENABLE" == "--enable" ]]; then
  systemctl --user start savagedev-memory-candidates.service
  systemctl --user enable --now savagedev-memory-candidates.timer
  echo "M2 candidate scanner: daily timer enabled; candidate extraction only."
else
  echo "M2 scanner and units installed, timer NOT enabled."
fi
