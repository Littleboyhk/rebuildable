"""The intentionally simple eight-point score."""

from __future__ import annotations

from collections.abc import Iterable

from .models import CheckResult


def score_checks(checks: Iterable[CheckResult]) -> int:
    """Return one point for each passing check."""

    return sum(check.passed for check in checks)
