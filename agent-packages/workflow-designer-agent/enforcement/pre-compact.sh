#!/usr/bin/env bash
set -euo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-.}"
bash "$ROOT/scripts/enforcement/workflow-enforce.sh" compaction
