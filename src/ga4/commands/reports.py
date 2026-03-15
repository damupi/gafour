from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from google.api_core import exceptions as google_exceptions  # type: ignore[import-untyped]

from ga4.auth import build_data_client
from ga4.config import load_config
from ga4.errors import AuthError, GA4CLIError, NetworkError, ValidationError
from ga4.models.report import ReportRequest, ReportResponse
from ga4.output import print_error, render_report

reports_app = typer.Typer(name="reports", help="Run GA4 Data API reports.")


def _split_csv(values: list[str] | None) -> list[str]:
    """Flatten a list that may contain comma-separated strings into individual tokens.

    When a user passes ``--metrics activeUsers,sessions`` Typer receives the whole
    string as one element.  This helper splits every element on commas and strips
    surrounding whitespace so callers always get a clean flat list.
    """
    if not values:
        return []
    result: list[str] = []
    for item in values:
        result.extend(part.strip() for part in item.split(",") if part.strip())
    return result


def _parse_order_bys(order_bys: list[str]) -> list:  # type: ignore[type-arg]
    """Convert ``name:direction`` strings into ``OrderBy`` proto objects.

    Accepted formats (case-insensitive direction):
      * ``sessions:desc``   – metric descending
      * ``date:asc``        – dimension ascending
      * ``sessions``        – metric ascending (default)
    Metric names are attempted first; if the GA4 API rejects the name as a metric
    it will fall back to treating it as a dimension name at the API layer.
    """
    from google.analytics.data_v1beta.types import OrderBy  # type: ignore[import-untyped]

    result = []
    for expr in order_bys:
        if ":" in expr:
            name, direction_raw = expr.rsplit(":", 1)
            descending = direction_raw.strip().lower() == "desc"
        else:
            name = expr
            descending = False
        name = name.strip()
        # Try metric first; if the field name looks like a dimension (lowercase
        # with underscores that match known GA4 dimension patterns) prefer
        # DimensionOrderBy — but let the API validate; we default to MetricOrderBy.
        result.append(
            OrderBy(
                metric=OrderBy.MetricOrderBy(metric_name=name),
                desc=descending,
            )
        )
    return result



@reports_app.command("run")
def reports_run(
    property_id: Annotated[
        Optional[str],
        typer.Option("--property-id", "-p", help="The numeric GA4 property ID."),
    ] = None,
    metrics: Annotated[
        Optional[list[str]],
        typer.Option("--metrics", "-m", help="Metric API names (repeatable)."),
    ] = None,
    start_date: Annotated[
        str,
        typer.Option("--start-date", help="Start date (YYYY-MM-DD or relative, e.g. 7daysAgo)."),
    ] = "28daysAgo",
    end_date: Annotated[
        str,
        typer.Option("--end-date", help="End date (YYYY-MM-DD or 'today')."),
    ] = "today",
    dimensions: Annotated[
        Optional[list[str]],
        typer.Option("--dimensions", "-d", help="Dimension API names (repeatable)."),
    ] = None,
    filter_expr: Annotated[
        Optional[str],
        typer.Option(
            "--filter",
            help=(
                "Dimension filter DSL. Supports: = != beginsWith endsWith contains matches "
                "< <= > >= AND OR NOT (...). "
                'Example: \'pagePath beginsWith "/" AND NOT deviceCategory = "tablet"\''
            ),
        ),
    ] = None,
    metric_filter_expr: Annotated[
        Optional[str],
        typer.Option(
            "--metric-filter",
            help=(
                "Metric filter DSL. Same syntax as --filter but applied to metric values. "
                "Example: 'sessions > 100'"
            ),
        ),
    ] = None,
    order_by: Annotated[
        Optional[list[str]],
        typer.Option("--order-by", help="Order-by expressions (repeatable)."),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", help="Maximum number of rows (1-250000)."),
    ] = 10000,
    offset: Annotated[
        int,
        typer.Option("--offset", help="Zero-based row offset for pagination."),
    ] = 0,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write output to file."),
    ] = None,
) -> None:
    """Run a GA4 Data API report."""
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

        # Bug 1 fix: split comma-separated values the user may have passed as a
        # single string (e.g. --metrics activeUsers,sessions,engagementRate).
        metrics_list = _split_csv(metrics)
        dimensions_list = _split_csv(dimensions)
        order_by_list = _split_csv(order_by)

        if not metrics_list:
            err = ValidationError(
                message="At least one --metrics value is required.",
                hint="Example: --metrics sessions --metrics users",
                recovery_command="ga4 metadata metrics --property-id " + effective_property_id,
            )
            print_error(err)
            raise typer.Exit(err.exit_code)

        from ga4.filters import parse_filter_expression

        dim_filter = None
        if filter_expr:
            try:
                dim_filter = parse_filter_expression(filter_expr)
            except ValueError as exc:
                err = ValidationError(
                    message=f"Invalid --filter expression: {exc}",
                    hint=(
                        'Example: \'pagePath beginsWith "/" AND country = "Spain" '
                        'AND NOT deviceCategory = "tablet"\''
                    ),
                )
                print_error(err)
                raise typer.Exit(err.exit_code)

        met_filter = None
        if metric_filter_expr:
            try:
                met_filter = parse_filter_expression(metric_filter_expr)
            except ValueError as exc:
                err = ValidationError(
                    message=f"Invalid --metric-filter expression: {exc}",
                    hint="Example: 'sessions > 100'",
                )
                print_error(err)
                raise typer.Exit(err.exit_code)

        req = ReportRequest(
            property_id=effective_property_id,
            metrics=metrics_list,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions_list,
            dimension_filter=dim_filter,
            metric_filter=met_filter,
            order_bys=order_by_list,
            limit=limit,
            offset=offset,
        )

        from google.analytics.data_v1beta.types import (  # type: ignore[import-untyped]
            DateRange,
            Dimension,
            Metric,
            OrderBy,
            RunReportRequest,
        )

        from ga4.filters import filter_expression_to_proto

        api_request = RunReportRequest(
            property=f"properties/{req.property_id}",
            dimensions=[Dimension(name=d) for d in req.dimensions],
            metrics=[Metric(name=m) for m in req.metrics],
            date_ranges=[DateRange(start_date=req.start_date, end_date=req.end_date)],
            dimension_filter=(
                filter_expression_to_proto(req.dimension_filter)
                if req.dimension_filter
                else None
            ),
            metric_filter=(
                filter_expression_to_proto(req.metric_filter)
                if req.metric_filter
                else None
            ),
            order_bys=_parse_order_bys(req.order_bys),
            limit=req.limit,
            offset=req.offset,
        )

        client = build_data_client(config)
        response = client.run_report(request=api_request)

        report = ReportResponse.from_api_response(response)
        result = render_report(report)
        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except google_exceptions.PermissionDenied as exc:
        # Bug 3 fix: surface the real API error message instead of hiding it.
        err = AuthError(
            message=f"Permission denied running report: {exc.message if hasattr(exc, 'message') else exc}",
            hint="Ensure your credentials have the Analytics Read & Analyze permission.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.InvalidArgument as exc:
        err = ValidationError(message=f"Invalid report request: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(message=f"API call failed: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
