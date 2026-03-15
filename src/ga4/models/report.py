from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DateRange(BaseModel):
    """A date range for use in report requests.

    Attributes:
        start_date: Inclusive start date in ``YYYY-MM-DD`` or relative format.
        end_date: Inclusive end date in ``YYYY-MM-DD`` or relative format.
    """

    model_config = ConfigDict(populate_by_name=True)

    start_date: str
    end_date: str


class DimensionValue(BaseModel):
    """A single dimension cell value in a report row.

    Attributes:
        value: String representation of the dimension value.
    """

    model_config = ConfigDict(populate_by_name=True)

    value: str


class MetricValue(BaseModel):
    """A single metric cell value in a report row.

    Attributes:
        value: String representation of the metric value.
    """

    model_config = ConfigDict(populate_by_name=True)

    value: str


class ReportRow(BaseModel):
    """A single data row in a report response.

    Attributes:
        dimension_values: Ordered dimension cell values.
        metric_values: Ordered metric cell values.
    """

    model_config = ConfigDict(populate_by_name=True)

    dimension_values: list[DimensionValue] = []
    metric_values: list[MetricValue] = []


class ReportRequest(BaseModel):
    """Input parameters for a GA4 Data API report request.

    Attributes:
        property_id: The GA4 property ID (numeric string).
        metrics: List of metric API names (e.g. ``["sessions", "users"]``).
        start_date: Inclusive start date.
        end_date: Inclusive end date.
        dimensions: Optional list of dimension API names.
        dimension_filter: Optional dimension filter expression string.
        metric_filter: Optional metric filter expression string.
        order_bys: Optional list of order-by expressions.
        limit: Maximum number of rows to return (1–250000).
        offset: Zero-based row offset for pagination.
    """

    model_config = ConfigDict(populate_by_name=True)

    property_id: str
    metrics: list[str]
    start_date: str
    end_date: str
    dimensions: list[str] = []
    dimension_filter: str | None = None
    metric_filter: str | None = None
    order_bys: list[str] = []
    limit: int = Field(default=10000, ge=1, le=250000)
    offset: int = Field(default=0, ge=0)


class ReportResponse(BaseModel):
    """Parsed response from a GA4 Data API report.

    Attributes:
        property_id: The GA4 property ID this report was run against.
        dimensions: Ordered list of dimension API names used in the report.
        metrics: Ordered list of metric API names used in the report.
        rows: Data rows.
        row_count: Total number of matching rows (may exceed ``len(rows)``).
    """

    model_config = ConfigDict(populate_by_name=True)

    property_id: str
    dimensions: list[str]
    metrics: list[str]
    rows: list[ReportRow] = []
    row_count: int = 0
