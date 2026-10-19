"""Check 2: a supported dependency lockfile."""

from __future__ import annotations

from pathlib import Path

from ..models import CheckResult, ScanContext
from .common import result, root_files

LOCKFILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "uv.lock", "pipfile.lock"}


def _requirements_are_pinned(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    return bool(lines) and all("==" in line and not line.startswith(("-r", "--", "git+", "http://", "https://")) for line in lines)


def run(context: ScanContext) -> CheckResult:
    files = root_files(context)
    found = sorted(name for name in LOCKFILES if name in files)
    if found:
        return result(2, "Dependency lockfile", True, f"Found {found[0]}.", "No action needed.")
    requirements = files.get("requirements.txt")
    if requirements and _requirements_are_pinned(requirements.content):
        return result(2, "Dependency lockfile", True, "requirements.txt pins every dependency with ==.", "No action needed.")
    return result(2, "Dependency lockfile", False, "No supported dependency lockfile was found.", "Generate and commit a lockfile; for example: uv lock, npm install, poetry lock, or pip freeze > requirements.txt.")
