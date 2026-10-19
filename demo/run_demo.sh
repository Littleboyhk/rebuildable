#!/usr/bin/env bash

# Show the real scanner and fixer against both intentionally incomplete apps.
set -u
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

run_case() {
  local label="$1"
  local directory="$2"
  printf '\n%s\n' "$label"
  printf '%s\n' '-----------------------------------------------'
  (cd "$ROOT" && python3 -m rebuildable scan "$directory") || true
  printf '\nApplying offline fixes (force is used so the demo README is regenerated)...\n'
  (cd "$ROOT" && python3 -m rebuildable fix "$directory" --force) || true
  printf '\nAfter fix:\n'
  (cd "$ROOT" && python3 -m rebuildable scan "$directory") || true
}

run_case 'Broken Node app' demo/broken-node-app
run_case 'Broken Python app' demo/broken-python-app
