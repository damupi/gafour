from __future__ import annotations

from typing import Annotated, Optional

import typer

from ga4x import __version__
from ga4x.commands.accounts import accounts_app
from ga4x.commands.audiences import audiences_app
from ga4x.commands.auth import auth_app
from ga4x.commands.config import config_app
from ga4x.commands.custom_dimensions import custom_dimensions_app
from ga4x.commands.custom_metrics import custom_metrics_app
from ga4x.commands.datastreams import datastreams_app
from ga4x.commands.events import events_app
from ga4x.commands.key_events import key_events_app
from ga4x.commands.metadata import metadata_app
from ga4x.commands.properties import properties_app
from ga4x.commands.realtime import realtime_app
from ga4x.commands.reports import reports_app

app = typer.Typer(
    name="ga4",
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
        typer.echo(f"ga4 version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
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
