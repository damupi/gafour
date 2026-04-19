# Metadata — Dimensions, Metrics & Compatibility

Use `metadata` commands to discover valid dimension/metric API names and check whether combinations can be queried together before building a report.

## List dimensions

```bash
gafour metadata dimensions --property-id 123456789
gafour metadata dimensions --property-id 123456789 --search device
gafour metadata dimensions --property-id 123456789 --search campaign
```

## List metrics

```bash
gafour metadata metrics --property-id 123456789
gafour metadata metrics --property-id 123456789 --search revenue
gafour metadata metrics --property-id 123456789 --search session
```

## Options (`dimensions` / `metrics`)

| Flag | Default | Description |
|------|---------|-------------|
| `--property-id`, `-p` | config / `GA4_PROPERTY_ID` | Numeric GA4 property ID |
| `--search`, `-s` | *(none)* | Case-insensitive filter on API name, UI name, or description |
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv` |
| `--output`, `-o` | stdout | Write to file |

### Response structure

```json
[
  {
    "api_name": "date",
    "ui_name": "Date",
    "description": "The date of the session formatted as YYYYMMDD.",
    "custom_definition": false,
    "category": "Time"
  }
]
```

Use `api_name` values directly in `--dimensions` and `--metrics` flags.

---

## Check compatibility

Verify that a set of dimensions and metrics can be queried together before running a report.

```bash
gafour metadata compatibility \
  --property-id 123456789 \
  --dimensions date,country \
  --metrics sessions,activeUsers
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--property-id`, `-p` | config / `GA4_PROPERTY_ID` | Numeric GA4 property ID |
| `--dimensions`, `-d` | *(none)* | Dimension API names — repeatable or comma-separated |
| `--metrics`, `-m` | *(none)* | Metric API names — repeatable or comma-separated |
| `--filter` | `all` | Filter results: `compatible`, `incompatible`, or `all` |
| `--format`, `-f` | `json` | Output format |
| `--output`, `-o` | stdout | Write to file |

### Examples

```bash
# Check full combination
gafour metadata compatibility \
  --property-id 123456789 \
  --dimensions date,country \
  --metrics sessions,activeUsers

# Show only what's incompatible (useful for debugging failed reports)
gafour metadata compatibility \
  --property-id 123456789 \
  --dimensions date,country \
  --metrics sessions,activeUsers \
  --filter incompatible
```

### Response structure

```json
{
  "dimension_compatibilities": [
    {
      "dimension_metadata": { "api_name": "date", "ui_name": "Date", ... },
      "compatibility": "COMPATIBLE"
    }
  ],
  "metric_compatibilities": [
    {
      "metric_metadata": { "api_name": "sessions", "ui_name": "Sessions", ... },
      "compatibility": "COMPATIBLE"
    }
  ]
}
```

`compatibility` values: `COMPATIBLE`, `INCOMPATIBLE`, `COMPATIBILITY_UNSPECIFIED`.
