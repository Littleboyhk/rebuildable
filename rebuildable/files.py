"""Safe, offline source-file traversal."""

from __future__ import annotations

from pathlib import Path

from .models import SourceFile

SKIP_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
}


def read_files(root: Path) -> tuple[SourceFile, ...]:
    """Read UTF-8 text files, ignoring generated, binary, and unreadable files."""

    if root.is_file():
        candidates = [root]
        base = root.parent
    else:
        candidates = []
        base = root
        for directory, dirs, names in __import__("os").walk(root):
            dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRECTORIES)
            for name in sorted(names):
                candidates.append(Path(directory) / name)

    files: list[SourceFile] = []
    for path in sorted(candidates):
        if not path.is_file() or path.suffix.lower() in {".pyc", ".pyo", ".whl", ".zip", ".exe", ".dll"}:
            continue
        try:
            data = path.read_bytes()
            if b"\x00" in data:
                continue
            content = data.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        relative = path.relative_to(base).as_posix()
        files.append(SourceFile(relative, content))
    return tuple(files)
