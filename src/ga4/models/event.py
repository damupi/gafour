from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class EventCreateRule(BaseModel):
    """Represents a GA4 event create rule on a data stream.

    Attributes:
        name: Full resource name,
            e.g. ``properties/123/dataStreams/456/eventCreateRules/789``.
        destination_event: The name of the new event created by this rule.
        event_conditions: List of conditions that trigger event creation.
        source_copy_parameters: Whether to copy parameters from the source event.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    destination_event: str
    event_conditions: list[dict[str, Any]] = []
    source_copy_parameters: bool = False

    def rule_id(self) -> str:
        """Return the numeric rule ID extracted from the resource name.

        Returns:
            The trailing segment of ``self.name`` (e.g. ``"789"``).
        """
        return self.name.split("/")[-1]
