from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from google.api_core import exceptions as google_exceptions  # type: ignore[import-untyped]

from gafour.auth import build_data_client
from gafour.config import load_config
from gafour.errors import AuthError, GA4CLIError, NetworkError, ValidationError
from gafour.models.report import BatchReportRequestItem, BatchReportResponse, ReportRequest, ReportResponse
from gafour.output import print_error, render_batch_report, render_report

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

        from gafour.filters import parse_filter_expression

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

        from gafour.filters import filter_expression_to_proto

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


@reports_app.command("batch")
def reports_batch(
    property_id: Annotated[
        Optional[str],
        typer.Option("--property-id", "-p", help="The numeric GA4 property ID."),
    ] = None,
    requests_file: Annotated[
        Optional[Path],
        typer.Option(
            "--requests-file",
            "-f",
            help="Path to a JSON file containing an array of report request objects (1–5).",
        ),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write output to file."),
    ] = None,
) -> None:
    """Run multiple independent GA4 reports in a single batchRunReports API call.

    Each request in the JSON file is an independent RunReportRequest with its own
    metrics, dimensions, date ranges, filters, and order-bys.  The GA4 API allows
    1-5 requests per batch.  Output is JSON with a 'reports' array.

    Example requests file:

    \\b
    [
      {
        "metrics": ["sessions"],
        "dimensions": ["date"],
        "date_ranges": [{"start_date": "7daysAgo", "end_date": "today"}]
      },
      {
        "metrics": ["activeUsers"],
        "dimensions": ["country"],
        "date_ranges": [{"start_date": "30daysAgo", "end_date": "today"}]
      }
    ]
    """
    import json as _json

    from pydantic import ValidationError as PydanticValidationError

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

        if not requests_file:
            err = ValidationError(
                message="--requests-file is required.",
                hint="Pass a JSON file containing an array of report request objects.",
            )
            print_error(err)
            raise typer.Exit(err.exit_code)

        # Parse and validate the JSON file.
        try:
            raw_text = requests_file.read_text(encoding="utf-8")
        except OSError as exc:
            err = ValidationError(message=f"Cannot read requests file: {exc}")
            print_error(err)
            raise typer.Exit(err.exit_code)

        try:
            raw_list = _json.loads(raw_text)
        except _json.JSONDecodeError as exc:
            err = ValidationError(message=f"Invalid JSON in requests file: {exc}")
            print_error(err)
            raise typer.Exit(err.exit_code)

        if not isinstance(raw_list, list) or len(raw_list) == 0:
            err = ValidationError(
                message="Requests file must contain a non-empty JSON array.",
                hint="Each element should be a report request object with 'metrics' and 'date_ranges'.",
            )
            print_error(err)
            raise typer.Exit(err.exit_code)

        if len(raw_list) > 5:
            err = ValidationError(
                message=f"Too many requests: {len(raw_list)} (GA4 API limit is 5 per batch).",
                hint="Split your requests into multiple batches of up to 5.",
            )
            print_error(err)
            raise typer.Exit(err.exit_code)

        try:
            items = [BatchReportRequestItem.model_validate(r) for r in raw_list]
        except PydanticValidationError as exc:
            err = ValidationError(message=f"Invalid request item in file: {exc}")
            print_error(err)
            raise typer.Exit(err.exit_code)

        from google.analytics.data_v1beta.types import (  # type: ignore[import-untyped]
            BatchRunReportsRequest,
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )

        from gafour.filters import filter_expression_to_proto

        def _build_run_request(item: BatchReportRequestItem) -> RunReportRequest:
            return RunReportRequest(
                property=f"properties/{effective_property_id}",
                dimensions=[Dimension(name=d) for d in item.dimensions],
                metrics=[Metric(name=m) for m in item.metrics],
                date_ranges=[
                    DateRange(start_date=dr.start_date, end_date=dr.end_date)
                    for dr in item.date_ranges
                ],
                dimension_filter=(
                    filter_expression_to_proto(item.dimension_filter)
                    if item.dimension_filter
                    else None
                ),
                metric_filter=(
                    filter_expression_to_proto(item.metric_filter)
                    if item.metric_filter
                    else None
                ),
                order_bys=_parse_order_bys(_split_csv(item.order_bys)),
                limit=item.limit,
                offset=item.offset,
            )

        run_requests = [_build_run_request(item) for item in items]

        batch_request = BatchRunReportsRequest(
            property=f"properties/{effective_property_id}",
            requests=run_requests,
        )

        client = build_data_client(config)
        response = client.batch_run_reports(request=batch_request)

        batch = BatchReportResponse.from_api_response(response)
        result = render_batch_report(batch)
        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except google_exceptions.PermissionDenied as exc:
        err = AuthError(
            message=f"Permission denied running batch report: {exc.message if hasattr(exc, 'message') else exc}",
            hint="Ensure your credentials have the Analytics Read & Analyze permission.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.InvalidArgument as exc:
        err = ValidationError(message=f"Invalid batch report request: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(message=f"API call failed: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
