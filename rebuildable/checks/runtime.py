"""Check 3: a declared runtime version."""

from __future__ import annotations

import re

from ..models import CheckResult, ScanContext
from .common import json_file, result, root_files


def run(context: ScanContext) -> CheckResult:
    files = root_files(context)
    for name in (".nvmrc", ".node-version", ".python-version", ".tool-versions"):
        if name in files and files[name].content.strip():
            return result(3, "Runtime version", True, f"Runtime version is pinned in {name}.", "No action needed.")
    package = json_file(context, "package.json")
    if package and isinstance(package.get("engines"), dict) and package["engines"]:
        return result(3, "Runtime version", True, "package.json declares an engines version.", "No action needed.")
    pyproject = files.get("pyproject.toml")
    if pyproject and re.search(r"(?m)^\s*requires-python\s*=\s*['\"]?[^\s#'\"]+", pyproject.content):
        return result(3, "Runtime version", True, "pyproject.toml declares requires-python.", "No action needed.")
    return result(3, "Runtime version", False, "No pinned Node or Python runtime version was found.", "Add .nvmrc, .python-version, .tool-versions, package.json engines, or pyproject.toml requires-python.")
