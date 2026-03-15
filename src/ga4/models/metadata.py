from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class CompatibilityStatus(str, Enum):
    """Compatibility status for a dimension or metric in the context of a report."""

    COMPATIBLE = "COMPATIBLE"
    INCOMPATIBLE = "INCOMPATIBLE"
    COMPATIBILITY_UNSPECIFIED = "COMPATIBILITY_UNSPECIFIED"


class DimensionMetadata(BaseModel):
    """Metadata for a single GA4 dimension.

    Attributes:
        api_name: The dimension name used in API requests.
        ui_name: Human-readable name shown in the UI.
        description: Description of what the dimension measures.
        deprecated_api_names: Legacy API names still accepted by the API.
        custom_definition: Whether this is a custom dimension.
        category: Category grouping for the dimension.
    """

    model_config = ConfigDict(populate_by_name=True)

    api_name: str
    ui_name: str
    description: str
    deprecated_api_names: list[str] = []
    custom_definition: bool = False
    category: str | None = None


class MetricMetadata(BaseModel):
    """Metadata for a single GA4 metric.

    Attributes:
        api_name: The metric name used in API requests.
        ui_name: Human-readable name shown in the UI.
        description: Description of what the metric measures.
        type_: Data type of the metric values.
        expression: Formula expression for derived metrics.
        deprecated_api_names: Legacy API names still accepted by the API.
        custom_definition: Whether this is a custom metric.
        category: Category grouping for the metric.
    """

    model_config = ConfigDict(populate_by_name=True)

    api_name: str
    ui_name: str
    description: str
    type_: str | None = None
    expression: str | None = None
    deprecated_api_names: list[str] = []
    custom_definition: bool = False
    category: str | None = None


class DimensionCompatibility(BaseModel):
    """Compatibility result for a single dimension.

    Attributes:
        dimension_metadata: The dimension's metadata.
        compatibility: Whether this dimension is compatible with the current report context.
    """

    model_config = ConfigDict(populate_by_name=True)

    dimension_metadata: DimensionMetadata
    compatibility: CompatibilityStatus


class MetricCompatibility(BaseModel):
    """Compatibility result for a single metric.

    Attributes:
        metric_metadata: The metric's metadata.
        compatibility: Whether this metric is compatible with the current report context.
    """

    model_config = ConfigDict(populate_by_name=True)

    metric_metadata: MetricMetadata
    compatibility: CompatibilityStatus


class CompatibilityResponse(BaseModel):
    """Full response from a compatibility check.

    Attributes:
        dimension_compatibilities: Compatibility results for all dimensions.
        metric_compatibilities: Compatibility results for all metrics.
    """

    model_config = ConfigDict(populate_by_name=True)

    dimension_compatibilities: list[DimensionCompatibility] = []
    metric_compatibilities: list[MetricCompatibility] = []
