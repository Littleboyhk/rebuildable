#!/usr/bin/env bash

# This is a fixture walkthrough, not the rebuildable scanner or fixer. It runs
# the two intentionally broken entrypoints, reports their expected failures,
# and exits zero so the demo is safe to include in documentation or CI output.
set -u
export PYTHONDONTWRITEBYTECODE=1

DEMO_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
NODE_APP="$DEMO_DIR/broken-node-app"
PYTHON_APP="$DEMO_DIR/broken-python-app"

printf '\nrebuildable demo · intentionally broken fixtures\n'
printf '%s\n' '-----------------------------------------------'
printf 'baseline: 2/8 checks passing\n'
printf '  01 hard-coded secrets    PASS\n'
printf '  02 debug artifacts       FAIL  development logging\n'
printf '  03 unresolved markers    FAIL  TODO marker\n'
printf '  04 dependency metadata   FAIL  lockfile missing\n'
printf '  05 test coverage signals FAIL  no test files\n'
printf '  06 project documentation PASS\n'
printf '  07 entrypoint discovery  FAIL  conventional entry missing\n'
printf '  08 configuration hygiene FAIL  local .env present\n'

run_case() {
  local label="$1"
  local directory="$2"
  shift 2

  printf '\n%s\n' "$label"
  printf '  $ (cd %s && %s)\n' "${directory#"$DEMO_DIR/"}" "$*"

  local output
  local exit_code
  if output=$(cd "$directory" && "$@" 2>&1); then
    exit_code=0
  else
    exit_code=$?
  fi

  if [ -n "$output" ]; then
    while IFS= read -r line; do
      printf '  %s\n' "$line"
    done <<< "$output"
  fi
  printf '  expected fixture exit: %s\n' "$exit_code"
}

if command -v node >/dev/null 2>&1; then
  run_case 'Node fixture' "$NODE_APP" node src/start.js
else
  printf '\nNode fixture: skipped (node is not installed)\n'
fi

if command -v python3 >/dev/null 2>&1; then
  run_case 'Python fixture' "$PYTHON_APP" python3 app/run.py
else
  printf '\nPython fixture: skipped (python3 is not installed)\n'
fi

printf '\nThe failures above are intentional. Repair the fixtures, then rerun the same commands.\n'
