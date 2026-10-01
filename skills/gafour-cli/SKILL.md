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

The output shows the configured auth method, method-specific credential details, the default property, and whether the API is reachable.

- **valid** → proceed.
- **expired OAuth2 token** → the next command refreshes it automatically.
- **missing or invalid credentials** → run `gafour auth login --method <method>`.
- Supported methods: `oauth2`, `service-account`, and `token`.
- `oauth2` opens a browser; `service-account` and `token` prompt for credentials.
- Remove stored credentials with `gafour auth logout`.

## Configuration

```bash
gafour config init
gafour config show
gafour config set <key> <value>
gafour config unset <key>
```

Configuration is stored in `~/.config/gafour/config.json`. Valid keys are `auth_method`, `key_file`, `access_token`, `default_property_id`, and `output_format`.

`config show` can expose stored credential values. Do not include its unredacted output in responses, logs, or commits.

## Output flags

Admin read commands support `--format`/`-f` (`json`, `table`, or `csv`) and `--output`/`-o`. Historical and realtime reports always emit JSON and support `--output`/`-o`.

Use the documented read and report commands only. Resource mutation commands such as `create`, `update`, `delete`, and `clone` are not implemented yet.

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
| `--metrics`, `-m` | `activeUsers` | Metric API names. Repeat the flag for multiple metrics. |
| `--dimensions`, `-d` | *(none)* | Dimension API names. Repeat the flag for multiple dimensions. |
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
  --metrics activeUsers \
  --metrics eventCount \
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
