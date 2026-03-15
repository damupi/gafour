from __future__ import annotations

import csv
import io
import json
import sys
from enum import Enum
from typing import Any

from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

from ga4.errors import GA4CLIError
from ga4.models.report import ReportResponse

_stderr_console = Console(stderr=True)
_stdout_console = Console()


class OutputFormat(str, Enum):
    """Supported output formats for CLI commands."""

    TABLE = "table"
    JSON = "json"
    CSV = "csv"


def proto_to_dict(obj: Any) -> dict[str, Any]:
    """Convert a google proto-plus object to a plain Python dict.

    Uses the class-level ``to_dict`` method provided by proto-plus generated
    classes.  Falls back to ``vars()`` for plain objects.

    Args:
        obj: A proto-plus message instance or any object.

    Returns:
        Dictionary representation of the object.
    """
    cls = type(obj)
    if hasattr(cls, "to_dict"):
        result: dict[str, Any] = cls.to_dict(obj)
        return result
    return dict(vars(obj))


def render(
    data: list[dict[str, Any]],
    format: OutputFormat,
    columns: list[str] | None = None,
) -> str:
    """Render a list of dicts to a string in the requested format.

    Args:
        data: List of row dictionaries to render.
        format: Output format (TABLE, JSON, or CSV).
        columns: Optional ordered list of column names to include. When
            omitted all keys from the first row are used.

    Returns:
        Rendered string output.
    """
    if not data:
        if format == OutputFormat.JSON:
            return "[]"
        if format == OutputFormat.CSV:
            return ""
        return "(no results)"

    effective_columns: list[str] = columns if columns is not None else list(data[0].keys())

    if format == OutputFormat.JSON:
        return _render_json(data)
    elif format == OutputFormat.CSV:
        return _render_csv(data, effective_columns)
    else:
        return _render_table(data, effective_columns)


def _render_json(data: list[dict[str, Any]]) -> str:
    """Serialize data as indented JSON."""
    return json.dumps(data, indent=2, default=str)


def _render_csv(data: list[dict[str, Any]], columns: list[str]) -> str:
    """Serialize data as CSV with a header row."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(data)
    return buf.getvalue()


def _render_table(data: list[dict[str, Any]], columns: list[str]) -> str:
    """Render data as a Rich table and capture it to a string."""
    table = Table(show_header=True, header_style="bold cyan")
    for col in columns:
        table.add_column(col)

    for row in data:
        table.add_row(*[str(row.get(col, "")) for col in columns])

    buf = io.StringIO()
    capture_console = Console(file=buf, highlight=False, width=200)
    capture_console.print(table)
    return buf.getvalue()


def print_error(error: GA4CLIError) -> None:
    """Print a formatted error to stderr using Rich.

    Displays the error message and, when present, the hint and recovery
    command.

    Args:
        error: The GA4CLIError instance to display.
    """
    _stderr_console.print(f"[bold red]Error:[/bold red] {error.message}")
    if error.hint:
        _stderr_console.print(f"[yellow]  {error.hint}[/yellow]")
    if error.recovery_command:
        _stderr_console.print(f"[dim]  Try:[/dim] [cyan]{error.recovery_command}[/cyan]")


def render_json_item(item: BaseModel) -> str:
    """Serialize a single Pydantic model as indented JSON."""
    return item.model_dump_json(indent=2)


def render_json_list(items: list[BaseModel]) -> str:
    """Serialize a list of Pydantic models as indented JSON."""
    return json.dumps([item.model_dump(mode="json") for item in items], indent=2)


def render_report(report: ReportResponse) -> str:
    """Serialize a ReportResponse as indented JSON.

    Report commands always output JSON — the structured response is designed
    for agent/programmatic consumption and does not have a meaningful
    table or CSV representation.
    """
    return report.model_dump_json(indent=2)


def print_success(message: str) -> None:
    """Print a success message to stdout with a green checkmark.

    Args:
        message: The message to display.
    """
    _stdout_console.print(f"[bold green]✓[/bold green] {message}")
