---
name: ga4-reports
version: 1.0.0
description: "Run GA4 Data API reports with dimensions, metrics, filters, and pagination. Always outputs JSON aligned with the RunReportResponse structure."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["ga4"]
    cliHelp: "ga4 reports --help"
---

# ga4 reports

> **PREREQUISITE:** The `ga4` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/ga4-cli#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/ga4-cli#authentication) section. Run `ga4 auth status` to verify.

```bash
ga4 reports run [flags]
```

## Commands

| Command | Description |
|---------|-------------|
| `reports run` | Run a historical Data API report. Always outputs JSON. |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--property-id`, `-p` | config / `GA4_PROPERTY_ID` env var | Numeric GA4 property ID. |
| `--metrics`, `-m` | *(required)* | Metric API names. Repeatable or comma-separated (e.g. `--metrics sessions,activeUsers`). |
| `--dimensions`, `-d` | *(none)* | Dimension API names. Repeatable or comma-separated. |
| `--start-date` | `28daysAgo` | Start date: `YYYY-MM-DD` or relative (e.g. `7daysAgo`). |
| `--end-date` | `today` | End date: `YYYY-MM-DD` or `today`. |
| `--filter` | *(none)* | Dimension filter expression string. |
| `--order-by` | *(none)* | Order-by expression: `name:asc` or `name:desc`. Repeatable. |
| `--limit` | `10000` | Maximum rows to return (1–250000). |
| `--offset` | `0` | Zero-based row offset for pagination. |
| `--output`, `-o` | *(stdout)* | Write output to a file path instead of stdout. |

## Response structure

Output always mirrors the [RunReportResponse](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/RunReportResponse) structure:

```json
{
  "dimension_headers": [{ "name": "date" }],
  "metric_headers":    [{ "name": "sessions", "type": "TYPE_INTEGER" }],
  "rows": [
    {
      "dimension_values": [{ "value": "20260101" }],
      "metric_values":    [{ "value": "1234" }]
    }
  ],
  "totals":    [],
  "maximums":  [],
  "minimums":  [],
  "row_count": 1,
  "kind":      ""
}
```

`dimension_headers[i]` names the dimension at `rows[n].dimension_values[i]`.
`metric_headers[j]` names the metric at `rows[n].metric_values[j]`.
`row_count` is the total matching rows — may exceed `len(rows)` when paginating.

## Examples

```bash
# Sessions and users over the last 28 days
ga4 reports run \
  --property-id 123456789 \
  --metrics sessions,activeUsers

# Daily sessions by country, last 7 days, top 50
ga4 reports run \
  --property-id 123456789 \
  --metrics sessions \
  --dimensions date,country \
  --start-date 7daysAgo \
  --order-by sessions:desc \
  --limit 50

# Paginate through a large result set
ga4 reports run \
  --property-id 123456789 \
  --metrics sessions \
  --dimensions date \
  --start-date 2026-01-01 \
  --limit 1000 \
  --offset 0

# Save output to file
ga4 reports run \
  --property-id 123456789 \
  --metrics sessions,activeUsers,engagementRate \
  --dimensions date,deviceCategory \
  --output report.json
```
