from __future__ import annotations

from pathlib import Path

import typer

from gafour.config import CONFIG_PATH, Config, load_config, save_config
from gafour.errors import GA4CLIError, ValidationError
from gafour.output import print_error, print_success

config_app = typer.Typer(name="config", help="Manage GA4 CLI configuration.")

_VALID_KEYS = frozenset(
    {
        "auth_method",
        "key_file",
        "access_token",
        "default_property_id",
        "output_format",
    }
)


@config_app.command("show")
def config_show() -> None:
    """Print the current GA4 CLI configuration as JSON."""
    try:
        config = load_config()
        typer.echo(config.model_dump_json(indent=2))
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)


@config_app.command("set")
def config_set(
    key: str = typer.Argument(help="Configuration key to update."),
    value: str = typer.Argument(help="New value for the key."),
) -> None:
    """Update a single configuration value.

    Valid keys: auth_method, key_file, access_token, default_property_id, output_format.
    """
    if key not in _VALID_KEYS:
        err = ValidationError(
            message=f"Unknown configuration key: '{key}'.",
            hint=f"Valid keys are: {', '.join(sorted(_VALID_KEYS))}",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)

    try:
        config = load_config()
    except GA4CLIError:
        from gafour.config import Config

        config = Config()

    try:
        updated = config.model_copy(update={key: value})
    except Exception as exc:
        err = ValidationError(
            message=f"Invalid value '{value}' for key '{key}': {exc}",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)

    try:
        save_config(updated)
        print_success(f"Set {key} = {value}")
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)


@config_app.command("unset")
def config_unset(
    key: str = typer.Argument(help="Configuration key to clear."),
) -> None:
    """Clear a single configuration value (reset to default).

    Valid keys: auth_method, key_file, access_token, default_property_id, output_format.
    """
    if key not in _VALID_KEYS:
        err = ValidationError(
            message=f"Unknown configuration key: '{key}'.",
            hint=f"Valid keys are: {', '.join(sorted(_VALID_KEYS))}",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)

    try:
        config = load_config()
    except GA4CLIError:
        config = Config()

    defaults: dict[str, object] = {
        "auth_method": "service-account",
        "key_file": None,
        "access_token": None,
        "default_property_id": None,
        "output_format": "json",
    }
    updated = config.model_copy(update={key: defaults[key]})

    try:
        save_config(updated)
        print_success(f"Cleared {key} (reset to default)")
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)


@config_app.command("init")
def config_init() -> None:
    """Interactive configuration wizard.

    Walks you through setting up authentication and default options,
    then writes the result to ~/.config/ga4/config.json.
    """
    typer.echo("GA4 CLI — configuration wizard")
    typer.echo(f"Config will be saved to: {CONFIG_PATH}\n")

    # Load existing config as defaults so re-running init is non-destructive
    try:
        existing = load_config()
    except GA4CLIError:
        existing = Config()

    # --- Auth method ---
    typer.echo("Authentication method:")
    typer.echo("  [1] service-account  (recommended for scripts/CI)")
    typer.echo("  [2] token            (direct access token)")
    typer.echo("  [3] oauth2           (browser-based, not yet implemented)")
    method_map = {"1": "service-account", "2": "token", "3": "oauth2"}
    current_method_num = {"service-account": "1", "token": "2", "oauth2": "3"}.get(
        existing.auth_method, "1"
    )
    choice = typer.prompt(
        "Choose auth method",
        default=current_method_num,
    )
    auth_method = method_map.get(choice, "service-account")

    # --- Auth credentials ---
    key_file: str | None = existing.key_file
    access_token: str | None = existing.access_token

    if auth_method == "service-account":
        raw = typer.prompt(
            "Path to service account JSON key file",
            default=existing.key_file or "",
        )
        key_file = raw.strip() or None
        if key_file and not Path(key_file).exists():
            typer.echo(f"  Warning: file not found at '{key_file}' — saved anyway.")
        access_token = None

    elif auth_method == "token":
        raw = typer.prompt(
            "Access token",
            default=existing.access_token or "",
            hide_input=True,
        )
        access_token = raw.strip() or None
        key_file = None

    elif auth_method == "oauth2":
        typer.echo(
            "  OAuth2 browser flow is not yet implemented. "
            "Use 'service-account' or 'token' for now."
        )
        auth_method = existing.auth_method

    # --- Default property ---
    raw_prop = typer.prompt(
        "\nDefault property ID (press Enter to skip)",
        default=existing.default_property_id or "",
    )
    default_property_id: str | None = raw_prop.strip() or None

    # --- Output format ---
    typer.echo("\nDefault output format:")
    typer.echo("  [1] table  (human-readable)")
    typer.echo("  [2] json   (machine-readable)")
    typer.echo("  [3] csv    (spreadsheet-friendly)")
    fmt_map = {"1": "table", "2": "json", "3": "csv"}
    current_fmt_num = {"table": "1", "json": "2", "csv": "3"}.get(
        existing.output_format, "2"
    )
    fmt_choice = typer.prompt("Choose output format", default=current_fmt_num)
    output_format = fmt_map.get(fmt_choice, "json")

    # --- Save ---
    config = Config(
        auth_method=auth_method,  # type: ignore[arg-type]
        key_file=key_file,
        access_token=access_token,
        default_property_id=default_property_id,
        output_format=output_format,  # type: ignore[arg-type]
    )

    try:
        save_config(config)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)

    typer.echo("")
    print_success(f"Configuration saved to {CONFIG_PATH}")
    typer.echo("\nRun 'ga4 config show' to review your settings.")
    typer.echo("Run 'ga4 auth status' to verify connectivity.")
