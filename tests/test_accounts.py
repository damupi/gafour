from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from ga4.cli import app


def _make_account(name: str, display_name: str, region_code: str = "US") -> MagicMock:
    """Helper to create a mock account proto object."""
    account = MagicMock()
    account.name = name
    account.display_name = display_name
    account.region_code = region_code
    account.create_time = None
    account.update_time = None
    return account


class TestAccountsList:
    def test_accounts_list_table(self, typer_runner: CliRunner) -> None:
        """Mock admin client returns 2 accounts; assert table output contains IDs and names."""
        mock_client = MagicMock()
        mock_client.list_accounts.return_value = [
            _make_account("accounts/111", "Alpha Corp"),
            _make_account("accounts/222", "Beta Ltd"),
        ]

        with (
            patch("ga4.commands.accounts.load_config") as mock_cfg,
            patch("ga4.commands.accounts.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="json",
            )
            result = typer_runner.invoke(app, ["accounts", "list", "--format", "table"])

        assert result.exit_code == 0
        assert "111" in result.output
        assert "222" in result.output
        assert "Alpha Corp" in result.output
        assert "Beta Ltd" in result.output

    def test_accounts_list_json(self, typer_runner: CliRunner) -> None:
        """Assert JSON output is valid and contains account data."""
        mock_client = MagicMock()
        mock_client.list_accounts.return_value = [
            _make_account("accounts/333", "Gamma Inc", "GB"),
        ]

        with (
            patch("ga4.commands.accounts.load_config") as mock_cfg,
            patch("ga4.commands.accounts.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="json",
            )
            result = typer_runner.invoke(app, ["accounts", "list", "--format", "json"])

        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        assert parsed[0]["Account ID"] == "333"
        assert parsed[0]["Name"] == "Gamma Inc"

    def test_accounts_list_empty(self, typer_runner: CliRunner) -> None:
        """Empty account list renders no-results placeholder."""
        mock_client = MagicMock()
        mock_client.list_accounts.return_value = []

        with (
            patch("ga4.commands.accounts.load_config") as mock_cfg,
            patch("ga4.commands.accounts.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="json",
            )
            result = typer_runner.invoke(app, ["accounts", "list"])

        assert result.exit_code == 0
        assert result.output.strip() == "[]"

    def test_accounts_list_auth_error(self, typer_runner: CliRunner) -> None:
        """Mock raises PermissionDenied; assert exit code is 2."""
        from google.api_core.exceptions import PermissionDenied

        mock_client = MagicMock()
        mock_client.list_accounts.side_effect = PermissionDenied("forbidden")

        with (
            patch("ga4.commands.accounts.load_config") as mock_cfg,
            patch("ga4.commands.accounts.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="json",
            )
            result = typer_runner.invoke(app, ["accounts", "list"])

        assert result.exit_code == 2


class TestAccountsGet:
    def test_accounts_get(self, typer_runner: CliRunner) -> None:
        """Mock returns 1 account; assert output contains its details."""
        mock_client = MagicMock()
        mock_client.get_account.return_value = _make_account(
            "accounts/999", "Delta Corp", "DE"
        )

        with (
            patch("ga4.commands.accounts.load_config") as mock_cfg,
            patch("ga4.commands.accounts.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="json",
            )
            result = typer_runner.invoke(app, ["accounts", "get", "999", "--format", "table"])

        assert result.exit_code == 0
        assert "999" in result.output
        assert "Delta Corp" in result.output

    def test_accounts_get_not_found(self, typer_runner: CliRunner) -> None:
        """Mock raises NotFound; assert exit code is 1."""
        from google.api_core.exceptions import NotFound

        mock_client = MagicMock()
        mock_client.get_account.side_effect = NotFound("not found")

        with (
            patch("ga4.commands.accounts.load_config") as mock_cfg,
            patch("ga4.commands.accounts.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="json",
            )
            result = typer_runner.invoke(app, ["accounts", "get", "000"])

        assert result.exit_code == 1

    def test_accounts_get_permission_denied(self, typer_runner: CliRunner) -> None:
        """Mock raises PermissionDenied; assert exit code is 2."""
        from google.api_core.exceptions import PermissionDenied

        mock_client = MagicMock()
        mock_client.get_account.side_effect = PermissionDenied("denied")

        with (
            patch("ga4.commands.accounts.load_config") as mock_cfg,
            patch("ga4.commands.accounts.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="json",
            )
            result = typer_runner.invoke(app, ["accounts", "get", "111"])

        assert result.exit_code == 2
