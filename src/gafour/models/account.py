from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Account(BaseModel):
    """Represents a Google Analytics 4 account.

    Attributes:
        name: Full resource name, e.g. ``accounts/123``.
        display_name: Human-readable account name.
        region_code: CLDR region code for the account's country.
        create_time: ISO-8601 creation timestamp.
        update_time: ISO-8601 last-updated timestamp.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    display_name: str
    region_code: str | None = None
    create_time: str | None = None
    update_time: str | None = None

    def account_id(self) -> str:
        """Return the numeric account ID extracted from the resource name.

        Returns:
            The trailing segment of ``self.name`` (e.g. ``"123"``).
        """
        return self.name.split("/")[-1]
