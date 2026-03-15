from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ga4x.cli import app
from ga4x.config import Config


@pytest.fixture()
def tmp_config(tmp_path: Path) -> Path:
    """Return a temporary config file path."""
    return tmp_path / "config.json"


class TestConfigShow:
    def test_show_default_config(self, typer_runner: CliRunner) -> None:
        """config show prints valid JSON with default values."""
        with patch("ga4x.commands.config.load_config", return_value=Config()):
            result = typer_runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["auth_method"] == "service-account"
        assert data["output_format"] == "json"

    def test_show_reflects_saved_values(self, typer_runner: CliRunner) -> None:
        """config show reflects non-default config values."""
        cfg = Config(
            auth_method="token",
            access_token="tok123",
            default_property_id="999",
            output_format="csv",
        )
        with patch("ga4x.commands.config.load_config", return_value=cfg):
            result = typer_runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["auth_method"] == "token"
        assert data["access_token"] == "tok123"
        assert data["default_property_id"] == "999"
        assert data["output_format"] == "csv"


class TestConfigSet:
    def test_set_valid_key(self, typer_runner: CliRunner) -> None:
        """config set saves a valid key and prints success."""
        with (
            patch("ga4x.commands.config.load_config", return_value=Config()),
            patch("ga4x.commands.config.save_config") as mock_save,
        ):
            result = typer_runner.invoke(app, ["config", "set", "output_format", "csv"])
        assert result.exit_code == 0
        assert "output_format" in result.output
        saved: Config = mock_save.call_args[0][0]
        assert saved.output_format == "csv"

    def test_set_default_property_id(self, typer_runner: CliRunner) -> None:
        """config set persists default_property_id correctly."""
        with (
            patch("ga4x.commands.config.load_config", return_value=Config()),
            patch("ga4x.commands.config.save_config") as mock_save,
        ):
            result = typer_runner.invoke(
                app, ["config", "set", "default_property_id", "123456"]
            )
        assert result.exit_code == 0
        saved: Config = mock_save.call_args[0][0]
        assert saved.default_property_id == "123456"

    def test_set_invalid_key(self, typer_runner: CliRunner) -> None:
        """config set exits with code 3 for unknown key."""
        result = typer_runner.invoke(app, ["config", "set", "bogus_key", "value"])
        assert result.exit_code == 3


class TestConfigUnset:
    def test_unset_clears_key(self, typer_runner: CliRunner) -> None:
        """config unset resets a key to its default."""
        cfg = Config(default_property_id="123456")
        with (
            patch("ga4x.commands.config.load_config", return_value=cfg),
            patch("ga4x.commands.config.save_config") as mock_save,
        ):
            result = typer_runner.invoke(app, ["config", "unset", "default_property_id"])
        assert result.exit_code == 0
        saved: Config = mock_save.call_args[0][0]
        assert saved.default_property_id is None

    def test_unset_output_format_resets_to_json(self, typer_runner: CliRunner) -> None:
        """config unset output_format resets to 'json'."""
        cfg = Config(output_format="csv")
        with (
            patch("ga4x.commands.config.load_config", return_value=cfg),
            patch("ga4x.commands.config.save_config") as mock_save,
        ):
            result = typer_runner.invoke(app, ["config", "unset", "output_format"])
        assert result.exit_code == 0
        saved: Config = mock_save.call_args[0][0]
        assert saved.output_format == "json"

    def test_unset_invalid_key(self, typer_runner: CliRunner) -> None:
        """config unset exits with code 3 for unknown key."""
        result = typer_runner.invoke(app, ["config", "unset", "bogus_key"])
        assert result.exit_code == 3


class TestConfigInit:
    def test_init_service_account(self, typer_runner: CliRunner, tmp_path: Path) -> None:
        """config init with service-account method saves key_file path."""
        fake_key = tmp_path / "key.json"
        fake_key.write_text("{}", encoding="utf-8")

        with (
            patch("ga4x.commands.config.load_config", return_value=Config()),
            patch("ga4x.commands.config.save_config") as mock_save,
        ):
            result = typer_runner.invoke(
                app,
                ["config", "init"],
                input=f"1\n{fake_key}\n\n1\n",  # method=1, key path, skip property, format=1
            )
        assert result.exit_code == 0
        saved: Config = mock_save.call_args[0][0]
        assert saved.auth_method == "service-account"
        assert saved.key_file == str(fake_key)

    def test_init_token(self, typer_runner: CliRunner) -> None:
        """config init with token method saves access_token."""
        with (
            patch("ga4x.commands.config.load_config", return_value=Config()),
            patch("ga4x.commands.config.save_config") as mock_save,
        ):
            result = typer_runner.invoke(
                app,
                ["config", "init"],
                input="2\nmysecrettoken\n999\n2\n",  # method=2, token, property, format=2
            )
        assert result.exit_code == 0
        saved: Config = mock_save.call_args[0][0]
        assert saved.auth_method == "token"
        assert saved.access_token == "mysecrettoken"
        assert saved.default_property_id == "999"
        assert saved.output_format == "json"

    def test_init_oauth2_falls_back(self, typer_runner: CliRunner) -> None:
        """config init with oauth2 warns and keeps existing method."""
        existing = Config(auth_method="service-account", key_file="/existing/key.json")
        with (
            patch("ga4x.commands.config.load_config", return_value=existing),
            patch("ga4x.commands.config.save_config") as mock_save,
        ):
            result = typer_runner.invoke(
                app,
                ["config", "init"],
                input="3\n\n1\n",  # method=3 (oauth2), skip property, format=1
            )
        assert result.exit_code == 0
        saved: Config = mock_save.call_args[0][0]
        # Should keep existing auth method since oauth2 not implemented
        assert saved.auth_method == "service-account"

    def test_init_preserves_existing_defaults(self, typer_runner: CliRunner) -> None:
        """Re-running config init with empty inputs keeps existing values."""
        existing = Config(
            auth_method="service-account",
            key_file="/my/key.json",
            default_property_id="42",
            output_format="csv",
        )
        with (
            patch("ga4x.commands.config.load_config", return_value=existing),
            patch("ga4x.commands.config.save_config") as mock_save,
        ):
            # Press Enter on every prompt to accept existing defaults
            result = typer_runner.invoke(
                app,
                ["config", "init"],
                input="\n\n\n\n",
            )
        assert result.exit_code == 0
        saved: Config = mock_save.call_args[0][0]
        assert saved.key_file == "/my/key.json"
        assert saved.default_property_id == "42"
