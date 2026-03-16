from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from gafour.cli import app
from gafour.models.report import BatchReportRequestItem, BatchReportResponse, ReportResponse


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


def test_batch_report_request_item_valid() -> None:
    """BatchReportRequestItem validates a minimal request object."""
    item = BatchReportRequestItem.model_validate(
        {
            "metrics": ["sessions"],
            "date_ranges": [{"start_date": "7daysAgo", "end_date": "today"}],
        }
    )
    assert item.metrics == ["sessions"]
    assert len(item.date_ranges) == 1
    assert item.dimensions == []
    assert item.limit == 10000
    assert item.offset == 0


def test_batch_report_request_item_missing_metrics() -> None:
    """BatchReportRequestItem raises when metrics is absent."""
    from pydantic import ValidationError as PydanticValidationError

    with pytest.raises(PydanticValidationError):
        BatchReportRequestItem.model_validate(
            {"date_ranges": [{"start_date": "7daysAgo", "end_date": "today"}]}
        )


def test_batch_report_request_item_missing_date_ranges() -> None:
    """BatchReportRequestItem raises when date_ranges is absent."""
    from pydantic import ValidationError as PydanticValidationError

    with pytest.raises(PydanticValidationError):
        BatchReportRequestItem.model_validate({"metrics": ["sessions"]})


# ---------------------------------------------------------------------------
# CLI helpers
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


def _write_requests_file(tmp_path: Path, requests: list) -> Path:  # type: ignore[type-arg]
    p = tmp_path / "requests.json"
    p.write_text(json.dumps(requests), encoding="utf-8")
    return p


_TWO_REQUESTS = [
    {
        "metrics": ["sessions"],
        "dimensions": ["date"],
        "date_ranges": [{"start_date": "7daysAgo", "end_date": "today"}],
    },
    {
        "metrics": ["activeUsers"],
        "dimensions": ["country"],
        "date_ranges": [{"start_date": "14daysAgo", "end_date": "8daysAgo"}],
    },
]

_ONE_REQUEST = [
    {
        "metrics": ["sessions"],
        "date_ranges": [{"start_date": "7daysAgo", "end_date": "today"}],
    }
]


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


def test_reports_batch_two_requests(runner: CliRunner, tmp_path: Path) -> None:
    """reports batch outputs valid JSON with two report entries from a file."""
    req_file = _write_requests_file(tmp_path, _TWO_REQUESTS)
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
                "--requests-file",
                str(req_file),
            ],
        )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "reports" in data
    assert len(data["reports"]) == 2


def test_reports_batch_single_request(runner: CliRunner, tmp_path: Path) -> None:
    """reports batch works with a single request in the file."""
    req_file = _write_requests_file(tmp_path, _ONE_REQUEST)
    single_report = MagicMock()
    single_report.dimension_headers = []
    single_report.metric_headers = []
    single_report.rows = []
    single_report.totals = []
    single_report.maximums = []
    single_report.minimums = []
    single_report.row_count = 0
    single_report.kind = "analyticsData#runReport"

    batch_resp = MagicMock()
    batch_resp.reports = [single_report]
    batch_resp.kind = "analyticsData#batchRunReports"

    mock_client = MagicMock()
    mock_client.batch_run_reports.return_value = batch_resp

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
                "--requests-file",
                str(req_file),
            ],
        )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert len(data["reports"]) == 1


def test_reports_batch_uses_default_property_id(runner: CliRunner, tmp_path: Path) -> None:
    """reports batch picks up property_id from config when not passed explicitly."""
    req_file = _write_requests_file(tmp_path, _ONE_REQUEST)
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
            ["reports", "batch", "--requests-file", str(req_file)],
        )

    assert result.exit_code == 0, result.output


def test_reports_batch_requires_property_id(runner: CliRunner, tmp_path: Path) -> None:
    """reports batch exits with an error when no property id is available."""
    req_file = _write_requests_file(tmp_path, _ONE_REQUEST)

    with (
        patch("gafour.commands.reports.build_data_client", return_value=MagicMock()),
        patch(
            "gafour.commands.reports.load_config",
            return_value=MagicMock(default_property_id=None),
        ),
    ):
        result = runner.invoke(
            app,
            ["reports", "batch", "--requests-file", str(req_file)],
        )

    assert result.exit_code != 0


def test_reports_batch_requires_requests_file(runner: CliRunner) -> None:
    """reports batch exits with an error when --requests-file is not given."""
    with (
        patch("gafour.commands.reports.build_data_client", return_value=MagicMock()),
        patch(
            "gafour.commands.reports.load_config",
            return_value=MagicMock(default_property_id="12345"),
        ),
    ):
        result = runner.invoke(
            app,
            ["reports", "batch", "--property-id", "12345"],
        )

    assert result.exit_code != 0


def test_reports_batch_invalid_json(runner: CliRunner, tmp_path: Path) -> None:
    """reports batch exits with an error when the file contains invalid JSON."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not json at all", encoding="utf-8")

    with (
        patch("gafour.commands.reports.build_data_client", return_value=MagicMock()),
        patch(
            "gafour.commands.reports.load_config",
            return_value=MagicMock(default_property_id="12345"),
        ),
    ):
        result = runner.invoke(
            app,
            ["reports", "batch", "--property-id", "12345", "--requests-file", str(bad_file)],
        )

    assert result.exit_code != 0


def test_reports_batch_missing_required_fields(runner: CliRunner, tmp_path: Path) -> None:
    """reports batch exits when a request item is missing required fields."""
    bad_requests = [{"dimensions": ["date"]}]  # missing metrics and date_ranges
    req_file = _write_requests_file(tmp_path, bad_requests)

    with (
        patch("gafour.commands.reports.build_data_client", return_value=MagicMock()),
        patch(
            "gafour.commands.reports.load_config",
            return_value=MagicMock(default_property_id="12345"),
        ),
    ):
        result = runner.invoke(
            app,
            ["reports", "batch", "--property-id", "12345", "--requests-file", str(req_file)],
        )

    assert result.exit_code != 0


def test_reports_batch_exceeds_five_requests(runner: CliRunner, tmp_path: Path) -> None:
    """reports batch exits when more than 5 requests are in the file."""
    too_many = [
        {
            "metrics": ["sessions"],
            "date_ranges": [{"start_date": "7daysAgo", "end_date": "today"}],
        }
    ] * 6
    req_file = _write_requests_file(tmp_path, too_many)

    with (
        patch("gafour.commands.reports.build_data_client", return_value=MagicMock()),
        patch(
            "gafour.commands.reports.load_config",
            return_value=MagicMock(default_property_id="12345"),
        ),
    ):
        result = runner.invoke(
            app,
            ["reports", "batch", "--property-id", "12345", "--requests-file", str(req_file)],
        )

    assert result.exit_code != 0


def test_reports_batch_sends_correct_request_count_to_api(
    runner: CliRunner, tmp_path: Path
) -> None:
    """reports batch sends exactly N RunReportRequests matching the file contents."""
    req_file = _write_requests_file(tmp_path, _TWO_REQUESTS)
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
                "--property-id",
                "12345",
                "--requests-file",
                str(req_file),
            ],
        )

    mock_client.batch_run_reports.assert_called_once()
    call_kwargs = mock_client.batch_run_reports.call_args
    request_arg = call_kwargs.kwargs.get("request") or call_kwargs.args[0]
    assert len(request_arg.requests) == 2


def test_reports_batch_output_to_file(runner: CliRunner, tmp_path: Path) -> None:
    """reports batch --output writes JSON to a file."""
    req_file = _write_requests_file(tmp_path, _TWO_REQUESTS)
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
                "--requests-file",
                str(req_file),
                "--output",
                str(out_file),
            ],
        )

    assert result.exit_code == 0, result.output
    data = json.loads(out_file.read_text())
    assert "reports" in data
