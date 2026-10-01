#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$HOME/.config/savage-agent"
CONFIG="$CONFIG_DIR/vault-projects.json"

mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"

if [ ! -f "$CONFIG" ]; then
  cp "$ROOT/secrets/vault-projects.example.json" "$CONFIG"
  chmod 600 "$CONFIG"
  echo "CREATED: $CONFIG"
else
  echo "EXISTS: $CONFIG"
fi

if command -v bws >/dev/null 2>&1; then
  echo "PASS: bws already installed: $(bws --version 2>/dev/null || true)"
else
  cat <<'EOF'
Bitwarden Secrets Manager CLI (bws) is not installed.

Official Linux install command from Bitwarden:
  curl https://bws.bitwarden.com/install | sh

For a stricter supply-chain workflow, download a specific release from Bitwarden's official GitHub SDK releases and verify it before installing.

After installing bws:
1. Create/enable a Free Bitwarden Secrets Manager organization.
2. Create up to three projects as needed.
3. Create a machine account for OpenCode.
4. Give it READ-ONLY access to the required projects.
5. Create an access token.
6. Do NOT paste the token into ChatGPT/OpenCode.
7. Load it directly into your terminal as BWS_ACCESS_TOKEN.
8. Put only project UUIDs in ~/.config/savage-agent/vault-projects.json.
EOF
fi

echo
echo "Next check:"
echo "  bash $ROOT/scripts/vault-doctor.sh"
