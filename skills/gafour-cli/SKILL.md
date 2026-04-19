---
name: gafour-cli
description: Inspects and queries Google Analytics 4 data using the gafour CLI. Covers accounts, properties, subproperties, data streams, audiences, key events, custom dimensions/metrics, event create rules, and historical/realtime reports. Use when the user asks about GA4 properties, subproperties, analytics data, web traffic metrics, conversion events, or needs to run GA4 reports.
allowed-tools: Bash(gafour:*)
---

# GA4 CLI (gafour)

## Auth check (always first)

```bash
gafour auth status
```

Expected output (oauth2, the default method):
```
Auth method:   oauth2
Account:       user@example.com
Token expiry:  2026-04-17 16:46 UTC
Default property: (not set)
✓ Credentials are valid and API is reachable.
```

- **valid** → proceed.
- **expired token** → token is refreshed automatically on the next command; no action needed.
- **missing credentials** → run `gafour auth login` to re-authenticate.
- **service-account** → shows `Key file: /path/to/key.json` instead of account/expiry.

## Global flags (all commands)

`--format`/`-f`: `json` (default), `table`, `csv` | `--output`/`-o`: write to file path

---

## Accounts

```bash
gafour accounts list
gafour accounts get <account-id>
```

The numeric account ID is the trailing segment of `name` (e.g. `"accounts/123456"` → `123456`).

```bash
gafour accounts list
gafour accounts get 123456
```

---

## Properties

```bash
gafour properties list --account-id <account-id>
gafour properties list-subproperties --property-id <property-id>
gafour properties get <property-id>
```

- `list` requires `--account-id`/`-a` — lists ordinary properties under an account.
- `list-subproperties` requires `--property-id`/`-p` — lists GA4 subproperties whose parent is the given property.

The numeric property ID is the trailing segment of `name` (e.g. `"properties/123456789"` → `123456789`). Use this ID as `--property-id` in all report and metadata commands.

### Response structure (JSON)

```json
[
  {
    "name": "properties/123456789",
    "display_name": "My Website",
    "time_zone": "America/New_York",
    "currency_code": "USD",
    "industry_category": "INDUSTRY_CATEGORY_TECHNOLOGY",
    "create_time": "2021-03-10 12:00:00+00:00",
    "update_time": "2024-05-20 09:00:00+00:00",
    "parent": "accounts/123456"
  }
]
```

```bash
gafour properties list --account-id 123456
gafour properties list-subproperties --property-id 123456789
gafour properties get 123456789
```

---

## Data streams

```bash
gafour datastreams list <property-id>
gafour datastreams get <property-id> <stream-id>
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

### Response structure (JSON)

```json
[
  {
    "name": "properties/123456789/dataStreams/9876543",
    "display_name": "My Website Stream",
    "type_": "WEB_DATA_STREAM",
    "create_time": "2021-03-10 12:00:00+00:00",
    "update_time": "2024-05-20 09:00:00+00:00",
    "web_stream_data": {
      "default_uri": "https://www.example.com",
      "measurement_id": "G-XXXXXXXXXX"
    }
  }
]
```

`web_stream_data.measurement_id` contains the `G-XXXXXXXXXX` tag. The numeric stream ID is the trailing segment of `name` and is required for `events list`.

### Examples

```bash
gafour datastreams list 123456789
gafour datastreams get 123456789 9876543
```

---

## Audiences

```bash
gafour audiences list <property-id>
gafour audiences get <property-id> <audience-id>
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

### Response structure (JSON)

```json
[
  {
    "name": "properties/123456789/audiences/987654",
    "display_name": "High-Value Users",
    "description": "Users with lifetime revenue > $100.",
    "membership_duration_days": 30,
    "ads_personalization_enabled": true,
    "create_time": "2023-04-01 08:00:00+00:00"
  }
]
```

The numeric audience ID is the trailing segment of `name`.

### Examples

```bash
gafour audiences list 123456789
gafour audiences get 123456789 987654
```

---

## Key events (conversions)

```bash
gafour key-events list <property-id>
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

### Response structure (JSON)

```json
[
  {
    "name": "properties/123456789/keyEvents/abc123",
    "event_name": "purchase",
    "create_time": "2022-06-01 10:00:00+00:00",
    "deletable": true,
    "custom": false,
    "counting_method": "ONCE_PER_EVENT"
  }
]
```

`counting_method` values: `ONCE_PER_EVENT`, `ONCE_PER_SESSION`, `COUNTING_METHOD_UNSPECIFIED`.

### Examples

```bash
gafour key-events list 123456789
gafour key-events list 123456789 --format table
```

---

## Custom dimensions

```bash
gafour custom-dimensions list <property-id>
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

### Response structure (JSON)

```json
[
  {
    "name": "properties/123456789/customDimensions/cd1",
    "parameter_name": "plan_type",
    "display_name": "Plan Type",
    "description": "The user's subscription plan.",
    "scope": "USER",
    "disallow_ads_personalization": false
  }
]
```

`scope` values: `EVENT`, `USER`, `DIMENSION_SCOPE_UNSPECIFIED`.

### Examples

```bash
gafour custom-dimensions list 123456789
```

---

## Custom metrics

```bash
gafour custom-metrics list <property-id>
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

### Response structure (JSON)

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

### Examples

```bash
gafour custom-metrics list 123456789
```

---

## Event create rules

```bash
gafour events list <property-id> <stream-id>
```

Use `gafour datastreams list <property-id>` first to discover available stream IDs.

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

### Response structure (JSON)

```json
[
  {
    "name": "properties/123456789/dataStreams/9876543/eventCreateRules/rule1",
    "destination_event": "purchase_completed",
    "event_conditions": [
      { "field": "event_name", "comparisonType": "EQUALS", "value": "checkout" }
    ],
    "source_copy_parameters": true
  }
]
```

### Examples

```bash
gafour events list 123456789 9876543
```

---

## Realtime reports

```bash
gafour realtime run [flags]
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--property-id`, `-p` | config / `GA4_PROPERTY_ID` env var | Numeric GA4 property ID. |
| `--metrics`, `-m` | `activeUsers` | Metric API names. Repeatable or comma-separated. |
| `--dimensions`, `-d` | *(none)* | Dimension API names. Repeatable or comma-separated. |
| `--limit` | `10000` | Maximum rows to return. |
| `--output`, `-o` | *(stdout)* | Write output to a file path instead of stdout. |

### Response structure (JSON)

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
# Current active users (default)
gafour realtime run --property-id 123456789

# Active users by country
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

---

## Typical discovery workflow

```bash
# 1. Find the account
gafour accounts list

# 2. Find the property (ordinary properties)
gafour properties list --account-id 123456

# 3. Find subproperties (GA4 subproperties under a rollup/parent)
gafour properties list-subproperties --property-id 123456789

# 4. Inspect the property
gafour datastreams list 123456789
gafour key-events list 123456789
gafour audiences list 123456789

# 5. Run a report
gafour reports run --property-id 123456789 --metrics sessions --dimensions date

# 6. Check live users
gafour realtime run --property-id 123456789
```

---

## Specific tasks

- **Reports (historical, batch, filters, pagination)** — [references/reports.md](references/reports.md)
- **Metadata (dimensions, metrics, compatibility)** — [references/metadata.md](references/metadata.md)
