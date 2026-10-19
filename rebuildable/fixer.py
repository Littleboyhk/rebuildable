"""Offline, conservative project repair suggestions and file generation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .detect import detect_kind
from .files import read_files
from .models import ScanResult
from .scanner import scan


@dataclass(frozen=True)
class FixAction:
    path: str
    action: str
    detail: str


@dataclass(frozen=True)
class FixResult:
    before: ScanResult
    after: ScanResult
    actions: tuple[FixAction, ...]
    reports: tuple[str, ...]


def _version(root: Path, files: dict[str, str], kind: str) -> tuple[str, str] | None:
    for name in (".nvmrc", ".node-version", ".python-version"):
        if files.get(name, "").strip():
            return name, files[name].strip().splitlines()[0]
    tools = files.get(".tool-versions", "")
    if tools.strip():
        for line in tools.splitlines():
            if line.startswith(("nodejs ", "python ")):
                runtime, version = line.split(maxsplit=1)
                return (".nvmrc" if runtime == "nodejs" else ".python-version", version.strip())
    package = files.get("package.json")
    if package:
        try:
            engines = json.loads(package).get("engines", {})
        except (json.JSONDecodeError, AttributeError):
            engines = {}
        if isinstance(engines, dict) and engines.get("node"):
            match = re.search(r"\d+(?:\.\d+){0,2}", str(engines["node"]))
            if match:
                return ".nvmrc", match.group(0)
    pyproject = files.get("pyproject.toml", "")
    match = re.search(r"requires-python\s*=\s*['\"]?[^\d]*(\d+\.\d+)", pyproject)
    if match:
        return ".python-version", match.group(1)
    return None


def _kind_and_files(root: Path) -> tuple[str, dict[str, str]]:
    collected = read_files(root)
    return detect_kind(root, collected), {Path(item.path).name.lower(): item.content for item in collected if "/" not in item.path}


def _dockerfile(kind: str) -> str:
    if kind == "node":
        return """FROM node:20-bookworm-slim\nWORKDIR /app\nCOPY package*.json ./\nRUN npm ci\nCOPY . .\nCMD [\"npm\", \"start\"]\n"""
    return """FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt ./\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nCMD [\"python\", \"-m\", \"app\"]\n"""


def _readme(kind: str) -> str:
    command = "npm install" if kind == "node" else "python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt"
    run = "npm start" if kind == "node" else "python -m app"
    test = "npm test" if kind == "node" else "pytest"
    return f"""# Project\n\n## Setup\n\n```sh\n{command}\n```\n\n## Run\n\n```sh\n{run}\n```\n\n## Test\n\n```sh\n{test}\n```\n"""


def _environment_names(root: Path) -> list[str]:
    names: set[str] = set()
    for source in read_files(root):
        if source.path.startswith(".env"):
            continue
        names.update(re.findall(r"process\.env\.([A-Z][A-Z0-9_]*)", source.content))
        names.update(re.findall(r"(?:os\.getenv|os\.environ\.get|os\.environ)\s*\[?\s*[\"']([A-Z][A-Z0-9_]*)", source.content))
    return sorted(names)


def _safe_relative_replacements(root: Path) -> tuple[list[tuple[Path, str]], list[str]]:
    replacements: list[tuple[Path, str]] = []
    reports: list[str] = []
    patterns = (
        re.compile(r"(?i)\b[A-Z]:\\" + "Users\\" + r"[^\s'\"`]+"),
        re.compile(r"(?i)/" + "home/" + r"[^\s'\"`]+|/" + "Users/" + r"[^\s'\"`]+"),
    )
    for source in read_files(root):
        matches = [match.group(0) for pattern in patterns for match in pattern.finditer(source.content)]
        if not matches:
            continue
        content = source.content
        for match in matches:
            candidate = Path(match)
            try:
                relative = candidate.resolve().relative_to(root.resolve()).as_posix()
            except (OSError, ValueError):
                reports.append(f"Could not safely replace {match} in {source.path}.")
                continue
            content = content.replace(match, relative or ".")
        if content != source.content:
            replacements.append((root / source.path, content))
    return replacements, reports


def fix(path: str | Path, *, dry_run: bool = False, force: bool = False) -> FixResult:
    root = Path(path).expanduser().resolve()
    before = scan(root)
    kind, files = _kind_and_files(root)
    actions: list[FixAction] = []
    reports: list[str] = []

    def plan(relative: str, content: str, detail: str) -> None:
        target = root / relative
        if target.exists() and not force:
            reports.append(f"Skipped existing {relative}; use --force to overwrite it.")
            return
        if target.exists() and target.read_text(encoding="utf-8") == content:
            return
        actions.append(FixAction(relative, "write", detail))
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

    version = _version(root, files, kind)
    if version:
        plan(version[0], version[1] + "\n", "pin the detected runtime")
    else:
        reports.append("Could not infer a runtime version; add a runtime pin manually.")

    if "dockerfile" not in files:
        plan("Dockerfile", _dockerfile("node" if kind == "node" else "python"), "generate a Dockerfile template")
    if ".env.example" not in files:
        names = _environment_names(root)
        plan(".env.example", "".join(f"{name}=\n" for name in names) or "# Add project settings here\n", "generate redacted environment settings")
    if not any(name.startswith("readme") for name in files):
        plan("README.md", _readme("node" if kind == "node" else "python"), "generate Setup, Run, and Test instructions")
    has_test = before.checks[4].passed
    if not has_test:
        if "makefile" not in files:
            plan("Makefile", "test:\n\tpytest\n", "add a test command stub")
        else:
            reports.append("Missing test command: add a test target to the existing Makefile.")
    if not before.checks[1].passed:
        command = "npm install" if kind == "node" else "python -m pip freeze > requirements.txt"
        reports.append(f"Missing lockfile; run this exact command when dependencies are available: {command}")

    replacements, path_reports = _safe_relative_replacements(root)
    reports.extend(path_reports)
    for target, content in replacements:
        relative = target.relative_to(root).as_posix()
        if not force:
            reports.append(f"Safe relative-path replacement available in {relative}; use --force to apply it.")
        elif not dry_run:
            target.write_text(content, encoding="utf-8")
            actions.append(FixAction(relative, "update", "replace a safe project-relative absolute path"))
        else:
            actions.append(FixAction(relative, "update", "replace a safe project-relative absolute path"))

    after = scan(root) if not dry_run else before
    return FixResult(before, after, tuple(actions), tuple(reports))
