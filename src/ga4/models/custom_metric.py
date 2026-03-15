from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class MetricScope(str, Enum):
    """The scope of a custom metric."""

    METRIC_SCOPE_UNSPECIFIED = "METRIC_SCOPE_UNSPECIFIED"
    EVENT = "EVENT"


class MeasurementUnit(str, Enum):
    """The unit of measurement for a custom metric."""

    MEASUREMENT_UNIT_UNSPECIFIED = "MEASUREMENT_UNIT_UNSPECIFIED"
    STANDARD = "STANDARD"
    CURRENCY = "CURRENCY"
    FEET = "FEET"
    METERS = "METERS"
    KILOMETERS = "KILOMETERS"
    MILES = "MILES"
    MILLISECONDS = "MILLISECONDS"
    SECONDS = "SECONDS"
    MINUTES = "MINUTES"
    HOURS = "HOURS"


class CustomMetric(BaseModel):
    """Represents a GA4 custom metric.

    Attributes:
        name: Full resource name, e.g. ``properties/123/customMetrics/456``.
        parameter_name: The event parameter name this metric maps to.
        display_name: Human-readable metric name.
        description: Optional description of what this metric measures.
        scope: The scope at which this metric is recorded.
        measurement_unit: The unit of measurement.
        restricted_metric_type: Restricted metric type identifiers.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    parameter_name: str
    display_name: str
    description: str | None = None
    scope: MetricScope
    measurement_unit: MeasurementUnit
    restricted_metric_type: list[str] = []

    def metric_id(self) -> str:
        """Return the numeric metric ID extracted from the resource name.

        Returns:
            The trailing segment of ``self.name`` (e.g. ``"456"``).
        """
        return self.name.split("/")[-1]
