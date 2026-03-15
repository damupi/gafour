from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from google.api_core import exceptions as google_exceptions  # type: ignore[import-untyped]

from ga4.auth import build_admin_client
from ga4.config import load_config
from ga4.errors import AuthError, GA4CLIError, NetworkError, PropertyNotFoundError, ValidationError
from ga4.models.property import Property
from ga4.output import OutputFormat, print_error, render

properties_app = typer.Typer(name="properties", help="Manage GA4 properties.")


def _property_to_dict(prop: Property) -> dict[str, str]:
    """Convert a Property model to a flat dict for rendering."""
    return {
        "Property ID": prop.property_id(),
        "Name": prop.display_name,
        "Time Zone": prop.time_zone,
        "Currency": prop.currency_code,
        "Industry": prop.industry_category or "",
        "Parent": prop.parent or "",
        "Created": prop.create_time or "",
    }


@properties_app.command("list")
def properties_list(
    account_id: Annotated[
        Optional[str],
        typer.Option("--account-id", "-a", help="The numeric account ID to filter by."),
    ] = None,
    format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", help="Output format."),
    ] = OutputFormat.JSON,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write output to file."),
    ] = None,
) -> None:
    """List GA4 properties, optionally filtered to a specific account."""
    if account_id is None:
        err = ValidationError(
            message="--account-id is required.",
            hint="Provide the numeric account ID to list its properties.",
            recovery_command="ga4 accounts list",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)

    try:
        from google.analytics.admin_v1beta.types import ListPropertiesRequest  # type: ignore[import-untyped]

        config = load_config()
        client = build_admin_client(config)
        request = ListPropertiesRequest(filter=f"parent:accounts/{account_id}")
        pager = client.list_properties(request=request)
        props = [
            Property(
                name=p.name,
                display_name=p.display_name,
                time_zone=p.time_zone,
                currency_code=p.currency_code,
                industry_category=str(p.industry_category) if p.industry_category else None,
                create_time=str(p.create_time) if p.create_time else None,
                update_time=str(p.update_time) if p.update_time else None,
                parent=p.parent or None,
            )
            for p in pager
        ]
        rows = [_property_to_dict(p) for p in props]
        columns = ["Property ID", "Name", "Time Zone", "Currency"]
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
            message=f"Permission denied listing properties for account '{account_id}'.",
            hint="Ensure your credentials have the Analytics Read & Analyze permission.",
            recovery_command="ga4 auth status",
        )
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


@properties_app.command("get")
def properties_get(
    property_id: Annotated[str, typer.Argument(help="The numeric property ID.")],
    format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", help="Output format."),
    ] = OutputFormat.JSON,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write output to file."),
    ] = None,
) -> None:
    """Get details for a specific GA4 property."""
    try:
        config = load_config()
        client = build_admin_client(config)
        p = client.get_property(name=f"properties/{property_id}")
        prop = Property(
            name=p.name,
            display_name=p.display_name,
            time_zone=p.time_zone,
            currency_code=p.currency_code,
            industry_category=str(p.industry_category) if p.industry_category else None,
            create_time=str(p.create_time) if p.create_time else None,
            update_time=str(p.update_time) if p.update_time else None,
            parent=p.parent or None,
        )
        rows = [_property_to_dict(prop)]
        columns = ["Property ID", "Name", "Time Zone", "Currency", "Industry", "Parent", "Created"]
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
            message=f"Permission denied accessing property '{property_id}'.",
            hint="Ensure your credentials have access to this property.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.NotFound as exc:
        err = PropertyNotFoundError(property_id=property_id)
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.InvalidArgument as exc:
        err = ValidationError(message=f"Invalid property ID '{property_id}': {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(message=f"API call failed: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)


@properties_app.command("create")
def properties_create() -> None:
    """Create a new GA4 property. (Not yet implemented)"""
    typer.echo("Not yet implemented")
    raise typer.Exit(0)


@properties_app.command("update")
def properties_update() -> None:
    """Update a GA4 property. (Not yet implemented)"""
    typer.echo("Not yet implemented")
    raise typer.Exit(0)


@properties_app.command("delete")
def properties_delete(
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview deletion without making changes."),
    ] = False,
) -> None:
    """Delete a GA4 property. (Not yet implemented)"""
    typer.echo("Not yet implemented")
    raise typer.Exit(0)


@properties_app.command("clone")
def properties_clone(
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview cloning without making changes."),
    ] = False,
) -> None:
    """Clone a GA4 property. (Not yet implemented)"""
    typer.echo("Not yet implemented")
    raise typer.Exit(0)
