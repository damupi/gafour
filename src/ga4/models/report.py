from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


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
    dimension_filter: str | None = None
    metric_filter: str | None = None
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
