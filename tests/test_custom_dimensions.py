from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from ga4x.cli import app


def _make_custom_dimension(
    name: str,
    parameter_name: str,
    display_name: str,
    scope: str = "EVENT",
    description: str = "A test dimension",
) -> MagicMock:
    cd = MagicMock()
    cd.name = name
    cd.parameter_name = parameter_name
    cd.display_name = display_name
    cd.scope = scope
    cd.description = description
    cd.disallow_ads_personalization = False
    return cd


class TestCustomDimensionsList:
    def test_custom_dimensions_list(self, typer_runner: CliRunner) -> None:
        """Mock list_custom_dimensions; assert output contains dimension data."""
        mock_client = MagicMock()
        mock_client.list_custom_dimensions.return_value = [
            _make_custom_dimension(
                "properties/123/customDimensions/1",
                "user_type",
                "User Type",
                scope="USER",
            ),
            _make_custom_dimension(
                "properties/123/customDimensions/2",
                "item_brand",
                "Item Brand",
                scope="ITEM",
            ),
        ]

        with (
            patch("ga4x.commands.custom_dimensions.load_config") as mock_cfg,
            patch(
                "ga4x.commands.custom_dimensions.build_admin_client",
                return_value=mock_client,
            ),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(app, ["custom-dimensions", "list", "123"])

        assert result.exit_code == 0
        assert "user_type" in result.output
        assert "User Type" in result.output
        assert "USER" in result.output
        assert "item_brand" in result.output

    def test_custom_dimensions_list_scope_displayed(
        self, typer_runner: CliRunner
    ) -> None:
        """Assert scope column is present."""
        mock_client = MagicMock()
        mock_client.list_custom_dimensions.return_value = [
            _make_custom_dimension(
                "properties/123/customDimensions/1",
                "event_param",
                "Event Param",
                scope="EVENT",
            ),
        ]

        with (
            patch("ga4x.commands.custom_dimensions.load_config") as mock_cfg,
            patch(
                "ga4x.commands.custom_dimensions.build_admin_client",
                return_value=mock_client,
            ),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(app, ["custom-dimensions", "list", "123"])

        assert result.exit_code == 0
        assert "EVENT" in result.output

    def test_custom_dimensions_list_empty(self, typer_runner: CliRunner) -> None:
        """Empty list renders no-results placeholder."""
        mock_client = MagicMock()
        mock_client.list_custom_dimensions.return_value = []

        with (
            patch("ga4x.commands.custom_dimensions.load_config") as mock_cfg,
            patch(
                "ga4x.commands.custom_dimensions.build_admin_client",
                return_value=mock_client,
            ),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="json",
            )
            result = typer_runner.invoke(app, ["custom-dimensions", "list", "123"])

        assert result.exit_code == 0
        assert result.output.strip() == "[]"

    def test_custom_dimensions_list_auth_error(self, typer_runner: CliRunner) -> None:
        """Mock raises PermissionDenied; assert exit code is 2."""
        from google.api_core.exceptions import PermissionDenied

        mock_client = MagicMock()
        mock_client.list_custom_dimensions.side_effect = PermissionDenied("denied")

        with (
            patch("ga4x.commands.custom_dimensions.load_config") as mock_cfg,
            patch(
                "ga4x.commands.custom_dimensions.build_admin_client",
                return_value=mock_client,
            ),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(app, ["custom-dimensions", "list", "123"])

        assert result.exit_code == 2
