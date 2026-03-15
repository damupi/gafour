from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class CountingMethod(str, Enum):
    """How key event conversions are counted per session."""

    COUNTING_METHOD_UNSPECIFIED = "COUNTING_METHOD_UNSPECIFIED"
    ONCE_PER_EVENT = "ONCE_PER_EVENT"
    ONCE_PER_SESSION = "ONCE_PER_SESSION"


class KeyEvent(BaseModel):
    """Represents a GA4 key event (formerly conversion event).

    Attributes:
        name: Full resource name, e.g. ``properties/123/keyEvents/456``.
        event_name: The GA4 event name this key event tracks.
        create_time: ISO-8601 creation timestamp.
        deletable: Whether this key event can be deleted via the API.
        custom: Whether this is a custom (user-defined) key event.
        counting_method: How conversions are counted within a session.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    event_name: str
    create_time: str | None = None
    deletable: bool = False
    custom: bool = False
    counting_method: CountingMethod = CountingMethod.COUNTING_METHOD_UNSPECIFIED

    def key_event_id(self) -> str:
        """Return the numeric key event ID extracted from the resource name.

        Returns:
            The trailing segment of ``self.name`` (e.g. ``"456"``).
        """
        return self.name.split("/")[-1]
