#!/usr/bin/env bash
set -euo pipefail
HERE="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec python3 -B "$HERE/../../scripts/enforcement/run_hook.py"
