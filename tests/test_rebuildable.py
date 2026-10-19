from __future__ import annotations

import shutil
from pathlib import Path

from rebuildable.fixer import fix
from rebuildable.scanner import scan


FIXTURES = Path(__file__).parent / "fixtures"


def test_perfect_fixture_scores_eight() -> None:
    result = scan(FIXTURES / "perfect-project")
    assert result.score == 8
    assert [item.status for item in result.checks] == ["PASS"] * 8


def test_broken_node_fixture_is_not_rebuildable() -> None:
    result = scan(FIXTURES / "broken-node-project")
    assert result.score < 8
    assert result.checks[1].passed is False


def test_broken_python_fixture_is_not_rebuildable() -> None:
    result = scan(FIXTURES / "broken-python-project")
    assert result.score < 8
    assert result.checks[2].passed is False


def test_fix_writes_missing_files_and_second_fix_is_idempotent(tmp_path: Path) -> None:
    project = tmp_path / "node-project"
    shutil.copytree(FIXTURES / "broken-node-project", project)
    first = fix(project)
    assert first.after.score > first.before.score
    assert (project / "Dockerfile").exists()
    assert (project / ".env.example").exists()
    second = fix(project)
    assert second.actions == ()


def test_dry_run_does_not_write(tmp_path: Path) -> None:
    project = tmp_path / "python-project"
    shutil.copytree(FIXTURES / "broken-python-project", project)
    planned = fix(project, dry_run=True)
    assert planned.actions
    assert not (project / "Dockerfile").exists()
    assert planned.before.score == planned.after.score
