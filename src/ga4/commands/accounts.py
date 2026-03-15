from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from google.api_core import exceptions as google_exceptions  # type: ignore[import-untyped]

from ga4.auth import build_admin_client
from ga4.config import load_config
from ga4.errors import AccountNotFoundError, AuthError, GA4CLIError, NetworkError
from ga4.models.account import Account
from ga4.output import OutputFormat, print_error, render

accounts_app = typer.Typer(name="accounts", help="Manage GA4 accounts.")


def _account_to_dict(account: Account) -> dict[str, str]:
    """Convert an Account model to a flat dict for rendering."""
    return {
        "Account ID": account.account_id(),
        "Name": account.display_name,
        "Region": account.region_code or "",
        "Created": account.create_time or "",
    }


@accounts_app.command("list")
def accounts_list(
    format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", help="Output format."),
    ] = OutputFormat.JSON,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write output to file."),
    ] = None,
) -> None:
    """List all accessible GA4 accounts."""
    try:
        config = load_config()
        client = build_admin_client(config)
        pager = client.list_accounts()
        accounts = [
            Account(
                name=a.name,
                display_name=a.display_name,
                region_code=a.region_code or None,
                create_time=str(a.create_time) if a.create_time else None,
                update_time=str(a.update_time) if a.update_time else None,
            )
            for a in pager
        ]
        rows = [_account_to_dict(a) for a in accounts]
        columns = ["Account ID", "Name", "Region"]
        result = render(rows, format, columns)
        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except google_exceptions.PermissionDenied as exc:
        err = AuthError(
            message="Permission denied when listing accounts.",
            hint="Ensure your credentials have the Analytics Read & Analyze permission.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.NotFound as exc:
        err = GA4CLIError(message=f"Resource not found: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.InvalidArgument as exc:
        from ga4.errors import ValidationError

        err = ValidationError(message=f"Invalid request: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(
            message=f"API call failed: {exc}",
            hint="Check your network connection and try again.",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)


@accounts_app.command("get")
def accounts_get(
    account_id: Annotated[str, typer.Argument(help="The numeric account ID.")],
    format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", help="Output format."),
    ] = OutputFormat.JSON,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write output to file."),
    ] = None,
) -> None:
    """Get details for a specific GA4 account."""
    try:
        config = load_config()
        client = build_admin_client(config)
        a = client.get_account(name=f"accounts/{account_id}")
        account = Account(
            name=a.name,
            display_name=a.display_name,
            region_code=a.region_code or None,
            create_time=str(a.create_time) if a.create_time else None,
            update_time=str(a.update_time) if a.update_time else None,
        )
        rows = [_account_to_dict(account)]
        columns = ["Account ID", "Name", "Region", "Created"]
        result = render(rows, format, columns)
        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except google_exceptions.PermissionDenied as exc:
        err = AuthError(
            message=f"Permission denied accessing account '{account_id}'.",
            hint="Ensure your credentials have access to this account.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.NotFound as exc:
        err = AccountNotFoundError(account_id=account_id)
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.InvalidArgument as exc:
        from ga4.errors import ValidationError

        err = ValidationError(message=f"Invalid account ID '{account_id}': {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(
            message=f"API call failed: {exc}",
            hint="Check your network connection and try again.",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
