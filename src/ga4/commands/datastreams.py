from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from google.api_core import exceptions as google_exceptions  # type: ignore[import-untyped]

from ga4.auth import build_admin_client
from ga4.config import load_config
from ga4.errors import AuthError, GA4CLIError, NetworkError, ValidationError
from ga4.models.datastream import DataStream, WebStreamData
from ga4.output import OutputFormat, print_error, render, render_json_item, render_json_list

datastreams_app = typer.Typer(name="datastreams", help="Manage GA4 data streams.")


def _stream_to_dict(stream: DataStream) -> dict[str, str]:
    """Convert a DataStream model to a flat dict for rendering."""
    web_uri = ""
    measurement_id = ""
    if stream.web_stream_data:
        web_uri = stream.web_stream_data.default_uri or ""
        measurement_id = stream.web_stream_data.measurement_id or ""
    return {
        "Stream ID": stream.stream_id(),
        "Name": stream.display_name,
        "Type": stream.type_,
        "Measurement ID": measurement_id,
        "Default URI": web_uri,
        "Created": stream.create_time or "",
    }


def _parse_stream(s: object) -> DataStream:
    """Parse a proto stream object into a DataStream model."""
    web_data: WebStreamData | None = None
    raw_web = getattr(s, "web_stream_data", None)
    if raw_web is not None:
        web_data = WebStreamData(
            default_uri=getattr(raw_web, "default_uri", None) or None,
            measurement_id=getattr(raw_web, "measurement_id", None) or None,
        )
    stream_type_raw = getattr(s, "type_", None) or getattr(s, "type", None)
    stream_type = str(stream_type_raw) if stream_type_raw else "TYPE_UNSPECIFIED"
    return DataStream(
        **{
            "name": getattr(s, "name", ""),
            "display_name": getattr(s, "display_name", ""),
            "type": stream_type,
            "create_time": str(getattr(s, "create_time", None)) if getattr(s, "create_time", None) else None,
            "update_time": str(getattr(s, "update_time", None)) if getattr(s, "update_time", None) else None,
            "web_stream_data": web_data,
        }
    )


@datastreams_app.command("list")
def datastreams_list(
    property_id: Annotated[str, typer.Argument(help="The numeric property ID.")],
    format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", help="Output format."),
    ] = OutputFormat.JSON,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write output to file."),
    ] = None,
) -> None:
    """List all data streams for a GA4 property."""
    try:
        config = load_config()
        client = build_admin_client(config)
        pager = client.list_data_streams(parent=f"properties/{property_id}")
        streams = [_parse_stream(s) for s in pager]
        if format == OutputFormat.JSON:
            result = render_json_list(streams)
        else:
            result = render([_stream_to_dict(s) for s in streams], format, ["Stream ID", "Name", "Type", "Measurement ID", "Default URI"])
        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except google_exceptions.PermissionDenied as exc:
        err = AuthError(
            message=f"Permission denied listing data streams for property '{property_id}'.",
            hint="Ensure your credentials have the Analytics Read & Analyze permission.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.NotFound as exc:
        from ga4.errors import PropertyNotFoundError

        err = PropertyNotFoundError(property_id=property_id)
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.InvalidArgument as exc:
        err = ValidationError(message=f"Invalid request: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(message=f"API call failed: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)


@datastreams_app.command("get")
def datastreams_get(
    property_id: Annotated[str, typer.Argument(help="The numeric property ID.")],
    stream_id: Annotated[str, typer.Argument(help="The numeric stream ID.")],
    format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", help="Output format."),
    ] = OutputFormat.JSON,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write output to file."),
    ] = None,
) -> None:
    """Get details for a specific data stream."""
    try:
        config = load_config()
        client = build_admin_client(config)
        s = client.get_data_stream(
            name=f"properties/{property_id}/dataStreams/{stream_id}"
        )
        stream = _parse_stream(s)
        if format == OutputFormat.JSON:
            result = render_json_item(stream)
        else:
            result = render([_stream_to_dict(stream)], format, ["Stream ID", "Name", "Type", "Measurement ID", "Default URI", "Created"])
        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)
    except GA4CLIError as exc:
        print_error(exc)
        raise typer.Exit(exc.exit_code)
    except google_exceptions.PermissionDenied as exc:
        err = AuthError(
            message=f"Permission denied accessing stream '{stream_id}'.",
            hint="Ensure your credentials have access to this property.",
            recovery_command="ga4 auth status",
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.NotFound as exc:
        err = GA4CLIError(
            message=f"Data stream 'properties/{property_id}/dataStreams/{stream_id}' not found."
        )
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.InvalidArgument as exc:
        err = ValidationError(message=f"Invalid request: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)
    except google_exceptions.GoogleAPICallError as exc:
        err = NetworkError(message=f"API call failed: {exc}")
        print_error(err)
        raise typer.Exit(err.exit_code)


@datastreams_app.command("create")
def datastreams_create() -> None:
    """Create a new data stream. (Not yet implemented)"""
    typer.echo("Not yet implemented")
    raise typer.Exit(0)


@datastreams_app.command("delete")
def datastreams_delete() -> None:
    """Delete a data stream. (Not yet implemented)"""
    typer.echo("Not yet implemented")
    raise typer.Exit(0)
