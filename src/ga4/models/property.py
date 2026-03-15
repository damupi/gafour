from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Property(BaseModel):
    """Represents a Google Analytics 4 property.

    Attributes:
        name: Full resource name, e.g. ``properties/123``.
        display_name: Human-readable property name.
        time_zone: IANA time zone identifier.
        currency_code: ISO 4217 currency code.
        industry_category: Vertical category for this property.
        create_time: ISO-8601 creation timestamp.
        update_time: ISO-8601 last-updated timestamp.
        parent: Parent resource name, e.g. ``accounts/123``.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    display_name: str
    time_zone: str
    currency_code: str
    industry_category: str | None = None
    create_time: str | None = None
    update_time: str | None = None
    parent: str | None = None

    def property_id(self) -> str:
        """Return the numeric property ID extracted from the resource name.

        Returns:
            The trailing segment of ``self.name`` (e.g. ``"123"``).
        """
        return self.name.split("/")[-1]
