#!/usr/bin/env bash

# Show the real scanner and fixer against both intentionally incomplete apps.
# The Python runner owns the temporary-copy isolation so this script is safe too.
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
exec python3 "$ROOT/demo/run_demo.py"
