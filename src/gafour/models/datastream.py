from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class WebStreamData(BaseModel):
    """Web-specific data stream metadata.

    Attributes:
        default_uri: Default measurement URI (website URL).
        measurement_id: The ``G-XXXXXXXX`` measurement ID.
    """

    model_config = ConfigDict(populate_by_name=True)

    default_uri: str | None = None
    measurement_id: str | None = None


class DataStream(BaseModel):
    """Represents a GA4 data stream.

    Attributes:
        name: Full resource name, e.g. ``properties/123/dataStreams/456``.
        display_name: Human-readable stream name.
        type_: Stream type (``WEB_DATA_STREAM``, ``ANDROID_APP_DATA_STREAM``, etc.).
        create_time: ISO-8601 creation timestamp.
        update_time: ISO-8601 last-updated timestamp.
        web_stream_data: Web-specific metadata; populated only for web streams.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    display_name: str
    type_: str = Field(alias="type")
    create_time: str | None = None
    update_time: str | None = None
    web_stream_data: WebStreamData | None = None

    def stream_id(self) -> str:
        """Return the numeric stream ID extracted from the resource name.

        Returns:
            The trailing segment of ``self.name`` (e.g. ``"456"``).
        """
        return self.name.split("/")[-1]
