"""Run the rebuildable demo against temporary copies of its fixtures."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ("broken-node-app", "broken-python-app")

# Running ``python demo/run_demo.py`` puts ``demo/`` on sys.path. Add the
# repository root so this works without an editable install from any cwd.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rebuildable.fixer import fix
from rebuildable.scanner import scan


def run_case(project_name: str) -> None:
    source = ROOT / "demo" / project_name
    print(f"\n{project_name}")
    print("-" * len(project_name))

    with tempfile.TemporaryDirectory(prefix="rebuildable-demo-") as temporary:
        copy = Path(temporary) / source.name
        shutil.copytree(source, copy)

        # A copied fixture does not carry its parent repository's .git tree.
        # Create an isolated temporary history so the Git check reflects a
        # clean checkout without ever touching the originals.
        subprocess.run(["git", "init", "--quiet", str(copy)], check=True, capture_output=True, text=True)
        subprocess.run(["git", "-C", str(copy), "add", "."], check=True, capture_output=True, text=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(copy),
                "-c",
                "user.name=Demo User",
                "-c",
                "user.email=demo@example.invalid",
                "commit",
                "--quiet",
                "-m",
                "fixture",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        before = scan(copy)
        print(f"Before: {before.score}/{len(before.checks)}")

        repaired = fix(copy, force=True)
        for action in repaired.actions:
            print(f"- {action.action} {action.path}: {action.detail}")
        for report in repaired.reports:
            print(f"- Note: {report}")

        after = scan(copy)
        print(f"After: {after.score}/{len(after.checks)}")


def main() -> None:
    for project_name in PROJECTS:
        run_case(project_name)


if __name__ == "__main__":
    main()
