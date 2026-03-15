from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from google.api_core import exceptions as google_exceptions  # type: ignore[import-untyped]

from ga4x.auth import build_admin_client
from ga4x.config import load_config
from ga4x.errors import AuthError, GA4CLIError, NetworkError, ValidationError
from ga4x.models.custom_dimension import CustomDimension, DimensionScope
from ga4x.output import OutputFormat, print_error, render, render_json_list

custom_dimensions_app = typer.Typer(
    name="custom-dimensions", help="Manage GA4 custom dimensions."
)


def _custom_dim_to_dict(dim: CustomDimension) -> dict[str, str]:
    """Convert a CustomDimension model to a flat dict for rendering."""
    return {
        "Parameter Name": dim.parameter_name,
        "Display Name": dim.display_name,
        "Scope": dim.scope.value,
        "Description": dim.description or "",
        "Disallow Ads": str(dim.disallow_ads_personalization),
        "Resource Name": dim.name,
    }


@custom_dimensions_app.command("list")
def custom_dimensions_list(
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
    """List all custom dimensions for a GA4 property."""
    try:
        config = load_config()
        client = build_admin_client(config)
        pager = client.list_custom_dimensions(parent=f"properties/{property_id}")

        dims: list[CustomDimension] = []
        for cd in pager:
            scope_raw = getattr(cd, "scope", None)
            try:
                scope = DimensionScope(str(scope_raw)) if scope_raw else DimensionScope.DIMENSION_SCOPE_UNSPECIFIED
            except ValueError:
                scope = DimensionScope.DIMENSION_SCOPE_UNSPECIFIED

            dims.append(
                CustomDimension(
                    name=cd.name,
                    parameter_name=cd.parameter_name,
                    display_name=cd.display_name,
                    description=getattr(cd, "description", None) or None,
                    scope=scope,
                    disallow_ads_personalization=bool(
                        getattr(cd, "disallow_ads_personalization", False)
                    ),
                )
            )

        if format == OutputFormat.JSON:
            result = render_json_list(dims)
        else:
            result = render([_custom_dim_to_dict(d) for d in dims], format, ["Parameter Name", "Display Name", "Scope", "Description"])
        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except google_exceptions.PermissionDenied as exc:
        err = AuthError(
            message=f"Permission denied listing custom dimensions for property '{property_id}'.",
            hint="Ensure your credentials have the Analytics Read & Analyze permission.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.NotFound as exc:
        from ga4x.errors import PropertyNotFoundError

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
