from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from google.api_core import exceptions as google_exceptions  # type: ignore[import-untyped]

from ga4.auth import build_data_client
from ga4.config import load_config
from ga4.errors import AuthError, GA4CLIError, NetworkError, ValidationError
from ga4.output import OutputFormat, print_error, render

realtime_app = typer.Typer(name="realtime", help="Run GA4 realtime reports.")


@realtime_app.command("run")
def realtime_run(
    property_id: Annotated[
        Optional[str],
        typer.Option("--property-id", "-p", help="The numeric GA4 property ID."),
    ] = None,
    metrics: Annotated[
        Optional[list[str]],
        typer.Option("--metrics", "-m", help="Metric API names (repeatable)."),
    ] = None,
    dimensions: Annotated[
        Optional[list[str]],
        typer.Option("--dimensions", "-d", help="Dimension API names (repeatable)."),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", help="Maximum number of rows."),
    ] = 10000,
    format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", help="Output format."),
    ] = OutputFormat.JSON,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write output to file."),
    ] = None,
) -> None:
    """Run a GA4 realtime report showing current active users and events."""
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

        effective_metrics = metrics or ["activeUsers"]
        effective_dimensions = dimensions or []

        from google.analytics.data_v1beta.types import (  # type: ignore[import-untyped]
            Dimension,
            Metric,
            RunRealtimeReportRequest,
        )

        api_request = RunRealtimeReportRequest(
            property=f"properties/{effective_property_id}",
            dimensions=[Dimension(name=d) for d in effective_dimensions],
            metrics=[Metric(name=m) for m in effective_metrics],
            limit=limit,
        )

        client = build_data_client(config)
        response = client.run_realtime_report(request=api_request)

        rows: list[dict[str, str]] = []
        for row in getattr(response, "rows", []):
            record: dict[str, str] = {}
            for i, dim in enumerate(effective_dimensions):
                dim_values = getattr(row, "dimension_values", [])
                record[dim] = dim_values[i].value if i < len(dim_values) else ""
            for j, met in enumerate(effective_metrics):
                met_values = getattr(row, "metric_values", [])
                record[met] = met_values[j].value if j < len(met_values) else ""
            rows.append(record)

        columns = effective_dimensions + effective_metrics
        result = render(rows, format, columns if columns else None)
        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except google_exceptions.PermissionDenied as exc:
        err = AuthError(
            message="Permission denied running realtime report.",
            hint="Ensure your credentials have the Analytics Read & Analyze permission.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.InvalidArgument as exc:
        err = ValidationError(message=f"Invalid realtime report request: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(message=f"API call failed: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
