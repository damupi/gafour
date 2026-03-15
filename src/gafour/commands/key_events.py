from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from google.api_core import exceptions as google_exceptions  # type: ignore[import-untyped]

from gafour.auth import build_admin_client
from gafour.config import load_config
from gafour.errors import AuthError, GA4CLIError, NetworkError, ValidationError
from gafour.models.key_event import CountingMethod, KeyEvent
from gafour.output import OutputFormat, print_error, render, render_json_list

key_events_app = typer.Typer(name="key-events", help="Manage GA4 key events.")


def _key_event_to_dict(event: KeyEvent) -> dict[str, str]:
    """Convert a KeyEvent model to a flat dict for rendering."""
    return {
        "Event Name": event.event_name,
        "Counting Method": event.counting_method.value,
        "Custom": str(event.custom),
        "Deletable": str(event.deletable),
        "Created": event.create_time or "",
        "Resource Name": event.name,
    }


@key_events_app.command("list")
def key_events_list(
    property_id: Annotated[str, typer.Argument(help="The numeric GA4 property ID.")],
    format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", help="Output format."),
    ] = OutputFormat.JSON,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write output to file."),
    ] = None,
) -> None:
    """List all key events for a GA4 property."""
    try:
        config = load_config()
        client = build_admin_client(config)
        pager = client.list_key_events(parent=f"properties/{property_id}")

        events: list[KeyEvent] = []
        for ke in pager:
            counting_raw = getattr(ke, "counting_method", None)
            try:
                counting = CountingMethod(str(counting_raw)) if counting_raw else CountingMethod.COUNTING_METHOD_UNSPECIFIED
            except ValueError:
                counting = CountingMethod.COUNTING_METHOD_UNSPECIFIED

            events.append(
                KeyEvent(
                    name=ke.name,
                    event_name=ke.event_name,
                    create_time=str(ke.create_time) if ke.create_time else None,
                    deletable=bool(getattr(ke, "deletable", False)),
                    custom=bool(getattr(ke, "custom", False)),
                    counting_method=counting,
                )
            )

        if format == OutputFormat.JSON:
            result = render_json_list(events)
        else:
            result = render([_key_event_to_dict(e) for e in events], format, ["Event Name", "Counting Method", "Custom", "Deletable", "Created"])
        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except google_exceptions.PermissionDenied as exc:
        err = AuthError(
            message=f"Permission denied listing key events for property '{property_id}'.",
            hint="Ensure your credentials have the Analytics Read & Analyze permission.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.NotFound as exc:
        from gafour.errors import PropertyNotFoundError

        err = PropertyNotFoundError(property_id=property_id)
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.InvalidArgument as exc:
        err = ValidationError(message=f"Invalid request: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(message=f"API call failed: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
