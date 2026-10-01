#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$ROOT/skills"
TARGET="${OPENCODE_SKILLS_DIR:-$HOME/.config/opencode/skills}"
MEMORY_SOURCE="$ROOT/memory"
MEMORY_TARGET="${OPENCODE_MEMORY_DIR:-$HOME/.config/opencode/memory}"
PLUGIN_SOURCE="$ROOT/opencode-plugins"
PLUGIN_TARGET="${OPENCODE_PLUGIN_DIR:-$HOME/.config/opencode/plugins}"

mkdir -p "$TARGET"
mkdir -p "$(dirname "$MEMORY_TARGET")"
mkdir -p "$PLUGIN_TARGET"

installed=0
for skill_dir in "$SOURCE"/*; do
  [ -d "$skill_dir" ] || continue
  name="$(basename "$skill_dir")"
  [ -f "$skill_dir/SKILL.md" ] || { echo "SKIP: $name has no SKILL.md"; continue; }

  dest="$TARGET/$name"

  if [ -L "$dest" ]; then
    rm "$dest"
  elif [ -e "$dest" ] && [ ! -f "$dest/.savage-managed" ]; then
    backup="$dest.backup-$(date +%Y%m%d%H%M%S)"
    echo "BACKUP: $dest -> $backup"
    mv "$dest" "$backup"
  elif [ -d "$dest" ] && [ -f "$dest/.savage-managed" ]; then
    rm -rf "$dest"
  fi

  mkdir -p "$dest"
  cp -a "$skill_dir/." "$dest/"
  touch "$dest/.savage-managed"
  echo "INSTALLED SKILL: $name"
  installed=$((installed + 1))
done

if [ -e "$MEMORY_TARGET" ] && [ ! -L "$MEMORY_TARGET" ]; then
  backup="$MEMORY_TARGET.backup-$(date +%Y%m%d%H%M%S)"
  echo "BACKUP: $MEMORY_TARGET -> $backup"
  mv "$MEMORY_TARGET" "$backup"
fi

ln -sfn "$MEMORY_SOURCE" "$MEMORY_TARGET"
echo "INSTALLED MEMORY: $MEMORY_TARGET -> $MEMORY_SOURCE"

plugin_count=0
for plugin in "$PLUGIN_SOURCE"/*.js "$PLUGIN_SOURCE"/*.ts; do
  [ -f "$plugin" ] || continue
  name="$(basename "$plugin")"
  cp "$plugin" "$PLUGIN_TARGET/$name"
  chmod 600 "$PLUGIN_TARGET/$name"
  echo "INSTALLED PLUGIN: $name"
  plugin_count=$((plugin_count + 1))
done

bash "$ROOT/install-global-instructions.sh"

echo
echo "Installed $installed skills into $TARGET"
echo "Installed $plugin_count OpenCode plugin(s) into $PLUGIN_TARGET"
echo "Shared memory linked at $MEMORY_TARGET"
echo "Global instructions updated at $HOME/.config/opencode/AGENTS.md"
echo "Restart or reload OpenCode so it refreshes skills, plugins, and instructions."
