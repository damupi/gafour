from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Optional

import typer
from google.api_core import exceptions as google_exceptions  # type: ignore[import-untyped]

from gafour.auth import build_admin_client
from gafour.config import load_config
from gafour.errors import AuthError, GA4CLIError, NetworkError, ValidationError
from gafour.models.event import EventCreateRule
from gafour.output import OutputFormat, print_error, render, render_json_list

events_app = typer.Typer(name="events", help="Manage GA4 event create rules.")


def _rule_to_dict(rule: EventCreateRule) -> dict[str, str]:
    """Convert an EventCreateRule model to a flat dict for rendering."""
    return {
        "Rule ID": rule.rule_id(),
        "Destination Event": rule.destination_event,
        "Source Copy Params": str(rule.source_copy_parameters),
        "Conditions Count": str(len(rule.event_conditions)),
        "Resource Name": rule.name,
    }


@events_app.command("list")
def events_list(
    property_id: Annotated[str, typer.Argument(help="The numeric GA4 property ID.")],
    stream_id: Annotated[str, typer.Argument(help="The numeric data stream ID.")],
    format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", help="Output format."),
    ] = OutputFormat.JSON,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write output to file."),
    ] = None,
) -> None:
    """List all event create rules for a GA4 data stream."""
    try:
        config = load_config()
        client = build_admin_client(config)
        parent = f"properties/{property_id}/dataStreams/{stream_id}"
        pager = client.list_event_create_rules(parent=parent)

        rules: list[EventCreateRule] = []
        for r in pager:
            conditions_raw = getattr(r, "event_conditions", [])
            conditions: list[dict[str, Any]] = []
            for c in conditions_raw:
                if hasattr(c, "__class__") and hasattr(type(c), "to_dict"):
                    conditions.append(type(c).to_dict(c))
                else:
                    conditions.append(dict(vars(c)) if hasattr(c, "__dict__") else {})

            rules.append(
                EventCreateRule(
                    name=r.name,
                    destination_event=r.destination_event,
                    event_conditions=conditions,
                    source_copy_parameters=bool(getattr(r, "source_copy_parameters", False)),
                )
            )

        if format == OutputFormat.JSON:
            result = render_json_list(rules)
        else:
            result = render([_rule_to_dict(rule) for rule in rules], format, ["Rule ID", "Destination Event", "Source Copy Params", "Conditions Count"])
        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except google_exceptions.PermissionDenied as exc:
        err = AuthError(
            message=f"Permission denied listing event create rules for stream '{stream_id}'.",
            hint="Ensure your credentials have the Analytics Edit permission.",
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


@events_app.command("create")
def events_create() -> None:
    """Create a new event create rule. (Not yet implemented)"""
    typer.echo("Not yet implemented")
    raise typer.Exit(0)


@events_app.command("delete")
def events_delete() -> None:
    """Delete an event create rule. (Not yet implemented)"""
    typer.echo("Not yet implemented")
    raise typer.Exit(0)
