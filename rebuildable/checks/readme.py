"""Check 6: setup, run, and test instructions in the README."""

from __future__ import annotations

import re

from ..models import CheckResult, ScanContext
from .common import result, root_files


def run(context: ScanContext) -> CheckResult:
    readme = next((source for name, source in root_files(context).items() if name.startswith("readme")), None)
    if readme is None:
        return result(6, "README instructions", False, "README is missing.", "Add Setup, Run, and Test sections with copyable commands.")
    missing = []
    for word in ("setup", "run", "test"):
        heading = re.search(rf"(?im)^\s*#{{1,6}}\s*{word}\b", readme.content)
        code_block = re.search(rf"(?is)```[^\n]*\n[^`]*\b{word}\b[^`]*```", readme.content)
        if heading is None and code_block is None:
            missing.append(word.title())
    passed = not missing
    return result(6, "README instructions", passed, "README has Setup, Run, and Test sections." if passed else "README is missing " + ", ".join(missing) + " instructions.", "Document one setup, run, and test command under clear headings.")
