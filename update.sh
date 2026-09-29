#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

git fetch origin
git pull --ff-only

bash "$ROOT/install.sh"
bash "$ROOT/doctor.sh"
