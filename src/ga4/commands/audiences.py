from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from google.api_core import exceptions as google_exceptions  # type: ignore[import-untyped]

from ga4.auth import build_admin_client
from ga4.config import load_config
from ga4.errors import AuthError, GA4CLIError, NetworkError, ValidationError
from ga4.models.audience import Audience
from ga4.output import OutputFormat, print_error, render

audiences_app = typer.Typer(name="audiences", help="Manage GA4 audiences.")


def _audience_to_dict(audience: Audience) -> dict[str, str]:
    """Convert an Audience model to a flat dict for rendering."""
    return {
        "Audience ID": audience.audience_id(),
        "Display Name": audience.display_name,
        "Description": audience.description or "",
        "Membership Days": str(audience.membership_duration_days or ""),
        "Ads Personalization": str(audience.ads_personalization_enabled or ""),
        "Created": audience.create_time or "",
    }


@audiences_app.command("list")
def audiences_list(
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
    """List all audiences for a GA4 property."""
    try:
        config = load_config()
        client = build_admin_client(config)
        pager = client.list_audiences(parent=f"properties/{property_id}")

        aud_list: list[Audience] = []
        for a in pager:
            aud_list.append(
                Audience(
                    name=a.name,
                    display_name=a.display_name,
                    description=getattr(a, "description", None) or None,
                    membership_duration_days=getattr(a, "membership_duration_days", None) or None,
                    ads_personalization_enabled=getattr(a, "ads_personalization_enabled", None),
                    create_time=str(a.create_time) if a.create_time else None,
                )
            )

        rows = [_audience_to_dict(a) for a in aud_list]
        columns = ["Audience ID", "Display Name", "Description", "Membership Days"]
        result = render(rows, format, columns)
        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except google_exceptions.PermissionDenied as exc:
        err = AuthError(
            message=f"Permission denied listing audiences for property '{property_id}'.",
            hint="Ensure your credentials have the Analytics Edit permission.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.NotFound as exc:
        from ga4.errors import PropertyNotFoundError

        err = PropertyNotFoundError(property_id=property_id)
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(message=f"API call failed: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)


@audiences_app.command("get")
def audiences_get(
    property_id: Annotated[str, typer.Argument(help="The numeric GA4 property ID.")],
    audience_id: Annotated[str, typer.Argument(help="The numeric audience ID.")],
    format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", help="Output format."),
    ] = OutputFormat.JSON,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write output to file."),
    ] = None,
) -> None:
    """Get details for a specific GA4 audience."""
    try:
        config = load_config()
        client = build_admin_client(config)
        a = client.get_audience(
            name=f"properties/{property_id}/audiences/{audience_id}"
        )
        audience = Audience(
            name=a.name,
            display_name=a.display_name,
            description=getattr(a, "description", None) or None,
            membership_duration_days=getattr(a, "membership_duration_days", None) or None,
            ads_personalization_enabled=getattr(a, "ads_personalization_enabled", None),
            create_time=str(a.create_time) if a.create_time else None,
        )
        rows = [_audience_to_dict(audience)]
        columns = [
            "Audience ID",
            "Display Name",
            "Description",
            "Membership Days",
            "Ads Personalization",
            "Created",
        ]
        result = render(rows, format, columns)
        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except google_exceptions.PermissionDenied as exc:
        err = AuthError(
            message=f"Permission denied accessing audience '{audience_id}'.",
            hint="Ensure your credentials have the Analytics Edit permission.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.NotFound as exc:
        err = GA4CLIError(
            message=f"Audience 'properties/{property_id}/audiences/{audience_id}' not found."
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(message=f"API call failed: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)


@audiences_app.command("create")
def audiences_create() -> None:
    """Create a new GA4 audience. (Not yet implemented)"""
    typer.echo("Not yet implemented")
    raise typer.Exit(0)


@audiences_app.command("delete")
def audiences_delete() -> None:
    """Delete a GA4 audience. (Not yet implemented)"""
    typer.echo("Not yet implemented")
    raise typer.Exit(0)
