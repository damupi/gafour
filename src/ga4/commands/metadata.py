from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal, Optional

import typer
from google.api_core import exceptions as google_exceptions  # type: ignore[import-untyped]

from ga4.auth import build_data_client
from ga4.config import load_config
from ga4.errors import AuthError, GA4CLIError, NetworkError, ValidationError
from ga4.models.metadata import (
    CompatibilityStatus,
    DimensionMetadata,
    MetricMetadata,
)
from ga4.output import OutputFormat, print_error, render

metadata_app = typer.Typer(name="metadata", help="Retrieve GA4 dimensions and metrics metadata.")


@metadata_app.command("dimensions")
def metadata_dimensions(
    property_id: Annotated[
        Optional[str],
        typer.Option("--property-id", "-p", help="The numeric GA4 property ID."),
    ] = None,
    search: Annotated[
        Optional[str],
        typer.Option("--search", "-s", help="Filter results by this search term (case-insensitive)."),
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
    """List available dimensions for a GA4 property."""
    try:
        config = load_config()
        effective_property_id = property_id or config.default_property_id
        if not effective_property_id:
            err = ValidationError(
                message="--property-id is required.",
                hint="Pass --property-id or set GA4_PROPERTY_ID in your environment.",
                recovery_command="ga4 config set default_property_id <property-id>",
            )
            print_error(err)
            raise typer.Exit(err.exit_code)

        client = build_data_client(config)
        response = client.get_metadata(name=f"properties/{effective_property_id}/metadata")

        dims: list[DimensionMetadata] = []
        for d in getattr(response, "dimensions", []):
            dims.append(
                DimensionMetadata(
                    api_name=d.api_name,
                    ui_name=d.ui_name,
                    description=d.description,
                    deprecated_api_names=list(getattr(d, "deprecated_api_names", [])),
                    custom_definition=bool(getattr(d, "custom_definition", False)),
                    category=getattr(d, "category", None) or None,
                )
            )

        if search:
            term = search.lower()
            dims = [
                d
                for d in dims
                if term in d.api_name.lower()
                or term in d.ui_name.lower()
                or term in d.description.lower()
            ]

        rows = [
            {
                "API Name": d.api_name,
                "UI Name": d.ui_name,
                "Category": d.category or "",
                "Custom": str(d.custom_definition),
                "Description": d.description,
            }
            for d in dims
        ]
        columns = ["API Name", "UI Name", "Category", "Custom", "Description"]
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
            message="Permission denied fetching metadata.",
            hint="Ensure your credentials have the Analytics Read & Analyze permission.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(message=f"API call failed: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)


@metadata_app.command("metrics")
def metadata_metrics(
    property_id: Annotated[
        Optional[str],
        typer.Option("--property-id", "-p", help="The numeric GA4 property ID."),
    ] = None,
    search: Annotated[
        Optional[str],
        typer.Option("--search", "-s", help="Filter results by this search term (case-insensitive)."),
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
    """List available metrics for a GA4 property."""
    try:
        config = load_config()
        effective_property_id = property_id or config.default_property_id
        if not effective_property_id:
            err = ValidationError(
                message="--property-id is required.",
                hint="Pass --property-id or set GA4_PROPERTY_ID in your environment.",
                recovery_command="ga4 config set default_property_id <property-id>",
            )
            print_error(err)
            raise typer.Exit(err.exit_code)

        client = build_data_client(config)
        response = client.get_metadata(name=f"properties/{effective_property_id}/metadata")

        mets: list[MetricMetadata] = []
        for m in getattr(response, "metrics", []):
            mets.append(
                MetricMetadata(
                    api_name=m.api_name,
                    ui_name=m.ui_name,
                    description=m.description,
                    type_=str(getattr(m, "type_", None) or getattr(m, "type", None)) or None,
                    expression=getattr(m, "expression", None) or None,
                    deprecated_api_names=list(getattr(m, "deprecated_api_names", [])),
                    custom_definition=bool(getattr(m, "custom_definition", False)),
                    category=getattr(m, "category", None) or None,
                )
            )

        if search:
            term = search.lower()
            mets = [
                m
                for m in mets
                if term in m.api_name.lower()
                or term in m.ui_name.lower()
                or term in m.description.lower()
            ]

        rows = [
            {
                "API Name": m.api_name,
                "UI Name": m.ui_name,
                "Category": m.category or "",
                "Type": m.type_ or "",
                "Custom": str(m.custom_definition),
                "Description": m.description,
            }
            for m in mets
        ]
        columns = ["API Name", "UI Name", "Category", "Type", "Custom", "Description"]
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
            message="Permission denied fetching metadata.",
            hint="Ensure your credentials have the Analytics Read & Analyze permission.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(message=f"API call failed: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)


CompatibilityFilter = Literal["compatible", "incompatible", "all"]


@metadata_app.command("compatibility")
def metadata_compatibility(
    property_id: Annotated[
        Optional[str],
        typer.Option("--property-id", "-p", help="The numeric GA4 property ID."),
    ] = None,
    dimensions: Annotated[
        Optional[list[str]],
        typer.Option("--dimensions", "-d", help="Dimension API names to check (repeatable)."),
    ] = None,
    metrics: Annotated[
        Optional[list[str]],
        typer.Option("--metrics", "-m", help="Metric API names to check (repeatable)."),
    ] = None,
    filter_compat: Annotated[
        CompatibilityFilter,
        typer.Option("--filter", help="Filter results: compatible, incompatible, or all."),
    ] = "all",
    format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", help="Output format."),
    ] = OutputFormat.JSON,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write output to file."),
    ] = None,
) -> None:
    """Check compatibility of dimensions and metrics for a GA4 property."""
    try:
        config = load_config()
        effective_property_id = property_id or config.default_property_id
        if not effective_property_id:
            err = ValidationError(
                message="--property-id is required.",
                hint="Pass --property-id or set GA4_PROPERTY_ID in your environment.",
                recovery_command="ga4 config set default_property_id <property-id>",
            )
            print_error(err)
            raise typer.Exit(err.exit_code)

        from google.analytics.data_v1beta.types import (  # type: ignore[import-untyped]
            CheckCompatibilityRequest,
            Dimension,
            Metric,
        )

        api_request = CheckCompatibilityRequest(
            property=f"properties/{effective_property_id}",
            dimensions=[Dimension(name=d) for d in (dimensions or [])],
            metrics=[Metric(name=m) for m in (metrics or [])],
        )

        client = build_data_client(config)
        response = client.check_compatibility(request=api_request)

        rows: list[dict[str, str]] = []

        for dc in getattr(response, "dimension_compatibilities", []):
            dim_meta = dc.dimension_metadata
            compat = str(getattr(dc, "compatibility", "COMPATIBILITY_UNSPECIFIED"))
            if filter_compat == "compatible" and compat != "COMPATIBLE":
                continue
            if filter_compat == "incompatible" and compat != "INCOMPATIBLE":
                continue
            rows.append(
                {
                    "Type": "dimension",
                    "API Name": getattr(dim_meta, "api_name", ""),
                    "UI Name": getattr(dim_meta, "ui_name", ""),
                    "Compatibility": compat,
                }
            )

        for mc in getattr(response, "metric_compatibilities", []):
            met_meta = mc.metric_metadata
            compat = str(getattr(mc, "compatibility", "COMPATIBILITY_UNSPECIFIED"))
            if filter_compat == "compatible" and compat != "COMPATIBLE":
                continue
            if filter_compat == "incompatible" and compat != "INCOMPATIBLE":
                continue
            rows.append(
                {
                    "Type": "metric",
                    "API Name": getattr(met_meta, "api_name", ""),
                    "UI Name": getattr(met_meta, "ui_name", ""),
                    "Compatibility": compat,
                }
            )

        columns = ["Type", "API Name", "UI Name", "Compatibility"]
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
            message="Permission denied checking compatibility.",
            hint="Ensure your credentials have the Analytics Read & Analyze permission.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.InvalidArgument as exc:
        err = ValidationError(message=f"Invalid compatibility request: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(message=f"API call failed: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
