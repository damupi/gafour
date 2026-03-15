from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Audience(BaseModel):
    """Represents a GA4 audience.

    Attributes:
        name: Full resource name, e.g. ``properties/123/audiences/456``.
        display_name: Human-readable audience name.
        description: Optional audience description.
        membership_duration_days: How long users remain in this audience (days).
        ads_personalization_enabled: Whether ads personalization is enabled.
        create_time: ISO-8601 creation timestamp.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    display_name: str
    description: str | None = None
    membership_duration_days: int | None = None
    ads_personalization_enabled: bool | None = None
    create_time: str | None = None

    def audience_id(self) -> str:
        """Return the numeric audience ID extracted from the resource name.

        Returns:
            The trailing segment of ``self.name`` (e.g. ``"456"``).
        """
        return self.name.split("/")[-1]
