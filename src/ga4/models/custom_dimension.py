from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class DimensionScope(str, Enum):
    """The scope of a custom dimension."""

    DIMENSION_SCOPE_UNSPECIFIED = "DIMENSION_SCOPE_UNSPECIFIED"
    EVENT = "EVENT"
    USER = "USER"
    ITEM = "ITEM"


class CustomDimension(BaseModel):
    """Represents a GA4 custom dimension.

    Attributes:
        name: Full resource name, e.g. ``properties/123/customDimensions/456``.
        parameter_name: The event parameter name this dimension maps to.
        display_name: Human-readable dimension name.
        description: Optional description of what this dimension captures.
        scope: The scope at which this dimension is recorded.
        disallow_ads_personalization: Whether to exclude this dimension from ads personalization.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    parameter_name: str
    display_name: str
    description: str | None = None
    scope: DimensionScope
    disallow_ads_personalization: bool = False

    def dimension_id(self) -> str:
        """Return the numeric dimension ID extracted from the resource name.

        Returns:
            The trailing segment of ``self.name`` (e.g. ``"456"``).
        """
        return self.name.split("/")[-1]
