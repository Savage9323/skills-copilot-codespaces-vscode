#!/usr/bin/env bash
set -euo pipefail

CONFIG="${SAVAGE_VAULT_CONFIG:-$HOME/.config/savage-agent/vault-projects.json}"
fail=0

echo "== Secret Vault doctor =="

if command -v bws >/dev/null 2>&1; then
  echo "PASS: bws found: $(command -v bws)"
  echo "INFO: $(bws --version 2>/dev/null || true)"
else
  echo "WARN: Bitwarden Secrets Manager CLI (bws) not installed"
fi

if [ -f "$CONFIG" ]; then
  echo "PASS: non-secret vault project mapping exists"
  if python3 -m json.tool "$CONFIG" >/dev/null 2>&1; then
    echo "PASS: vault project mapping is valid JSON"
  else
    echo "FAIL: vault project mapping is invalid JSON"
    fail=1
  fi
else
  echo "WARN: vault project mapping not configured: $CONFIG"
fi

if [ -n "${BWS_ACCESS_TOKEN:-}" ]; then
  echo "PASS: BWS_ACCESS_TOKEN loaded (value not displayed)"
  if command -v bws >/dev/null 2>&1; then
    if bws project list --output json >/dev/null 2>&1; then
      echo "PASS: Bitwarden machine-account authentication works"
    else
      echo "WARN: Bitwarden authentication test failed"
    fi
  fi
else
  echo "WARN: BWS_ACCESS_TOKEN not loaded"
fi

if [ "$fail" -ne 0 ]; then
  echo "Vault doctor: FAIL"
  exit 1
fi

echo "Vault doctor: PASS (warnings may remain until account setup is complete)"
