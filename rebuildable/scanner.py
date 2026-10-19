"""Public scanner API."""

from __future__ import annotations

from pathlib import Path

from .checks import CHECKS
from .detect import detect_kind
from .files import read_files
from .models import ScanContext, ScanResult


def scan(path: str | Path) -> ScanResult:
    root = Path(path).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"project path does not exist: {path}")
    if not root.is_dir():
        raise ValueError(f"project path is not a directory: {path}")
    files = read_files(root)
    context = ScanContext(root, files, detect_kind(root, files))
    return ScanResult(root, tuple(check(context) for check in CHECKS))
