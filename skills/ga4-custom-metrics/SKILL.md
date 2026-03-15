---
name: ga4-custom-metrics
version: 1.0.0
description: "List custom metrics registered on a GA4 property."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["gafour"]
    cliHelp: "gafour custom-metrics --help"
---

# ga4 custom-metrics

> **PREREQUISITE:** The `gafour` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/gafour#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/gafour#authentication) section. Run `gafour auth status` to verify.

```bash
gafour custom-metrics <command> <property-id> [flags]
```

## Commands

| Command | Description |
|---------|-------------|
| `custom-metrics list <property-id>` | List all custom metrics for a property. |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

## Response structure (JSON)

```json
[
  {
    "name": "properties/123456789/customMetrics/cm1",
    "parameter_name": "lifetime_value",
    "display_name": "Lifetime Value",
    "description": "Total revenue attributed to the user.",
    "scope": "USER",
    "measurement_unit": "CURRENCY",
    "restricted_metric_type": []
  }
]
```

`scope` values: `EVENT`, `USER`, `METRIC_SCOPE_UNSPECIFIED`.
`measurement_unit` values: `STANDARD`, `CURRENCY`, `FEET`, `METERS`, `KILOMETERS`, `MILES`, `MILLISECONDS`, `SECONDS`, `MINUTES`, `HOURS`.

## Examples

```bash
# List all custom metrics for a property
gafour custom-metrics list 123456789
```
