"""Project ecosystem detection used by the fixer and Docker checks."""

from __future__ import annotations

from pathlib import Path

from .models import SourceFile


def detect_kind(root: Path, files: tuple[SourceFile, ...]) -> str:
    names = {Path(item.path).name.lower() for item in files}
    has_node = "package.json" in names or any(Path(item.path).suffix in {".js", ".ts", ".tsx", ".jsx"} for item in files)
    has_python = any(Path(item.path).suffix == ".py" for item in files) or bool(names & {"pyproject.toml", "requirements.txt", "setup.py"})
    if has_node and has_python:
        return "mixed"
    if has_node:
        return "node"
    if has_python:
        return "python"
    return "other"
