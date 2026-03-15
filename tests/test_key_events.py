from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from ga4x.cli import app


def _make_key_event(
    name: str,
    event_name: str,
    counting_method: str = "ONCE_PER_EVENT",
    deletable: bool = True,
    custom: bool = False,
) -> MagicMock:
    ke = MagicMock()
    ke.name = name
    ke.event_name = event_name
    ke.counting_method = counting_method
    ke.deletable = deletable
    ke.custom = custom
    ke.create_time = None
    return ke


class TestKeyEventsList:
    def test_key_events_list(self, typer_runner: CliRunner) -> None:
        """Mock list_key_events; assert output contains event names."""
        mock_client = MagicMock()
        mock_client.list_key_events.return_value = [
            _make_key_event("properties/123/keyEvents/1", "purchase"),
            _make_key_event("properties/123/keyEvents/2", "sign_up", custom=True),
        ]

        with (
            patch("ga4x.commands.key_events.load_config") as mock_cfg,
            patch("ga4x.commands.key_events.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(app, ["key-events", "list", "123"])

        assert result.exit_code == 0
        assert "purchase" in result.output
        assert "sign_up" in result.output

    def test_key_events_list_counting_method_shown(
        self, typer_runner: CliRunner
    ) -> None:
        """Assert counting method is shown in output."""
        mock_client = MagicMock()
        mock_client.list_key_events.return_value = [
            _make_key_event(
                "properties/123/keyEvents/1",
                "purchase",
                counting_method="ONCE_PER_SESSION",
            ),
        ]

        with (
            patch("ga4x.commands.key_events.load_config") as mock_cfg,
            patch("ga4x.commands.key_events.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(app, ["key-events", "list", "123"])

        assert result.exit_code == 0
        assert "ONCE_PER_SESSION" in result.output

    def test_key_events_list_empty(self, typer_runner: CliRunner) -> None:
        """Empty key events list renders no-results placeholder."""
        mock_client = MagicMock()
        mock_client.list_key_events.return_value = []

        with (
            patch("ga4x.commands.key_events.load_config") as mock_cfg,
            patch("ga4x.commands.key_events.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="json",
            )
            result = typer_runner.invoke(app, ["key-events", "list", "123"])

        assert result.exit_code == 0
        assert result.output.strip() == "[]"

    def test_key_events_list_auth_error(self, typer_runner: CliRunner) -> None:
        """Mock raises PermissionDenied; assert exit code is 2."""
        from google.api_core.exceptions import PermissionDenied

        mock_client = MagicMock()
        mock_client.list_key_events.side_effect = PermissionDenied("denied")

        with (
            patch("ga4x.commands.key_events.load_config") as mock_cfg,
            patch("ga4x.commands.key_events.build_admin_client", return_value=mock_client),
        ):
            mock_cfg.return_value = MagicMock(
                auth_method="service-account",
                key_file="/fake/key.json",
                default_property_id=None,
                output_format="table",
            )
            result = typer_runner.invoke(app, ["key-events", "list", "123"])

        assert result.exit_code == 2
