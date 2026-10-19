"""Run the scan and, when available, verify the Docker build and test command."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .files import read_files
from .scanner import scan


def _test_command(root: Path) -> str | None:
    files = {Path(item.path).name.lower(): item.content for item in read_files(root) if "/" not in item.path}
    package = files.get("package.json")
    if package:
        try:
            scripts = json.loads(package).get("scripts", {})
        except (json.JSONDecodeError, AttributeError):
            scripts = {}
        if isinstance(scripts, dict) and scripts.get("test"):
            return "npm test"
    if "pytest.ini" in files or "tox.ini" in files or "[tool.pytest" in files.get("pyproject.toml", "") or "[tool:pytest]" in files.get("setup.cfg", ""):
        return "pytest"
    if files.get("makefile") and any(line.startswith("test:") for line in files["makefile"].splitlines()):
        return "make test"
    return None


def verify(path: str | Path) -> tuple[bool, str]:
    root = Path(path).expanduser().resolve()
    result = scan(root)
    lines = [f"Scan: {result.score}/8"]
    docker = shutil.which("docker")
    if docker is None:
        lines.append("Docker not available, skipped")
        passed = result.score == 8
        lines.append("PASS" if passed else "FAIL")
        return passed, "\n".join(lines)

    image = "rebuildable-verify"
    build = subprocess.run([docker, "build", "--tag", image, str(root)], capture_output=True, text=True, check=False)
    if build.returncode != 0:
        lines.extend(["Docker build: FAIL", build.stderr.strip() or build.stdout.strip()])
        lines.append("FAIL")
        return False, "\n".join(line for line in lines if line)
    lines.append("Docker build: PASS")
    command = _test_command(root)
    if command is None:
        lines.append("Test command: FAIL (not found)")
        lines.append("FAIL")
        return False, "\n".join(lines)
    test = subprocess.run([docker, "run", "--rm", "--network=none", image, "sh", "-lc", command], capture_output=True, text=True, check=False)
    if test.returncode != 0:
        lines.extend([f"Test command ({command}): FAIL", test.stderr.strip() or test.stdout.strip()])
        lines.append("FAIL")
        return False, "\n".join(line for line in lines if line)
    lines.append(f"Test command ({command}): PASS")
    passed = result.score == 8
    lines.append("PASS" if passed else "FAIL (scan is below 8/8)")
    return passed, "\n".join(lines)
