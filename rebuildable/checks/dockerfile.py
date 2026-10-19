"""Check 4: a Dockerfile can build, install, and run the project."""

from __future__ import annotations

import re

from ..models import CheckResult, ScanContext
from .common import result, root_files


def run(context: ScanContext) -> CheckResult:
    dockerfile = root_files(context).get("dockerfile")
    if dockerfile is None:
        return result(4, "Dockerfile", False, "Dockerfile is missing.", "Add FROM, dependency installation from the lockfile, and CMD or ENTRYPOINT.")
    text = dockerfile.content
    has_from = re.search(r"(?im)^\s*FROM\s+\S+", text) is not None
    has_run = re.search(r"(?im)^\s*(CMD|ENTRYPOINT)\b", text) is not None
    install_words = ("npm ci", "yarn install", "pnpm install", "pip install", "poetry install", "uv sync")
    has_install = any(word in text for word in install_words)
    passed = has_from and has_run and has_install
    missing = []
    if not has_from:
        missing.append("FROM")
    if not has_install:
        missing.append("lockfile install")
    if not has_run:
        missing.append("CMD/ENTRYPOINT")
    reason = "Dockerfile has a base image, lockfile install, and run command." if passed else "Dockerfile is missing " + ", ".join(missing) + "."
    return result(4, "Dockerfile", passed, reason, "Use a pinned runtime image, install from the committed lockfile, and add CMD or ENTRYPOINT.")
