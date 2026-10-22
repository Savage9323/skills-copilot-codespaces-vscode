#!/usr/bin/env bash
# Fail-closed wrapper. No arbitrary commands and never expose credential values.
set -euo pipefail
umask 077
if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 <approved-project-slug> <preapproved-action>" >&2
  exit 2
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/vault-broker.py" "$1" "$2"
