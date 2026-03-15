from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from google.api_core import exceptions as google_exceptions  # type: ignore[import-untyped]

from gafour.auth import build_admin_client
from gafour.config import load_config
from gafour.errors import AuthError, GA4CLIError, NetworkError, ValidationError
from gafour.models.custom_metric import CustomMetric, MeasurementUnit, MetricScope
from gafour.output import OutputFormat, print_error, render, render_json_list

custom_metrics_app = typer.Typer(name="custom-metrics", help="Manage GA4 custom metrics.")


def _custom_metric_to_dict(metric: CustomMetric) -> dict[str, str]:
    """Convert a CustomMetric model to a flat dict for rendering."""
    return {
        "Parameter Name": metric.parameter_name,
        "Display Name": metric.display_name,
        "Scope": metric.scope.value,
        "Unit": metric.measurement_unit.value,
        "Description": metric.description or "",
        "Resource Name": metric.name,
    }


@custom_metrics_app.command("list")
def custom_metrics_list(
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
    """List all custom metrics for a GA4 property."""
    try:
        config = load_config()
        client = build_admin_client(config)
        pager = client.list_custom_metrics(parent=f"properties/{property_id}")

        metrics: list[CustomMetric] = []
        for cm in pager:
            scope_raw = getattr(cm, "scope", None)
            try:
                scope = MetricScope(str(scope_raw)) if scope_raw else MetricScope.METRIC_SCOPE_UNSPECIFIED
            except ValueError:
                scope = MetricScope.METRIC_SCOPE_UNSPECIFIED

            unit_raw = getattr(cm, "measurement_unit", None)
            try:
                unit = MeasurementUnit(str(unit_raw)) if unit_raw else MeasurementUnit.MEASUREMENT_UNIT_UNSPECIFIED
            except ValueError:
                unit = MeasurementUnit.MEASUREMENT_UNIT_UNSPECIFIED

            metrics.append(
                CustomMetric(
                    name=cm.name,
                    parameter_name=cm.parameter_name,
                    display_name=cm.display_name,
                    description=getattr(cm, "description", None) or None,
                    scope=scope,
                    measurement_unit=unit,
                    restricted_metric_type=list(getattr(cm, "restricted_metric_type", [])),
                )
            )

        if format == OutputFormat.JSON:
            result = render_json_list(metrics)
        else:
            result = render([_custom_metric_to_dict(m) for m in metrics], format, ["Parameter Name", "Display Name", "Scope", "Unit"])
        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except google_exceptions.PermissionDenied as exc:
        err = AuthError(
            message=f"Permission denied listing custom metrics for property '{property_id}'.",
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
