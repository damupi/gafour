from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from gafour.cli import app


def _make_property(
    name: str,
    display_name: str,
    time_zone: str = "UTC",
    currency_code: str = "USD",
    parent: str = "accounts/123",
) -> MagicMock:
    """Helper to create a mock property proto object."""
    prop = MagicMock()
    prop.name = name
    prop.display_name = display_name
    prop.time_zone = time_zone
    prop.currency_code = currency_code
    prop.industry_category = None
    prop.create_time = None
    prop.update_time = None
    prop.parent = parent
    return prop


class TestPropertiesList:
    def test_properties_list(self, typer_runner: CliRunner) -> None:
        """Mock returns properties for an account; assert they appear in output."""
        mock_client = MagicMock()
        mock_client.list_properties.return_value = [
            _make_property("properties/456", "My Web Property"),
            _make_property("properties/789", "My App Property"),
        ]

        with (
            patch("gafour.commands.properties.load_config") as mock_cfg,
            patch("gafour.commands.properties.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(
                app, ["properties", "list", "--account-id", "123"]
            )

        assert result.exit_code == 0
        assert "456" in result.output
        assert "789" in result.output
        assert "My Web Property" in result.output

    def test_properties_list_passes_filter(self, typer_runner: CliRunner) -> None:
        """Verify the API is called with the correct parent filter."""
        mock_client = MagicMock()
        mock_client.list_properties.return_value = []

        with (
            patch("gafour.commands.properties.load_config") as mock_cfg,
            patch("gafour.commands.properties.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(
                app, ["properties", "list", "--account-id", "555"]
            )

        from google.analytics.admin_v1beta.types import ListPropertiesRequest  # type: ignore[import-untyped]
        mock_client.list_properties.assert_called_once_with(
            request=ListPropertiesRequest(filter="parent:accounts/555")
        )

    def test_properties_list_missing_account_id(self, typer_runner: CliRunner) -> None:
        """Assert error and non-zero exit when --account-id is not provided."""
        result = typer_runner.invoke(app, ["properties", "list"])
        assert result.exit_code != 0

    def test_properties_list_json_format(self, typer_runner: CliRunner) -> None:
        """Assert JSON output is valid and contains property data."""
        mock_client = MagicMock()
        mock_client.list_properties.return_value = [
            _make_property("properties/101", "JSON Property"),
        ]

        with (
            patch("gafour.commands.properties.load_config") as mock_cfg,
            patch("gafour.commands.properties.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(
                app, ["properties", "list", "--account-id", "123", "--format", "json"]
            )

        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert parsed[0]["name"] == "properties/101"
        assert parsed[0]["display_name"] == "JSON Property"


class TestPropertiesGet:
    def test_properties_get(self, typer_runner: CliRunner) -> None:
        """Mock returns a single property; assert output contains its details."""
        mock_client = MagicMock()
        mock_client.get_property.return_value = _make_property(
            "properties/456",
            "Test Property",
            time_zone="Europe/London",
            currency_code="GBP",
        )

        with (
            patch("gafour.commands.properties.load_config") as mock_cfg,
            patch("gafour.commands.properties.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(app, ["properties", "get", "456"])

        assert result.exit_code == 0
        assert "456" in result.output
        assert "Test Property" in result.output

    def test_properties_get_not_found(self, typer_runner: CliRunner) -> None:
        """Mock raises NotFound; assert exit code is 1."""
        from google.api_core.exceptions import NotFound

        mock_client = MagicMock()
        mock_client.get_property.side_effect = NotFound("not found")

        with (
            patch("gafour.commands.properties.load_config") as mock_cfg,
            patch("gafour.commands.properties.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(app, ["properties", "get", "000"])

        assert result.exit_code == 1

    def test_properties_get_auth_error(self, typer_runner: CliRunner) -> None:
        """Mock raises PermissionDenied; assert exit code is 2."""
        from google.api_core.exceptions import PermissionDenied

        mock_client = MagicMock()
        mock_client.get_property.side_effect = PermissionDenied("denied")

        with (
            patch("gafour.commands.properties.load_config") as mock_cfg,
            patch("gafour.commands.properties.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(app, ["properties", "get", "456"])

        assert result.exit_code == 2
