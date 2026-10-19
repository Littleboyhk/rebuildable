"""Typer/Rich command-line interface for rebuildable."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import NoReturn

try:
    import typer
    from rich.console import Console
    from rich.table import Table
except ImportError:  # Keep the scanner usable before an offline dev install.
    typer = None  # type: ignore[assignment]
    Console = None  # type: ignore[assignment,misc]
    Table = None  # type: ignore[assignment,misc]

from .scanner import scan as run_scan


def _plain_scan(result: object) -> None:
    payload = result.to_dict()  # type: ignore[attr-defined]
    print(f"{'#':<3} {'CHECK':<24} {'STATUS':<6} REASON")
    for check in payload["checks"]:
        print(f"{check['check']:<3} {check['name']:<24} {check['status']:<6} {check['reason']}")
    print(f"Score: {payload['score']}/{payload['total']}")


def _render_scan(result: object, as_json: bool) -> None:
    payload = result.to_dict()  # type: ignore[attr-defined]
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    if Console is None or Table is None:
        _plain_scan(result)
        return
    table = Table("#", "Check", "Status", "Reason", "Fix hint")
    for check in payload["checks"]:
        table.add_row(str(check["check"]), check["name"], check["status"], check["reason"], check["fix_hint"])
    Console().print(table)
    Console().print(f"Score: {payload['score']}/{payload['total']}")


def scan_command(path: str, as_json: bool = False) -> int:
    try:
        result = run_scan(path)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    _render_scan(result, as_json)
    return 0 if result.score == 8 else 1


if typer is not None:
    app = typer.Typer(add_completion=False, help="Check whether a project can be rebuilt on a clean Linux machine.")

    @app.command("scan")
    def scan_cli(
        path: str = typer.Argument(".", help="Project directory to scan."),
        as_json: bool = typer.Option(False, "--json", help="Print the scan as JSON."),
    ) -> NoReturn:
        raise typer.Exit(scan_command(path, as_json))
else:
    app = None


def main() -> None:
    if app is not None:
        app()
        return
    args = sys.argv[1:]
    if not args or args[0] != "scan":
        print("Usage: rebuildable scan <path> [--json]", file=sys.stderr)
        raise SystemExit(2)
    path = "."
    as_json = "--json" in args
    positional = [item for item in args[1:] if not item.startswith("-")]
    if positional:
        path = positional[0]
    raise SystemExit(scan_command(path, as_json))
