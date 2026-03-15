---
name: ga4-realtime
version: 1.0.0
description: "Run GA4 realtime reports to get live user and event data. Always outputs JSON."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["ga4x"]
    cliHelp: "ga4x realtime --help"
---

# ga4 realtime

> **PREREQUISITE:** The `ga4x` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/ga4x#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/ga4x#authentication) section. Run `ga4x auth status` to verify.

```bash
ga4x realtime run [flags]
```

## Commands

| Command | Description |
|---------|-------------|
| `realtime run` | Run a realtime report showing current active users and events. Always outputs JSON. |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--property-id`, `-p` | config / `GA4_PROPERTY_ID` env var | Numeric GA4 property ID. |
| `--metrics`, `-m` | `activeUsers` | Metric API names. Repeatable or comma-separated. |
| `--dimensions`, `-d` | *(none)* | Dimension API names. Repeatable or comma-separated. |
| `--limit` | `10000` | Maximum rows to return. |
| `--output`, `-o` | *(stdout)* | Write output to a file path instead of stdout. |

## Response structure

Output mirrors the [RunRealtimeReportResponse](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/RunRealtimeReportResponse) structure:

```json
{
  "dimension_headers": [{ "name": "country" }],
  "metric_headers":    [{ "name": "activeUsers", "type": "TYPE_INTEGER" }],
  "rows": [
    {
      "dimension_values": [{ "value": "United States" }],
      "metric_values":    [{ "value": "42" }]
    }
  ],
  "totals":    [],
  "maximums":  [],
  "minimums":  [],
  "row_count": 1,
  "kind":      ""
}
```

## Examples

```bash
# Current active users (default)
ga4x realtime run --property-id 123456789

# Active users broken down by country
ga4x realtime run \
  --property-id 123456789 \
  --metrics activeUsers \
  --dimensions country

# Active users and events by device category
ga4x realtime run \
  --property-id 123456789 \
  --metrics activeUsers,eventCount \
  --dimensions deviceCategory
```
