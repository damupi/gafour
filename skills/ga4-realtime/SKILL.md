---
name: ga4-realtime
version: 1.0.0
description: "Run GA4 realtime reports to get live user and event data. Always outputs JSON."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["gafour"]
    cliHelp: "gafour realtime --help"
---

# ga4 realtime

> **PREREQUISITE:** The `gafour` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/gafour#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/gafour#authentication) section. Run `gafour auth status` to verify.

```bash
gafour realtime run [flags]
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
gafour realtime run --property-id 123456789

# Active users broken down by country
gafour realtime run \
  --property-id 123456789 \
  --metrics activeUsers \
  --dimensions country

# Active users and events by device category
gafour realtime run \
  --property-id 123456789 \
  --metrics activeUsers,eventCount \
  --dimensions deviceCategory
```
