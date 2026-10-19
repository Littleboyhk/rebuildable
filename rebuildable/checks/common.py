"""Helpers shared by the deliberately small check modules."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..models import CheckResult, ScanContext, SourceFile


def result(number: int, name: str, passed: bool, reason: str, hint: str) -> CheckResult:
    return CheckResult(number, name, passed, reason, hint)


def file_map(context: ScanContext) -> dict[str, SourceFile]:
    return {item.path: item for item in context.files}


def root_files(context: ScanContext) -> dict[str, SourceFile]:
    return {Path(item.path).name.lower(): item for item in context.files if "/" not in item.path}


def json_file(context: ScanContext, name: str) -> dict[str, Any] | None:
    source = root_files(context).get(name)
    if source is None:
        return None
    try:
        parsed = json.loads(source.content)
    except (json.JSONDecodeError, TypeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def has_heading_or_code_block(text: str, word: str) -> bool:
    heading = re.search(rf"^\s*#{{1,6}}\s*{re.escape(word)}\b", text, re.IGNORECASE | re.MULTILINE)
    return heading is not None
