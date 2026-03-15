---
name: ga4-custom-metrics
version: 1.0.0
description: "List custom metrics registered on a GA4 property."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["ga4x"]
    cliHelp: "ga4x custom-metrics --help"
---

# ga4 custom-metrics

> **PREREQUISITE:** The `ga4x` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/ga4x#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/ga4x#authentication) section. Run `ga4x auth status` to verify.

```bash
ga4x custom-metrics <command> <property-id> [flags]
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
ga4x custom-metrics list 123456789
```
