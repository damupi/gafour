from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from gafour.cli import app
from gafour.config import Config
from gafour.errors import AuthError


# ---------------------------------------------------------------------------
# Config: OAuth2 fields
# ---------------------------------------------------------------------------


class TestConfigOAuth2Fields:
    def test_default_oauth2_fields_are_none(self) -> None:
        """Config defaults leave oauth2 fields unset."""
        cfg = Config()
        assert cfg.oauth2_client_secret_file is None
        assert cfg.oauth2_credentials is None

    def test_oauth2_fields_round_trip(self) -> None:
        """oauth2_credentials dict survives model_dump_json / model_validate."""
        creds = {
            "token": "ya29.abc",
            "refresh_token": "1//refresh",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "client.apps.googleusercontent.com",
            "client_secret": "secret",
            "scopes": ["https://www.googleapis.com/auth/analytics.readonly"],
            "expiry": "2026-04-19T15:00:00+00:00",
        }
        cfg = Config(
            auth_method="oauth2",
            oauth2_client_secret_file="/home/user/.config/gafour/client_secret.json",
            oauth2_credentials=creds,
        )
        raw = cfg.model_dump_json()
        restored = Config.model_validate_json(raw)
        assert restored.auth_method == "oauth2"
        assert restored.oauth2_client_secret_file == "/home/user/.config/gafour/client_secret.json"
        assert restored.oauth2_credentials["refresh_token"] == "1//refresh"


# ---------------------------------------------------------------------------
# auth._build_oauth2_credentials
# ---------------------------------------------------------------------------


class TestBuildOAuth2Credentials:
    def test_raises_when_no_credentials_stored(self) -> None:
        """AuthError raised when oauth2_credentials is None."""
        from gafour.auth import _build_oauth2_credentials

        cfg = Config(auth_method="oauth2")
        with pytest.raises(AuthError, match="No OAuth2 credentials stored"):
            _build_oauth2_credentials(cfg)

    def test_builds_credentials_from_stored_dict(self) -> None:
        """Valid stored dict produces a Credentials object with matching fields."""
        from gafour.auth import _build_oauth2_credentials

        stored = {
            "token": "ya29.valid",
            "refresh_token": "1//refresh",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "scopes": ["https://www.googleapis.com/auth/analytics.readonly"],
            "expiry": None,
        }
        cfg = Config(auth_method="oauth2", oauth2_credentials=stored)

        mock_creds = MagicMock()
        mock_creds.expired = False
        mock_creds.valid = True

        with patch("gafour.auth.Credentials", return_value=mock_creds) as mock_cls:
            result = _build_oauth2_credentials(cfg)

        mock_cls.assert_called_once()
        call_kwargs = mock_cls.call_args.kwargs
        assert call_kwargs["token"] == "ya29.valid"
        assert call_kwargs["refresh_token"] == "1//refresh"
        assert result is mock_creds

    def test_refreshes_expired_credentials(self) -> None:
        """Expired credentials are refreshed and config is updated."""
        from gafour.auth import _build_oauth2_credentials

        stored = {
            "token": "ya29.expired",
            "refresh_token": "1//refresh",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "scopes": ["https://www.googleapis.com/auth/analytics.readonly"],
            "expiry": "2020-01-01T00:00:00+00:00",
        }
        cfg = Config(auth_method="oauth2", oauth2_credentials=stored)

        mock_creds = MagicMock()
        mock_creds.expired = True
        mock_creds.refresh_token = "1//refresh"
        mock_creds.token = "ya29.new"
        mock_creds.expiry = datetime(2026, 4, 19, 15, 0, 0, tzinfo=timezone.utc)
        mock_creds.token_uri = "https://oauth2.googleapis.com/token"
        mock_creds.client_id = "client_id"
        mock_creds.client_secret = "client_secret"
        mock_creds.scopes = ["https://www.googleapis.com/auth/analytics.readonly"]

        with (
            patch("gafour.auth.Credentials", return_value=mock_creds),
            patch("gafour.auth.Request"),
            patch("gafour.auth.save_config") as mock_save,
        ):
            _build_oauth2_credentials(cfg)

        mock_creds.refresh.assert_called_once()
        mock_save.assert_called_once()
        saved_cfg: Config = mock_save.call_args[0][0]
        assert saved_cfg.oauth2_credentials["token"] == "ya29.new"


# ---------------------------------------------------------------------------
# auth login --method oauth2 (CLI)
# ---------------------------------------------------------------------------


class TestAuthLoginOAuth2:
    def test_login_oauth2_saves_credentials(
        self, typer_runner: CliRunner, tmp_path: Path
    ) -> None:
        """auth login --method oauth2 runs flow and saves credentials to config."""
        secret_file = tmp_path / "client_secret.json"
        secret_file.write_text("{}", encoding="utf-8")

        mock_creds = MagicMock()
        mock_creds.token = "ya29.new"
        mock_creds.refresh_token = "1//refresh"
        mock_creds.token_uri = "https://oauth2.googleapis.com/token"
        mock_creds.client_id = "client_id"
        mock_creds.client_secret = "client_secret"
        mock_creds.scopes = ["https://www.googleapis.com/auth/analytics.readonly"]
        mock_creds.expiry = None

        mock_flow = MagicMock()
        mock_flow.run_local_server.return_value = mock_creds

        with (
            patch("gafour.commands.auth.load_config", return_value=Config()),
            patch("gafour.commands.auth.save_config") as mock_save,
            patch("gafour.commands.auth.InstalledAppFlow") as mock_flow_cls,
        ):
            mock_flow_cls.from_client_secrets_file.return_value = mock_flow
            result = typer_runner.invoke(
                app,
                ["auth", "login", "--method", "oauth2"],
                input=f"{secret_file}\n",
            )

        assert result.exit_code == 0, result.output
        assert "Authentication configured" in result.output
        mock_flow.run_local_server.assert_called_once_with(port=0, open_browser=True)
        saved: Config = mock_save.call_args[0][0]
        assert saved.auth_method == "oauth2"
        assert saved.oauth2_credentials["token"] == "ya29.new"
        assert saved.oauth2_credentials["refresh_token"] == "1//refresh"

    def test_login_unsupported_method_exits(self, typer_runner: CliRunner) -> None:
        """auth login with an unknown method exits with code 2."""
        result = typer_runner.invoke(app, ["auth", "login", "--method", "magic"])
        assert result.exit_code == 2


# ---------------------------------------------------------------------------
# auth status (oauth2 method)
# ---------------------------------------------------------------------------


class TestAuthStatusOAuth2:
    def test_status_shows_oauth2_method(self, typer_runner: CliRunner) -> None:
        """auth status shows method: oauth2 and credential expiry."""
        stored = {
            "token": "ya29.abc",
            "refresh_token": "1//refresh",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "client_id",
            "client_secret": "secret",
            "scopes": ["https://www.googleapis.com/auth/analytics.readonly"],
            "expiry": "2026-12-31T00:00:00+00:00",
        }
        cfg = Config(auth_method="oauth2", oauth2_credentials=stored)

        mock_admin = MagicMock()
        mock_admin.list_accounts.return_value = iter([MagicMock()])

        with (
            patch("gafour.commands.auth.load_config", return_value=cfg),
            patch("gafour.auth.build_admin_client", return_value=mock_admin),
            patch("gafour.commands.auth.build_admin_client", return_value=mock_admin),
        ):
            result = typer_runner.invoke(app, ["auth", "status"])

        assert result.exit_code == 0, result.output
        assert "oauth2" in result.output


# ---------------------------------------------------------------------------
# auth logout (oauth2 method)
# ---------------------------------------------------------------------------


class TestAuthLogoutOAuth2:
    def test_logout_clears_oauth2_credentials(self, typer_runner: CliRunner) -> None:
        """auth logout clears oauth2_credentials and oauth2_client_secret_file."""
        stored = {
            "token": "ya29.abc",
            "refresh_token": "1//refresh",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "client_id",
            "client_secret": "secret",
            "scopes": ["https://www.googleapis.com/auth/analytics.readonly"],
            "expiry": None,
        }
        cfg = Config(
            auth_method="oauth2",
            oauth2_credentials=stored,
            oauth2_client_secret_file="/path/to/secret.json",
        )

        with (
            patch("gafour.commands.auth.load_config", return_value=cfg),
            patch("gafour.commands.auth.save_config") as mock_save,
        ):
            result = typer_runner.invoke(app, ["auth", "logout"])

        assert result.exit_code == 0, result.output
        saved: Config = mock_save.call_args[0][0]
        assert saved.oauth2_credentials is None
        assert saved.oauth2_client_secret_file is None
