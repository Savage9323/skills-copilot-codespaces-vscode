#!/usr/bin/env bash
# Disables only the M2 scanner; private candidate and recent journal data remain intact.
set -euo pipefail
systemctl --user disable --now savagedev-memory-candidates.timer || true
systemctl --user stop savagedev-memory-candidates.service || true
for name in savagedev-memory-candidates.timer savagedev-memory-candidates.service; do
  rm -f "$HOME/.config/systemd/user/$name"
done
for name in memory-lifecycle-scan-all.sh memory-lifecycle.py; do
  rm -f "$HOME/.local/lib/savagedev/$name"
done
systemctl --user daemon-reload
echo "M2 user timer disabled; all private state and repo sources preserved."
