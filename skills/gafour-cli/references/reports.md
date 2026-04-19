# Reports

## Historical reports

```bash
gafour reports run [flags]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--property-id`, `-p` | config / `GA4_PROPERTY_ID` | Numeric GA4 property ID |
| `--metrics`, `-m` | *(required)* | Metric API names — repeatable or comma-separated |
| `--dimensions`, `-d` | *(none)* | Dimension API names — repeatable or comma-separated |
| `--start-date` | `28daysAgo` | `YYYY-MM-DD` or relative (`7daysAgo`) |
| `--end-date` | `today` | `YYYY-MM-DD` or `today` |
| `--filter` | *(none)* | Dimension filter DSL (see below) |
| `--metric-filter` | *(none)* | Metric filter DSL — same syntax |
| `--order-by` | *(none)* | `name:asc` or `name:desc` — repeatable |
| `--limit` | `10000` | Max rows (1–250000) |
| `--offset` | `0` | Row offset for pagination |
| `--output`, `-o` | stdout | Write output to a file path |

### Examples

```bash
# Sessions and users, last 28 days
gafour reports run --property-id 123456789 --metrics sessions,activeUsers

# Daily sessions by country, last 7 days, top 50
gafour reports run \
  --property-id 123456789 \
  --metrics sessions \
  --dimensions date,country \
  --start-date 7daysAgo \
  --order-by sessions:desc \
  --limit 50

# Paginate through large result sets
gafour reports run \
  --property-id 123456789 \
  --metrics sessions \
  --dimensions date \
  --start-date 2026-01-01 \
  --limit 1000 --offset 0

# Save to file
gafour reports run \
  --property-id 123456789 \
  --metrics sessions,activeUsers,engagementRate \
  --dimensions date,deviceCategory \
  --output report.json
```

### Response structure

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
  "row_count": 1
}
```

`dimension_headers[i]` names the dimension at `rows[n].dimension_values[i]`.
`metric_headers[j]` names the metric at `rows[n].metric_values[j]`.
`row_count` is the total matching rows — may exceed `len(rows)` when paginating.

---

## Realtime reports

```bash
gafour realtime run [flags]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--property-id`, `-p` | config / `GA4_PROPERTY_ID` | Numeric GA4 property ID |
| `--metrics`, `-m` | `activeUsers` | Metric API names |
| `--dimensions`, `-d` | *(none)* | Dimension API names |
| `--limit` | `10000` | Max rows |
| `--output`, `-o` | stdout | Write output to file |

### Response structure

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

### Examples

```bash
# Active users by country
gafour realtime run --property-id 123456789 --metrics activeUsers --dimensions country

# Active users and events by device
gafour realtime run \
  --property-id 123456789 \
  --metrics activeUsers,eventCount \
  --dimensions deviceCategory
```

---

## Batch reports

Run 1–5 independent reports in a single API call.

```bash
gafour reports batch --property-id <id> --requests-file <path> [--output <path>]
```

### Request file format

```json
[
  {
    "metrics": ["sessions"],
    "dimensions": ["date"],
    "date_ranges": [{"start_date": "7daysAgo", "end_date": "yesterday"}]
  },
  {
    "metrics": ["activeUsers"],
    "dimensions": ["country"],
    "date_ranges": [{"start_date": "30daysAgo", "end_date": "yesterday"}]
  }
]
```

Each object supports: `metrics`, `date_ranges`, `dimensions`, `dimension_filter`, `metric_filter`, `order_bys`, `limit`, `offset`.

### Response structure

```json
{
  "kind": "analyticsData#batchRunReports",
  "reports": [
    { /* RunReportResponse for request 0 */ },
    { /* RunReportResponse for request 1 */ }
  ]
}
```

`reports[i]` corresponds to request index `i`.

### Example: period-over-period comparison

```bash
cat > compare.json << 'EOF'
[
  {"metrics": ["sessions","activeUsers"], "date_ranges": [{"start_date": "30daysAgo", "end_date": "yesterday"}]},
  {"metrics": ["sessions","activeUsers"], "date_ranges": [{"start_date": "60daysAgo", "end_date": "31daysAgo"}]}
]
EOF
gafour reports batch --property-id 123456789 --requests-file compare.json
```

---

## Filter syntax

Both `--filter` (dimension) and `--metric-filter` use the same DSL.

### Operators

| Operator | Applies to | Meaning |
|----------|-----------|---------|
| `=` | strings / numbers | exact match / equal |
| `!=` | strings / numbers | not equal |
| `beginsWith` | strings | prefix match (case-insensitive) |
| `endsWith` | strings | suffix match (case-insensitive) |
| `contains` | strings | substring match (case-insensitive) |
| `matches` | strings | full regular expression |
| `<` `<=` `>` `>=` | numbers | numeric comparison |

### Connectives

`NOT` (highest) → `AND` → `OR` (lowest). Use `(...)` to override precedence.

### Examples

```bash
--filter 'country = "Spain"'
--filter 'country = "Spain" AND NOT deviceCategory = "tablet"'
--filter '(country = "Spain" OR country = "France") AND sessions > 100'
--filter 'pagePath beginsWith "/blog"'
--metric-filter 'sessions > 100'
```
