from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from ga4.errors import ConfigError

CONFIG_PATH = Path.home() / ".config" / "ga4" / "config.json"

AuthMethod = Literal["oauth2", "service-account", "token"]
OutputFormatLiteral = Literal["table", "json", "csv"]


class Config(BaseModel):
    """GA4 CLI configuration.

    Attributes:
        auth_method: Authentication method to use.
        key_file: Path to service account JSON key file.
        access_token: Bearer access token for token auth.
        default_property_id: Default GA4 property ID used when --property-id is omitted.
        output_format: Default output format for commands.
    """

    model_config = ConfigDict(populate_by_name=True)

    auth_method: AuthMethod = "service-account"
    key_file: str | None = None
    access_token: str | None = None
    default_property_id: str | None = None
    output_format: OutputFormatLiteral = "json"


def load_config() -> Config:
    """Load configuration from disk and apply environment variable overrides.

    Environment variables (override file values):
        GA4_AUTH_METHOD: Authentication method.
        GA4_KEY_FILE: Path to service account key file.
        GOOGLE_APPLICATION_CREDENTIALS: Path to service account key file (ADC standard).
        GA4_ACCESS_TOKEN: Bearer access token.
        GA4_PROPERTY_ID: Default property ID.

    Returns:
        Populated Config instance.

    Raises:
        ConfigError: If the config file exists but cannot be parsed.
    """
    data: dict[str, object] = {}

    if CONFIG_PATH.exists():
        try:
            raw = CONFIG_PATH.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (json.JSONDecodeError, OSError) as exc:
            raise ConfigError(
                message=f"Failed to read config file: {CONFIG_PATH}",
                hint="The config file may be corrupted. Delete it and run 'ga4 auth login' to reconfigure.",
                recovery_command="ga4 auth login",
            ) from exc

    # Environment variable overrides
    if auth_method := os.environ.get("GA4_AUTH_METHOD"):
        data["auth_method"] = auth_method

    # GA4_KEY_FILE takes precedence over GOOGLE_APPLICATION_CREDENTIALS
    if key_file := os.environ.get("GA4_KEY_FILE"):
        data["key_file"] = key_file
    elif adc := os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        data["key_file"] = adc

    if access_token := os.environ.get("GA4_ACCESS_TOKEN"):
        data["access_token"] = access_token

    if property_id := os.environ.get("GA4_PROPERTY_ID"):
        data["default_property_id"] = property_id

    return Config.model_validate(data)


def save_config(config: Config) -> None:
    """Persist configuration to disk.

    Creates the config directory if it does not exist.

    Args:
        config: The Config instance to persist.

    Raises:
        ConfigError: If the config file cannot be written.
    """
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(
            config.model_dump_json(indent=2, exclude_none=False),
            encoding="utf-8",
        )
    except OSError as exc:
        raise ConfigError(
            message=f"Failed to write config file: {CONFIG_PATH}",
            hint="Check that you have write permissions to ~/.config/ga4/.",
        ) from exc
