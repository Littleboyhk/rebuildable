"""Check 5: a declared test command."""

from __future__ import annotations

import re

from ..models import CheckResult, ScanContext
from .common import json_file, result, root_files


def run(context: ScanContext) -> CheckResult:
    files = root_files(context)
    package = json_file(context, "package.json")
    scripts = package.get("scripts", {}) if package else {}
    if isinstance(scripts, dict) and isinstance(scripts.get("test"), str) and scripts["test"].strip():
        return result(5, "Test command", True, "package.json defines a test script.", "No action needed.")
    for name in ("pytest.ini", "tox.ini"):
        if name in files and re.search(r"(?im)^\s*\[.*pytest|^\s*\[testenv", files[name].content):
            return result(5, "Test command", True, f"{name} config declares a test runner.", "No action needed.")
    pyproject = files.get("pyproject.toml")
    if pyproject and "[tool.pytest" in pyproject.content:
        return result(5, "Test command", True, "pyproject.toml configures pytest.", "No action needed.")
    setup_cfg = files.get("setup.cfg")
    if setup_cfg and "[tool:pytest]" in setup_cfg.content:
        return result(5, "Test command", True, "setup.cfg configures pytest.", "No action needed.")
    makefile = files.get("makefile")
    if makefile and re.search(r"(?m)^test\s*:", makefile.content):
        return result(5, "Test command", True, "Makefile defines a test target.", "No action needed.")
    return result(5, "Test command", False, "No test command was found.", "Add a package.json test script, pytest config, or Makefile test target.")
