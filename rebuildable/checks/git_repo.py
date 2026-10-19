"""Check 1: a repository with a reachable commit."""

from __future__ import annotations

import subprocess

from ..models import CheckResult, ScanContext
from .common import result


def run(context: ScanContext) -> CheckResult:
    try:
        repository = subprocess.run(
            ["git", "-C", str(context.root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        commit = subprocess.run(
            ["git", "-C", str(context.root), "rev-parse", "--verify", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return result(1, "Git repository", False, "Git is not available or this is not a repository.", "Run git init, add the project files, and create the first commit.")
    passed = repository.returncode == 0 and repository.stdout.strip() == "true" and commit.returncode == 0
    return result(
        1,
        "Git repository",
        passed,
        "Git repository has at least one commit." if passed else "Git repository is missing or has no commits.",
        "Create a commit before handing the project to a clean machine.",
    )
