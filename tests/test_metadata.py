from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from ga4.cli import app


def _make_dimension_meta(
    api_name: str,
    ui_name: str,
    description: str = "",
    category: str = "General",
) -> MagicMock:
    d = MagicMock()
    d.api_name = api_name
    d.ui_name = ui_name
    d.description = description
    d.deprecated_api_names = []
    d.custom_definition = False
    d.category = category
    return d


def _make_metric_meta(
    api_name: str,
    ui_name: str,
    description: str = "",
    category: str = "General",
) -> MagicMock:
    m = MagicMock()
    m.api_name = api_name
    m.ui_name = ui_name
    m.description = description
    m.deprecated_api_names = []
    m.custom_definition = False
    m.category = category
    m.type_ = "TYPE_INTEGER"
    m.expression = None
    return m


def _make_metadata_response(
    dimensions: list[MagicMock] | None = None,
    metrics: list[MagicMock] | None = None,
) -> MagicMock:
    resp = MagicMock()
    resp.dimensions = dimensions or []
    resp.metrics = metrics or []
    return resp


class TestMetadataDimensions:
    def test_metadata_dimensions(self, typer_runner: CliRunner) -> None:
        """Mock get_metadata; assert dimensions are rendered in output."""
        mock_client = MagicMock()
        mock_client.get_metadata.return_value = _make_metadata_response(
            dimensions=[
                _make_dimension_meta("city", "City"),
                _make_dimension_meta("country", "Country"),
            ]
        )

        with (
            patch("ga4.commands.metadata.load_config") as mock_cfg,
            patch("ga4.commands.metadata.build_data_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(
                app, ["metadata", "dimensions", "--property-id", "123"]
            )

        assert result.exit_code == 0
        assert "city" in result.output
        assert "country" in result.output
        assert "City" in result.output

    def test_metadata_dimensions_search(self, typer_runner: CliRunner) -> None:
        """Assert search term filters dimension results."""
        mock_client = MagicMock()
        mock_client.get_metadata.return_value = _make_metadata_response(
            dimensions=[
                _make_dimension_meta("city", "City"),
                _make_dimension_meta("country", "Country"),
                _make_dimension_meta("deviceCategory", "Device Category"),
            ]
        )

        with (
            patch("ga4.commands.metadata.load_config") as mock_cfg,
            patch("ga4.commands.metadata.build_data_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(
                app,
                ["metadata", "dimensions", "--property-id", "123", "--search", "cit"],
            )

        assert result.exit_code == 0
        assert "city" in result.output
        # country and deviceCategory should be filtered out
        assert "country" not in result.output
        assert "deviceCategory" not in result.output

    def test_metadata_dimensions_missing_property_id(
        self, typer_runner: CliRunner
    ) -> None:
        """Assert non-zero exit when --property-id is missing."""
        result = typer_runner.invoke(app, ["metadata", "dimensions"])
        assert result.exit_code != 0


class TestMetadataMetrics:
    def test_metadata_metrics(self, typer_runner: CliRunner) -> None:
        """Mock get_metadata; assert metrics are rendered."""
        mock_client = MagicMock()
        mock_client.get_metadata.return_value = _make_metadata_response(
            metrics=[
                _make_metric_meta("sessions", "Sessions"),
                _make_metric_meta("users", "Users"),
            ]
        )

        with (
            patch("ga4.commands.metadata.load_config") as mock_cfg,
            patch("ga4.commands.metadata.build_data_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(
                app, ["metadata", "metrics", "--property-id", "123"]
            )

        assert result.exit_code == 0
        assert "sessions" in result.output
        assert "users" in result.output

    def test_metadata_metrics_search(self, typer_runner: CliRunner) -> None:
        """Assert search term filters metric results."""
        mock_client = MagicMock()
        mock_client.get_metadata.return_value = _make_metadata_response(
            metrics=[
                _make_metric_meta("sessions", "Sessions"),
                _make_metric_meta("bounceRate", "Bounce Rate"),
            ]
        )

        with (
            patch("ga4.commands.metadata.load_config") as mock_cfg,
            patch("ga4.commands.metadata.build_data_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(
                app,
                ["metadata", "metrics", "--property-id", "123", "--search", "bounce"],
            )

        assert result.exit_code == 0
        assert "bounceRate" in result.output
        assert "sessions" not in result.output


class TestMetadataCompatibility:
    def _make_dim_compat(self, api_name: str, compatible: bool) -> MagicMock:
        dc = MagicMock()
        dc.compatibility = "COMPATIBLE" if compatible else "INCOMPATIBLE"
        dc.dimension_metadata = _make_dimension_meta(api_name, api_name.title())
        return dc

    def _make_met_compat(self, api_name: str, compatible: bool) -> MagicMock:
        mc = MagicMock()
        mc.compatibility = "COMPATIBLE" if compatible else "INCOMPATIBLE"
        mc.metric_metadata = _make_metric_meta(api_name, api_name.title())
        return mc

    def test_metadata_compatibility(self, typer_runner: CliRunner) -> None:
        """Mock check_compatibility; assert COMPATIBLE/INCOMPATIBLE labels shown."""
        mock_client = MagicMock()
        compat_resp = MagicMock()
        compat_resp.dimension_compatibilities = [
            self._make_dim_compat("city", True),
        ]
        compat_resp.metric_compatibilities = [
            self._make_met_compat("sessions", True),
            self._make_met_compat("bounceRate", False),
        ]
        mock_client.check_compatibility.return_value = compat_resp

        with (
            patch("ga4.commands.metadata.load_config") as mock_cfg,
            patch("ga4.commands.metadata.build_data_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(
                app,
                [
                    "metadata",
                    "compatibility",
                    "--property-id",
                    "123",
                    "--dimensions",
                    "city",
                    "--metrics",
                    "sessions",
                ],
            )

        assert result.exit_code == 0
        assert "COMPATIBLE" in result.output

    def test_metadata_compatibility_filter_compatible(
        self, typer_runner: CliRunner
    ) -> None:
        """Assert --filter compatible shows only COMPATIBLE entries."""
        mock_client = MagicMock()
        compat_resp = MagicMock()
        compat_resp.dimension_compatibilities = []
        compat_resp.metric_compatibilities = [
            self._make_met_compat("sessions", True),
            self._make_met_compat("bounceRate", False),
        ]
        mock_client.check_compatibility.return_value = compat_resp

        with (
            patch("ga4.commands.metadata.load_config") as mock_cfg,
            patch("ga4.commands.metadata.build_data_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(
                app,
                [
                    "metadata",
                    "compatibility",
                    "--property-id",
                    "123",
                    "--filter",
                    "compatible",
                ],
            )

        assert result.exit_code == 0
        assert "sessions" in result.output
        assert "bounceRate" not in result.output
