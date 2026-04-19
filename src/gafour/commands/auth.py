from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from gafour.auth import build_admin_client, _serialize_credentials
from gafour.config import ANALYTICS_SCOPES, AuthMethod, load_config, save_config
from gafour.errors import AuthError, GA4CLIError
from gafour.output import print_error, print_success

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    InstalledAppFlow = None  # type: ignore[assignment,misc]

auth_app = typer.Typer(name="auth", help="Manage GA4 CLI authentication.")

_DEFAULT_CLIENT_SECRET = str(Path.home() / ".config" / "gafour" / "client_secret.json")


@auth_app.command("login")
def auth_login(
    method: Annotated[
        Optional[str],
        typer.Option(
            "--method",
            "-m",
            help="Authentication method: oauth2, service-account, or token.",
        ),
    ] = None,
) -> None:
    """Configure authentication credentials for the GA4 CLI.

    For oauth2: opens a browser to authenticate with your Google account (recommended).
    For service-account: provide the path to your service account JSON key file.
    For token: provide a valid OAuth2 access token.
    """
    try:
        config = load_config()
    except GA4CLIError:
        from gafour.config import Config

        config = Config()

    effective_method = method or "oauth2"

    if effective_method not in ("oauth2", "service-account", "token"):
        err = AuthError(
            message=f"Unsupported auth method: '{effective_method}'.",
            hint="Supported methods are: oauth2, service-account, token.",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)

    config.auth_method = effective_method  # type: ignore[assignment]

    if effective_method == "oauth2":
        if InstalledAppFlow is None:
            err = AuthError(
                message="google-auth-oauthlib is not installed.",
                hint="Run: pip install google-auth-oauthlib",
            )
            print_error(err)
            raise typer.Exit(err.exit_code)

        secret_file = typer.prompt(
            "Path to OAuth2 client secret JSON",
            default=config.oauth2_client_secret_file or _DEFAULT_CLIENT_SECRET,
        )
        flow = InstalledAppFlow.from_client_secrets_file(secret_file, scopes=ANALYTICS_SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
        config.oauth2_client_secret_file = secret_file.strip()
        config.oauth2_credentials = _serialize_credentials(creds)

    elif effective_method == "service-account":
        key_file = typer.prompt(
            "Path to service account JSON key file",
            default=config.key_file or "",
        )
        if not key_file:
            err = AuthError(
                message="Key file path cannot be empty.",
                hint="Provide the full path to your service account JSON key file.",
            )
            print_error(err)
            raise typer.Exit(err.exit_code)
        config.key_file = key_file.strip()

    elif effective_method == "token":
        token = typer.prompt("Access token", hide_input=True)
        if not token:
            err = AuthError(
                message="Access token cannot be empty.",
            )
            print_error(err)
            raise typer.Exit(err.exit_code)
        config.access_token = token.strip()

    try:
        save_config(config)
        print_success(f"Authentication configured using method: {effective_method}")
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)


@auth_app.command("status")
def auth_status() -> None:
    """Check the current authentication configuration and verify connectivity."""
    try:
        config = load_config()
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)

    typer.echo(f"Auth method:   {config.auth_method}")

    if config.auth_method == "service-account":
        typer.echo(f"Key file:      {config.key_file or '(not set)'}")
    elif config.auth_method == "token":
        token_preview = (
            config.access_token[:8] + "..." if config.access_token else "(not set)"
        )
        typer.echo(f"Access token:  {token_preview}")
    elif config.auth_method == "oauth2":
        expiry = (config.oauth2_credentials or {}).get("expiry", "(not set)")
        typer.echo(f"Token expiry:  {expiry}")

    typer.echo(f"Default property: {config.default_property_id or '(not set)'}")

    # Attempt to build a client to verify credentials work
    try:
        from gafour.auth import build_admin_client

        client = build_admin_client(config)
        # Make a lightweight call to verify connectivity
        next(iter(client.list_accounts()), None)
        print_success("Credentials are valid and API is reachable.")
    except AuthError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except Exception as exc:
        err = AuthError(
            message=f"Could not verify credentials: {exc}",
            hint="Run 'gafour auth login' to reconfigure authentication.",
            recovery_command="gafour auth login",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)


@auth_app.command("logout")
def auth_logout() -> None:
    """Remove stored credentials from the GA4 CLI configuration."""
    try:
        config = load_config()
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)

    config.key_file = None
    config.access_token = None
    config.oauth2_credentials = None
    config.oauth2_client_secret_file = None

    try:
        save_config(config)
        print_success("Credentials removed from configuration.")
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
