"""Check 8: no machine-specific absolute paths."""

from __future__ import annotations

import re

from ..models import CheckResult, ScanContext
from .common import result

ABSOLUTE_PATHS = (
    re.compile(r"(?i)\b[A-Z]:\\" + "Users\\" + r"[^\s'\"`]+"),
    re.compile(r"(?i)/" + "home/" + r"[^\s'\"`]+|/" + "Users/" + r"[^\s'\"`]+"),
)


def run(context: ScanContext) -> CheckResult:
    hits = [source.path for source in context.files if any(pattern.search(source.content) for pattern in ABSOLUTE_PATHS)]
    if not hits:
        return result(8, "Relative paths", True, "No author-machine absolute paths were found.", "No action needed.")
    return result(8, "Relative paths", False, "Absolute paths found in " + ", ".join(hits[:3]) + ".", "Replace machine-specific paths with relative paths or environment variables.")
