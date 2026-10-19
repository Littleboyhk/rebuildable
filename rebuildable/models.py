"""Small typed objects shared by the scanner and its CLI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SourceFile:
    """A readable text file relative to the project root."""

    path: str
    content: str


@dataclass(frozen=True)
class CheckResult:
    """One of the eight user-facing checks."""

    number: int
    name: str
    passed: bool
    reason: str
    fix_hint: str

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"

    def to_dict(self) -> dict[str, Any]:
        return {
            "check": self.number,
            "name": self.name,
            "status": self.status,
            "reason": self.reason,
            "fix_hint": self.fix_hint,
        }


@dataclass(frozen=True)
class ScanResult:
    """Complete scan result, with a deliberately simple JSON shape."""

    root: Path
    checks: tuple[CheckResult, ...]

    @property
    def score(self) -> int:
        from .scoring import score_checks

        return score_checks(self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.root),
            "score": self.score,
            "total": len(self.checks),
            "checks": [check.to_dict() for check in self.checks],
        }


@dataclass(frozen=True)
class ScanContext:
    root: Path
    files: tuple[SourceFile, ...]
    kind: str
