---
name: ga4-metadata
version: 1.0.0
description: "List available dimensions and metrics for a GA4 property, and check which combinations are compatible."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["ga4"]
    cliHelp: "ga4 metadata --help"
---

# ga4 metadata

> **PREREQUISITE:** The `ga4` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/ga4-cli#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/ga4-cli#authentication) section. Run `ga4 auth status` to verify.

```bash
ga4 metadata <command> [flags]
```

## Commands

| Command | Description |
|---------|-------------|
| `metadata dimensions` | List all dimensions available for a property. |
| `metadata metrics` | List all metrics available for a property. |
| `metadata compatibility` | Check which dimensions and metrics can be queried together. |

## Options

### `metadata dimensions` / `metadata metrics`

| Flag | Default | Description |
|------|---------|-------------|
| `--property-id`, `-p` | config / `GA4_PROPERTY_ID` env var | Numeric GA4 property ID. |
| `--search`, `-s` | *(none)* | Case-insensitive filter on API name, UI name, or description. |
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

### `metadata compatibility`

| Flag | Default | Description |
|------|---------|-------------|
| `--property-id`, `-p` | config / `GA4_PROPERTY_ID` env var | Numeric GA4 property ID. |
| `--dimensions`, `-d` | *(none)* | Dimension API names to check. Repeatable or comma-separated. |
| `--metrics`, `-m` | *(none)* | Metric API names to check. Repeatable or comma-separated. |
| `--filter` | `all` | Filter results: `compatible`, `incompatible`, or `all`. |
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

## Response structure

### `metadata dimensions` / `metadata metrics` (JSON)

```json
[
  {
    "api_name": "date",
    "ui_name": "Date",
    "description": "The date of the session formatted as YYYYMMDD.",
    "deprecated_api_names": [],
    "custom_definition": false,
    "category": "Time"
  }
]
```

### `metadata compatibility` (JSON)

```json
{
  "dimension_compatibilities": [
    {
      "dimension_metadata": {
        "api_name": "date",
        "ui_name": "Date",
        "description": "...",
        "deprecated_api_names": [],
        "custom_definition": false,
        "category": "Time"
      },
      "compatibility": "COMPATIBLE"
    }
  ],
  "metric_compatibilities": [
    {
      "metric_metadata": {
        "api_name": "sessions",
        "ui_name": "Sessions",
        "description": "...",
        "type_": "TYPE_INTEGER",
        "expression": null,
        "deprecated_api_names": [],
        "custom_definition": false,
        "category": "Session"
      },
      "compatibility": "COMPATIBLE"
    }
  ]
}
```

`compatibility` values: `COMPATIBLE`, `INCOMPATIBLE`, `COMPATIBILITY_UNSPECIFIED`.

## Examples

```bash
# List all dimensions for a property
ga4 metadata dimensions --property-id 123456789

# Search for device-related dimensions
ga4 metadata dimensions --property-id 123456789 --search device

# Find revenue metrics
ga4 metadata metrics --property-id 123456789 --search revenue

# Check if date + country + sessions + activeUsers can be queried together
ga4 metadata compatibility \
  --property-id 123456789 \
  --dimensions date,country \
  --metrics sessions,activeUsers

# Show only incompatible combinations
ga4 metadata compatibility \
  --property-id 123456789 \
  --dimensions date,country \
  --metrics sessions,activeUsers \
  --filter incompatible
```
