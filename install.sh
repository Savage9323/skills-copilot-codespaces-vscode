#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$ROOT/skills"
TARGET="${OPENCODE_SKILLS_DIR:-$HOME/.config/opencode/skills}"

mkdir -p "$TARGET"

installed=0
for skill_dir in "$SOURCE"/*; do
  [ -d "$skill_dir" ] || continue
  name="$(basename "$skill_dir")"
  [ -f "$skill_dir/SKILL.md" ] || { echo "SKIP: $name has no SKILL.md"; continue; }

  dest="$TARGET/$name"
  if [ -e "$dest" ] && [ ! -L "$dest" ]; then
    backup="$dest.backup-$(date +%Y%m%d%H%M%S)"
    echo "BACKUP: $dest -> $backup"
    mv "$dest" "$backup"
  fi

  ln -sfn "$skill_dir" "$dest"
  echo "INSTALLED: $name"
  installed=$((installed + 1))
done

echo
echo "Installed $installed skills into $TARGET"
echo "Restart OpenCode so it refreshes discovered skills."
