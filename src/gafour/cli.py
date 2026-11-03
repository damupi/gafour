from __future__ import annotations

import json
from typing import Annotated

import typer

from gafour import __version__
from gafour.commands.accounts import accounts_app
from gafour.commands.audiences import audiences_app
from gafour.commands.auth import auth_app
from gafour.commands.config import config_app
from gafour.commands.custom_dimensions import custom_dimensions_app
from gafour.commands.custom_metrics import custom_metrics_app
from gafour.commands.datastreams import datastreams_app
from gafour.commands.events import events_app
from gafour.commands.key_events import key_events_app
from gafour.commands.metadata import metadata_app
from gafour.commands.properties import properties_app
from gafour.commands.realtime import realtime_app
from gafour.commands.reports import reports_app
from gafour.update import (
    UpgradeError,
    install_info,
    installed_version,
    is_newer,
    latest_release,
    pending_notice,
    perform_upgrade,
    upgrade_command,
)

app = typer.Typer(
    name="gafour",
    help="Google Analytics 4 CLI — manage accounts, properties, and run reports.",
    no_args_is_help=True,
)

app.add_typer(accounts_app, name="accounts")
app.add_typer(properties_app, name="properties")
app.add_typer(datastreams_app, name="datastreams")
app.add_typer(reports_app, name="reports")
app.add_typer(realtime_app, name="realtime")
app.add_typer(metadata_app, name="metadata")
app.add_typer(key_events_app, name="key-events")
app.add_typer(custom_dimensions_app, name="custom-dimensions")
app.add_typer(custom_metrics_app, name="custom-metrics")
app.add_typer(audiences_app, name="audiences")
app.add_typer(events_app, name="events")
app.add_typer(auth_app, name="auth")
app.add_typer(config_app, name="config")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"gafour {__version__}")
        raise typer.Exit()


def _show_update_notice() -> None:
    """Print a best-effort cached notice without affecting command success."""
    try:
        if notice := pending_notice():
            typer.echo(f"\n{notice}", err=True)
    except Exception:
        pass


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            help="Print the CLI version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """Google Analytics 4 CLI."""
    if ctx.invoked_subcommand not in (None, "version", "upgrade"):
        ctx.call_on_close(_show_update_notice)


@app.command("version")
def version_command(as_json: bool = typer.Option(False, "--json")) -> None:
    """Show the installed version and latest stable GitHub release."""
    current = installed_version() or __version__
    latest = latest_release()
    available = is_newer(latest, current)
    command = upgrade_command(latest) if latest and available else None
    result = {
        "installed": current,
        "latest": latest,
        "update_available": available,
        "upgrade_command": command,
    }
    if as_json:
        typer.echo(json.dumps(result, indent=2))
        return
    typer.echo(f"Installed: {current}")
    typer.echo(f"Latest: {latest or 'unknown'}")
    typer.echo(f"Update available: {'yes' if available else 'no'}")
    if command:
        typer.echo(f"To upgrade, run: {command}")


@app.command("upgrade")
def upgrade(yes: bool = typer.Option(False, "--yes", "-y")) -> None:
    """Upgrade gafour to the latest stable GitHub release."""
    current = installed_version() or __version__
    latest = latest_release()
    if latest is None:
        typer.echo("Could not determine the latest gafour release from GitHub.", err=True)
        raise typer.Exit(1)
    if not is_newer(latest, current):
        typer.echo(f"gafour is already up to date ({current}; latest release {latest}).")
        return

    command = upgrade_command(latest)
    if install_info()["kind"] == "editable":
        typer.echo("Editable install detected; gafour will not modify your checkout.")
        typer.echo(f"Update it with: {command}")
        return

    typer.echo(f"gafour {current} → {latest}")
    typer.echo(f"Will run: {command}")
    if not yes and not typer.confirm("Proceed with the upgrade?"):
        typer.echo("Upgrade cancelled.")
        return
    try:
        result = perform_upgrade(latest)
    except UpgradeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    if output := (result.stdout or "").strip():
        typer.echo(output)
    typer.echo(f"Upgraded gafour to {latest}.")
