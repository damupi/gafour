---
name: ga4-custom-metrics
version: 1.0.0
description: "List custom metrics registered on a GA4 property."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["ga4"]
    cliHelp: "ga4 custom-metrics --help"
---

# ga4 custom-metrics

> **PREREQUISITE:** The `ga4` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/ga4-cli#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/ga4-cli#authentication) section. Run `ga4 auth status` to verify.

```bash
ga4 custom-metrics <command> <property-id> [flags]
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
ga4 custom-metrics list 123456789
```
