"""Typer/Rich command-line interface for rebuildable."""

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
from .fixer import fix as run_fix
from .verifier import verify as run_verify


def _plain_scan(result: object) -> None:
    payload = result.to_dict()  # type: ignore[attr-defined]
    print(f"{'#':<3} {'Check':<24} {'Status':<6} {'Reason':<60} Fix hint")
    for check in payload["checks"]:
        print(
            f"{check['check']:<3} {check['name']:<24} {check['status']:<6} "
            f"{check['reason']:<60} {check['fix_hint']}"
        )
    print(f"Score: {payload['score']}/{payload['total']}")


def _render_scan(result: object, as_json: bool = False) -> None:
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


def fix_command(path: str, dry_run: bool = False, force: bool = False) -> int:
    try:
        fixed = run_fix(path, dry_run=dry_run, force=force)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(f"Before: {fixed.before.score}/8")
    if fixed.actions:
        print("Planned changes:" if dry_run else "Changes:")
        for action in fixed.actions:
            print(f"- {action.action} {action.path}: {action.detail}")
    else:
        print("No file changes needed.")
    for report in fixed.reports:
        print(f"- Note: {report}")
    print(f"After: {fixed.after.score}/8")
    return 0 if fixed.after.score == 8 else 1


def verify_command(path: str) -> int:
    try:
        passed, output = run_verify(path)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(output)
    return 0 if passed else 1


if typer is not None:
    app = typer.Typer(add_completion=False, help="Check whether a project can be rebuilt on a clean Linux machine.")

    @app.command("scan")
    def scan_cli(
        path: str = typer.Argument(".", help="Project directory to scan."),
        as_json: bool = typer.Option(False, "--json", flag_value=True, help="Print the scan as JSON."),
    ) -> NoReturn:
        raise typer.Exit(scan_command(path, as_json))

    @app.command("fix")
    def fix_cli(
        path: str = typer.Argument(".", help="Project directory to repair."),
        dry_run: bool = typer.Option(False, "--dry-run", help="Only print planned changes."),
        force: bool = typer.Option(False, "--force", help="Allow overwriting existing files."),
    ) -> NoReturn:
        raise typer.Exit(fix_command(path, dry_run, force))

    @app.command("verify")
    def verify_cli(path: str = typer.Argument(".", help="Project directory to verify.")) -> NoReturn:
        raise typer.Exit(verify_command(path))
else:
    app = None


def main() -> None:
    if app is not None:
        app()
        return
    args = sys.argv[1:]
    if not args or args[0] not in {"scan", "fix", "verify"}:
        print("Usage: rebuildable scan|fix|verify <path> [--json|--dry-run|--force]", file=sys.stderr)
        raise SystemExit(2)
    path = "."
    as_json = "--json" in args
    dry_run = "--dry-run" in args
    force = "--force" in args
    positional = [item for item in args[1:] if not item.startswith("-")]
    if positional:
        path = positional[0]
    if args[0] == "fix":
        raise SystemExit(fix_command(path, dry_run, force))
    if args[0] == "verify":
        raise SystemExit(verify_command(path))
    raise SystemExit(scan_command(path, as_json))
