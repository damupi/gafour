from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from gafour.cli import app


def _make_custom_metric(
    name: str,
    parameter_name: str,
    display_name: str,
    scope: str = "EVENT",
    measurement_unit: str = "STANDARD",
    description: str = "A test metric",
) -> MagicMock:
    cm = MagicMock()
    cm.name = name
    cm.parameter_name = parameter_name
    cm.display_name = display_name
    cm.scope = scope
    cm.measurement_unit = measurement_unit
    cm.description = description
    cm.restricted_metric_type = []
    return cm


class TestCustomMetricsList:
    def test_custom_metrics_list(self, typer_runner: CliRunner) -> None:
        """Mock list_custom_metrics; assert output contains metric data."""
        mock_client = MagicMock()
        mock_client.list_custom_metrics.return_value = [
            _make_custom_metric(
                "properties/123/customMetrics/1",
                "engagement_score",
                "Engagement Score",
                measurement_unit="STANDARD",
            ),
            _make_custom_metric(
                "properties/123/customMetrics/2",
                "revenue_custom",
                "Custom Revenue",
                measurement_unit="CURRENCY",
            ),
        ]

        with (
            patch("gafour.commands.custom_metrics.load_config") as mock_cfg,
            patch(
                "gafour.commands.custom_metrics.build_admin_client",
                return_value=mock_client,
            ),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(app, ["custom-metrics", "list", "123"])

        assert result.exit_code == 0
        assert "engagement_score" in result.output
        assert "Engagement Score" in result.output
        assert "revenue_custom" in result.output
        assert "CURRENCY" in result.output

    def test_custom_metrics_list_unit_displayed(self, typer_runner: CliRunner) -> None:
        """Assert measurement unit column is displayed."""
        mock_client = MagicMock()
        mock_client.list_custom_metrics.return_value = [
            _make_custom_metric(
                "properties/123/customMetrics/1",
                "session_duration",
                "Session Duration",
                measurement_unit="SECONDS",
            ),
        ]

        with (
            patch("gafour.commands.custom_metrics.load_config") as mock_cfg,
            patch(
                "gafour.commands.custom_metrics.build_admin_client",
                return_value=mock_client,
            ),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(app, ["custom-metrics", "list", "123"])

        assert result.exit_code == 0
        assert "SECONDS" in result.output

    def test_custom_metrics_list_empty(self, typer_runner: CliRunner) -> None:
        """Empty list renders no-results placeholder."""
        mock_client = MagicMock()
        mock_client.list_custom_metrics.return_value = []

        with (
            patch("gafour.commands.custom_metrics.load_config") as mock_cfg,
            patch(
                "gafour.commands.custom_metrics.build_admin_client",
                return_value=mock_client,
            ),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="json",
            )
            result = typer_runner.invoke(app, ["custom-metrics", "list", "123"])

        assert result.exit_code == 0
        assert result.output.strip() == "[]"

    def test_custom_metrics_list_auth_error(self, typer_runner: CliRunner) -> None:
        """Mock raises PermissionDenied; assert exit code is 2."""
        from google.api_core.exceptions import PermissionDenied

        mock_client = MagicMock()
        mock_client.list_custom_metrics.side_effect = PermissionDenied("denied")

        with (
            patch("gafour.commands.custom_metrics.load_config") as mock_cfg,
            patch(
                "gafour.commands.custom_metrics.build_admin_client",
                return_value=mock_client,
            ),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(app, ["custom-metrics", "list", "123"])

        assert result.exit_code == 2
