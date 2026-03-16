from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from gafour.cli import app
from gafour.models.report import BatchReportResponse, ReportResponse


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


def _make_mock_report_response() -> MagicMock:
    """Build a minimal mock proto RunReportResponse."""
    resp = MagicMock()
    resp.dimension_headers = []
    resp.metric_headers = []
    resp.rows = []
    resp.totals = []
    resp.maximums = []
    resp.minimums = []
    resp.row_count = 0
    resp.kind = "analyticsData#runReport"
    return resp


def test_batch_report_response_from_api_response_two_reports() -> None:
    """BatchReportResponse.from_api_response parses two RunReportResponse entries."""
    api_resp = MagicMock()
    api_resp.reports = [_make_mock_report_response(), _make_mock_report_response()]
    api_resp.kind = "analyticsData#batchRunReports"

    result = BatchReportResponse.from_api_response(api_resp)

    assert result.kind == "analyticsData#batchRunReports"
    assert len(result.reports) == 2
    assert all(isinstance(r, ReportResponse) for r in result.reports)


def test_batch_report_response_empty_reports() -> None:
    """BatchReportResponse handles an empty reports list gracefully."""
    api_resp = MagicMock()
    api_resp.reports = []
    api_resp.kind = "analyticsData#batchRunReports"

    result = BatchReportResponse.from_api_response(api_resp)

    assert result.reports == []


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


def _make_batch_api_response() -> MagicMock:
    dim_header = MagicMock()
    dim_header.name = "date"

    met_header = MagicMock()
    met_header.name = "sessions"
    met_header.type_ = "TYPE_INTEGER"

    row = MagicMock()
    dv = MagicMock()
    dv.value = "20240101"
    mv = MagicMock()
    mv.value = "42"
    row.dimension_values = [dv]
    row.metric_values = [mv]

    single_report = MagicMock()
    single_report.dimension_headers = [dim_header]
    single_report.metric_headers = [met_header]
    single_report.rows = [row]
    single_report.totals = []
    single_report.maximums = []
    single_report.minimums = []
    single_report.row_count = 1
    single_report.kind = "analyticsData#runReport"

    batch_resp = MagicMock()
    batch_resp.reports = [single_report, single_report]
    batch_resp.kind = "analyticsData#batchRunReports"
    return batch_resp


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_reports_batch_run_basic(runner: CliRunner) -> None:
    """reports batch outputs valid JSON with two report entries."""
    mock_client = MagicMock()
    mock_client.batch_run_reports.return_value = _make_batch_api_response()

    with (
        patch("gafour.commands.reports.build_data_client", return_value=mock_client),
        patch(
            "gafour.commands.reports.load_config",
            return_value=MagicMock(default_property_id="12345"),
        ),
    ):
        result = runner.invoke(
            app,
            [
                "reports",
                "batch",
                "--property-id",
                "12345",
                "--metrics",
                "sessions",
                "--start-date",
                "7daysAgo",
                "--end-date",
                "today",
                "--compare-start-date",
                "14daysAgo",
                "--compare-end-date",
                "8daysAgo",
            ],
        )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "reports" in data
    assert len(data["reports"]) == 2


def test_reports_batch_uses_default_property_id(runner: CliRunner) -> None:
    """reports batch picks up property_id from config when not passed explicitly."""
    mock_client = MagicMock()
    mock_client.batch_run_reports.return_value = _make_batch_api_response()

    with (
        patch("gafour.commands.reports.build_data_client", return_value=mock_client),
        patch(
            "gafour.commands.reports.load_config",
            return_value=MagicMock(default_property_id="99999"),
        ),
    ):
        result = runner.invoke(
            app,
            [
                "reports",
                "batch",
                "--metrics",
                "sessions",
                "--compare-start-date",
                "14daysAgo",
                "--compare-end-date",
                "8daysAgo",
            ],
        )

    assert result.exit_code == 0, result.output


def test_reports_batch_requires_metrics(runner: CliRunner) -> None:
    """reports batch exits with an error when no --metrics are given."""
    mock_client = MagicMock()

    with (
        patch("gafour.commands.reports.build_data_client", return_value=mock_client),
        patch(
            "gafour.commands.reports.load_config",
            return_value=MagicMock(default_property_id="12345"),
        ),
    ):
        result = runner.invoke(
            app,
            [
                "reports",
                "batch",
                "--property-id",
                "12345",
                "--compare-start-date",
                "14daysAgo",
                "--compare-end-date",
                "8daysAgo",
            ],
        )

    assert result.exit_code != 0


def test_reports_batch_requires_property_id(runner: CliRunner) -> None:
    """reports batch exits with an error when no property id is available."""
    mock_client = MagicMock()

    with (
        patch("gafour.commands.reports.build_data_client", return_value=mock_client),
        patch(
            "gafour.commands.reports.load_config",
            return_value=MagicMock(default_property_id=None),
        ),
    ):
        result = runner.invoke(
            app,
            [
                "reports",
                "batch",
                "--metrics",
                "sessions",
                "--compare-start-date",
                "14daysAgo",
                "--compare-end-date",
                "8daysAgo",
            ],
        )

    assert result.exit_code != 0


def test_reports_batch_sends_two_requests_to_api(runner: CliRunner) -> None:
    """reports batch sends exactly two RunReportRequests in the API call."""
    mock_client = MagicMock()
    mock_client.batch_run_reports.return_value = _make_batch_api_response()

    with (
        patch("gafour.commands.reports.build_data_client", return_value=mock_client),
        patch(
            "gafour.commands.reports.load_config",
            return_value=MagicMock(default_property_id="12345"),
        ),
    ):
        runner.invoke(
            app,
            [
                "reports",
                "batch",
                "--metrics",
                "sessions",
                "--property-id",
                "12345",
                "--start-date",
                "7daysAgo",
                "--end-date",
                "today",
                "--compare-start-date",
                "14daysAgo",
                "--compare-end-date",
                "8daysAgo",
            ],
        )

    mock_client.batch_run_reports.assert_called_once()
    call_kwargs = mock_client.batch_run_reports.call_args
    request_arg = call_kwargs.kwargs.get("request") or call_kwargs.args[0]
    assert len(request_arg.requests) == 2


def test_reports_batch_output_to_file(runner: CliRunner, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """reports batch --output writes JSON to a file."""
    mock_client = MagicMock()
    mock_client.batch_run_reports.return_value = _make_batch_api_response()
    out_file = tmp_path / "batch.json"

    with (
        patch("gafour.commands.reports.build_data_client", return_value=mock_client),
        patch(
            "gafour.commands.reports.load_config",
            return_value=MagicMock(default_property_id="12345"),
        ),
    ):
        result = runner.invoke(
            app,
            [
                "reports",
                "batch",
                "--property-id",
                "12345",
                "--metrics",
                "sessions",
                "--compare-start-date",
                "14daysAgo",
                "--compare-end-date",
                "8daysAgo",
                "--output",
                str(out_file),
            ],
        )

    assert result.exit_code == 0, result.output
    data = json.loads(out_file.read_text())
    assert "reports" in data
