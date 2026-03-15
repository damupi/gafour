from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Filter expression models — mirror GA4 FilterExpression / Filter protos.
# These are proto-free Pydantic models; filters.py owns conversion to protos.
# ---------------------------------------------------------------------------


class StringFilter(BaseModel):
    """Mirrors Filter.StringFilter."""

    model_config = ConfigDict(populate_by_name=True)

    match_type: str  # EXACT | BEGINS_WITH | ENDS_WITH | CONTAINS | FULL_REGEXP
    value: str
    case_sensitive: bool = False


class NumericValue(BaseModel):
    """Mirrors google.analytics.data_v1beta.types.NumericValue."""

    model_config = ConfigDict(populate_by_name=True)

    double_value: float


class NumericFilter(BaseModel):
    """Mirrors Filter.NumericFilter."""

    model_config = ConfigDict(populate_by_name=True)

    operation: str  # EQUAL | LESS_THAN | LESS_THAN_OR_EQUAL | GREATER_THAN | GREATER_THAN_OR_EQUAL
    value: NumericValue


class FilterField(BaseModel):
    """Mirrors a GA4 Filter (leaf node) — a single field comparison."""

    model_config = ConfigDict(populate_by_name=True)

    field_name: str
    string_filter: StringFilter | None = None
    numeric_filter: NumericFilter | None = None


class FilterExpression(BaseModel):
    """Mirrors GA4 FilterExpression — a tree node that can be AND / OR / NOT / leaf."""

    model_config = ConfigDict(populate_by_name=True)

    and_group: list[FilterExpression] | None = None
    or_group: list[FilterExpression] | None = None
    not_expression: FilterExpression | None = None
    filter: FilterField | None = None


# Required for self-referential model
FilterExpression.model_rebuild()


class DateRange(BaseModel):
    """A date range for use in report requests."""

    model_config = ConfigDict(populate_by_name=True)

    start_date: str
    end_date: str


class DimensionHeader(BaseModel):
    """Maps a position index to a dimension name in a report response."""

    model_config = ConfigDict(populate_by_name=True)

    name: str


class MetricHeader(BaseModel):
    """Maps a position index to a metric name and type in a report response."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    type: str = ""


class DimensionValue(BaseModel):
    """A single dimension cell value in a report row."""

    model_config = ConfigDict(populate_by_name=True)

    value: str


class MetricValue(BaseModel):
    """A single metric cell value in a report row."""

    model_config = ConfigDict(populate_by_name=True)

    value: str


class ReportRow(BaseModel):
    """A single data row in a report response."""

    model_config = ConfigDict(populate_by_name=True)

    dimension_values: list[DimensionValue] = []
    metric_values: list[MetricValue] = []


class ReportRequest(BaseModel):
    """Input parameters for a GA4 Data API report request."""

    model_config = ConfigDict(populate_by_name=True)

    property_id: str
    metrics: list[str]
    start_date: str
    end_date: str
    dimensions: list[str] = []
    dimension_filter: FilterExpression | None = None
    metric_filter: FilterExpression | None = None
    order_bys: list[str] = []
    limit: int = Field(default=10000, ge=1, le=250000)
    offset: int = Field(default=0, ge=0)


class ReportResponse(BaseModel):
    """Parsed response from a GA4 Data API report, mirroring RunReportResponse.

    See: https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/RunReportResponse
    """

    model_config = ConfigDict(populate_by_name=True)

    dimension_headers: list[DimensionHeader] = []
    metric_headers: list[MetricHeader] = []
    rows: list[ReportRow] = []
    totals: list[ReportRow] = []
    maximums: list[ReportRow] = []
    minimums: list[ReportRow] = []
    row_count: int = 0
    kind: str = ""

    @classmethod
    def from_api_response(cls, response: object) -> ReportResponse:
        """Build a ReportResponse from a raw proto-plus API response object."""

        def _parse_row(row: object) -> ReportRow:
            return ReportRow(
                dimension_values=[
                    DimensionValue(value=v.value)
                    for v in getattr(row, "dimension_values", [])
                ],
                metric_values=[
                    MetricValue(value=v.value)
                    for v in getattr(row, "metric_values", [])
                ],
            )

        return cls(
            dimension_headers=[
                DimensionHeader(name=h.name)
                for h in getattr(response, "dimension_headers", [])
            ],
            metric_headers=[
                MetricHeader(
                    name=h.name,
                    type=str(
                        getattr(h, "type_", None) or getattr(h, "type", None) or ""
                    ),
                )
                for h in getattr(response, "metric_headers", [])
            ],
            rows=[_parse_row(r) for r in getattr(response, "rows", [])],
            totals=[_parse_row(r) for r in getattr(response, "totals", [])],
            maximums=[_parse_row(r) for r in getattr(response, "maximums", [])],
            minimums=[_parse_row(r) for r in getattr(response, "minimums", [])],
            row_count=getattr(response, "row_count", 0),
            kind=str(getattr(response, "kind", "") or ""),
        )
