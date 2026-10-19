<div align="center">

# ↻ rebuildable

### Make any project rebuildable on a clean machine.

An offline Python 3.12 CLI that scans a repository, scores its rebuildability,
and repairs the most common missing pieces — without network calls or hidden
installs.

<br>

```text
SCAN  →  FIX  →  VERIFY
  5/8     +3      8/8
```

</div>

---

## Why rebuildable?

“Works on my machine” usually means a project is missing one of its contracts:
a lockfile, a runtime pin, a test command, setup instructions, or a safe
configuration example.

`rebuildable` turns those contracts into a small, repeatable checklist:

- **Offline-first** — scanning and fixing never call the network.
- **Actionable** — every failure includes a reason and a fix hint.
- **Conservative** — existing files are not overwritten unless `--force` is used.
- **Portable** — Node, Python, and other stacks are detected automatically.
- **CI-friendly** — table output for people, JSON output for automation, and
  exit code `0` only when all eight checks pass.

## Setup

Requires **Python 3.12+**.

```sh
python -m pip install -e .
```

This installs the `rebuildable` command with Typer and Rich. You can also run
the module directly from a checkout:

```sh
python -m rebuildable scan .
```

## Quick start

### Scan a project

```sh
rebuildable scan path/to/project
```

The default output is a readable table:

```text
#   Check                    Status Reason                         Fix hint
1   Git repository           PASS   Git repository has a commit.   No action needed.
2   Dependency lockfile      PASS   Found package-lock.json.       No action needed.
3   Runtime version          PASS   .nvmrc pins Node.              No action needed.
4   Dockerfile               FAIL   Dockerfile is missing.         Add FROM and CMD.
...
Score: 7/8
```

Use `--json` only when a script or CI job needs structured output:

```sh
rebuildable scan path/to/project --json
```

### Fix missing pieces

Preview changes first:

```sh
rebuildable fix path/to/project --dry-run
```

Apply safe generated files:

```sh
rebuildable fix path/to/project
```

The fixer can generate or suggest:

- a runtime pin such as `.nvmrc` or `.python-version`;
- a Node or Python `Dockerfile`;
- a redacted `.env.example` from environment variable names;
- a `README.md` skeleton with Setup, Run, and Test sections;
- a missing test command stub;
- safe replacements for author-machine absolute paths.

It never runs network installs. If a lockfile is missing, it prints the exact
command you can run when dependencies are available.

Use `--force` only when you explicitly want generated files to replace existing
files:

```sh
rebuildable fix path/to/project --force
```

### Verify in Docker

```sh
rebuildable verify path/to/project
```

Verification always runs the scan. When Docker is available it also builds the
image and runs the detected test command inside it. Without Docker, it reports:

```text
Docker not available, skipped
```

## The eight checks

| # | Check | What passes |
|---:|---|---|
| 1 | Git repository | The project is a Git repository with at least one commit. |
| 2 | Dependency lockfile | A supported lockfile exists, or every `requirements.txt` dependency is pinned with `==`. |
| 3 | Runtime version | Node or Python is pinned in a version file or project metadata. |
| 4 | Dockerfile | `FROM`, lockfile-based installation, and `CMD`/`ENTRYPOINT` are present. |
| 5 | Test command | A package.json test script, pytest configuration, or Makefile `test` target exists. |
| 6 | README instructions | Setup, Run, and Test sections or command blocks are documented. |
| 7 | Settings and secrets | `.env.example` exists and common hardcoded secret patterns are absent. |
| 8 | Relative paths | No author-machine home-directory or Windows user paths are embedded. |

Skipped directories include `.git`, `node_modules`, virtual environments,
`dist`, and `build`. Binary files are ignored.

## Demo

The included fixtures start below 8/8 and are repaired in temporary copies, so
the originals are never modified.

### Windows, macOS, or Linux

```sh
python demo/run_demo.py
```

### macOS or Linux shell wrapper

```sh
bash demo/run_demo.sh
```

Example:

```text
broken-node-app
---------------
Before: 5/8
After: 8/8

broken-python-app
-----------------
Before: 5/8
After: 8/8
```

## Development

Install the test dependencies:

```sh
python -m pip install -r requirements.txt -r requirements-dev.txt
```

Run the test suite:

```sh
python -m pytest -q
```

Run the project's own self-scan:

```sh
python -m rebuildable scan .
```

Expected result:

```text
Score: 8/8
```

## Project layout

```text
rebuildable/
├── rebuildable/          # CLI, scanner, fixer, verifier, and checks
├── tests/                # pytest suite and fixture projects
├── demo/                 # broken Node/Python projects and runners
├── docs/index.html       # static GitHub Pages / Netlify documentation
├── Dockerfile
├── pyproject.toml
└── README.md
```

## License

This project is provided as-is for local development and repository
rebuildability checks.
