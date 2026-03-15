# Product Requirements Document — ga4 CLI

## Overview

`ga4` is a Python CLI tool for Google Analytics 4 that combines admin operations, reporting, metadata discovery, and compatibility checking into a single, well-designed command-line interface. It improves on existing tools (`sulimanbenhalim/ga-cli`, `FunnelEnvy/ga4-cli`) by being the only tool that covers the full GA4 surface area with advanced filtering, metadata search, compatibility checking, and safety features like dry-run mode.

**Invocation:** `ga4 <command-group> <command> [options]`
**Distribution:** PyPI (`pip install ga4-cli` / `uv add ga4-cli`)
**Target users:** Analytics engineers, developers, and data teams who work with GA4 programmatically.

---

## Goals

1. Replace the need for multiple GA4 CLI tools with one complete solution.
2. Be the reference implementation for GA4 CLI tooling in the Python ecosystem.
3. Work well in both interactive use and automation/CI pipelines.

## Non-Goals

- No GUI, TUI, or web interface.
- No MCP server layer (the CLI is the product).
- No real-time streaming or websocket-based live dashboards.
- No BigQuery export management (out of scope for v1).

---

## Authentication

Three methods, selectable at runtime or via config:

| Method | Flag | Use case |
|---|---|---|
| OAuth2 (browser) | `--auth oauth2` | Interactive, personal accounts |
| Service Account | `--auth service-account --key path/to/key.json` | CI/CD, automation |
| Access Token | `--auth token --token $TOKEN` | Scripts, pre-authenticated environments |

**Config precedence (highest to lowest):**
1. CLI flags
2. Environment variables: `GA4_AUTH_METHOD`, `GA4_KEY_FILE`, `GA4_ACCESS_TOKEN`, `GOOGLE_APPLICATION_CREDENTIALS`
3. Config file: `~/.config/ga4/config.toml`

---

## Command Reference

### `ga4 auth`
```
ga4 auth login [--method oauth2|service-account|token]
ga4 auth status
ga4 auth logout
```

### `ga4 accounts`
```
ga4 accounts list
ga4 accounts get <account-id>
```

### `ga4 properties`
```
ga4 properties list --account-id <id>
ga4 properties get <property-id>
ga4 properties create --account-id <id> --name <name> --timezone <tz> --currency <cur>
ga4 properties update <property-id> [--name] [--timezone] [--currency]
ga4 properties delete <property-id> [--dry-run]
ga4 properties clone <property-id> --name <name> [--account-id <id>] [--dry-run]
```

### `ga4 datastreams`
```
ga4 datastreams list <property-id>
ga4 datastreams get <property-id> <stream-id>
ga4 datastreams create <property-id> --name <name> --url <url> [--dry-run]
ga4 datastreams delete <property-id> <stream-id> [--dry-run]
```

### `ga4 reports`
```
ga4 reports run \
  --property-id <id> \
  --metrics <m1,m2,...> \
  --start-date <YYYY-MM-DD> \
  --end-date <YYYY-MM-DD> \
  [--dimensions <d1,d2,...>] \
  [--filter <expression>] \
  [--order-by <metric:asc|desc>] \
  [--limit <n>] \
  [--offset <n>]
```

### `ga4 realtime`
```
ga4 realtime run --property-id <id> \
  [--metrics <m1,m2,...>] \
  [--dimensions <d1,d2,...>] \
  [--filter <expression>]
```

### `ga4 metadata`
```
ga4 metadata dimensions --property-id <id> [--search <term>]
ga4 metadata metrics --property-id <id> [--search <term>]
ga4 metadata describe <dimension|metric> <name> --property-id <id>
ga4 metadata compatibility \
  --property-id <id> \
  --dimensions <d1,d2,...> \
  --metrics <m1,m2,...> \
  [--filter compatible|incompatible]
```

`compatibility` calls the GA4 Data API's `properties.checkCompatibility` endpoint. It returns each requested dimension and metric tagged as `COMPATIBLE`, `INCOMPATIBLE`, or `COMPATIBILITY_UNSPECIFIED`, with API name, UI name, and description. The `--filter` flag narrows output to only compatible or only incompatible items.

### `ga4 key-events`

Lists Key Events (formerly Conversions) configured on a property. Read-only in v1.

```
ga4 key-events list <property-id>
```

Response fields per key event: `name`, `eventName`, `createTime`, `deletable`, `custom`, `countingMethod`.

### `ga4 custom-dimensions`

Lists custom dimensions registered on a property (Admin API, read-only in v1).

```
ga4 custom-dimensions list <property-id>
```

Response fields: `name`, `parameterName`, `displayName`, `description`, `scope` (`EVENT` | `USER`), `disallowAdsPersonalization`.

### `ga4 custom-metrics`

Lists custom metrics registered on a property (Admin API, read-only in v1).

```
ga4 custom-metrics list <property-id>
```

Response fields: `name`, `parameterName`, `displayName`, `description`, `scope`, `measurementUnit`, `restrictedMetricType`.

### `ga4 audiences`
```
ga4 audiences list <property-id>
ga4 audiences get <property-id> <audience-id>
ga4 audiences create <property-id> --name <name> --definition <json-file> [--dry-run]
ga4 audiences delete <property-id> <audience-id> [--dry-run]
```

### `ga4 events`
```
ga4 events list <property-id>
ga4 events get <property-id> <event-name>
ga4 events create <property-id> --name <name> --source-event <name> [--dry-run]
```

### `ga4 user-properties`
```
ga4 user-properties list <property-id>
ga4 user-properties get <property-id> <property-name>
```

### `ga4 config`
```
ga4 config init
ga4 config show
ga4 config set <key> <value>
ga4 config unset <key>
```

---

## Global Flags

| Flag | Description |
|---|---|
| `--format table\|json\|csv` | Output format (default: `table`) |
| `--output <file>` | Write output to file instead of stdout |
| `--property-id <id>` | Default property (can be set in config) |
| `--quiet` | Suppress all non-data output (for scripting) |
| `--dry-run` | Preview write operations without executing |
| `--no-header` | Omit header row (CSV/table only) |
| `--page-all` | Auto-paginate and stream all results as NDJSON |
| `--page-limit <n>` | Max pages to fetch when paginating (default: 10) |
| `--page-delay <ms>` | Delay between pagination requests in ms (default: 0) |
| `--version` | Print version and exit |

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | GA4 API error (4xx / 5xx from Google) |
| `2` | Authentication error |
| `3` | Invalid arguments or validation error |
| `4` | Configuration error (missing config, bad config file) |
| `5` | Network / connection error |

---

## Output Formats

- **table** (default): Rich-formatted, colored, human-readable. Used for interactive sessions.
- **json**: Structured, pipe-friendly. Preserves all API response fields.
- **csv**: Flat, Excel-compatible. Useful for reporting pipelines and data exports.

All write operations (`create`, `update`, `delete`, `clone`) print a confirmation summary. With `--quiet`, only the resulting resource ID is printed (or nothing on delete).

---

## Error Handling UX

Errors follow a three-line pattern:
```
Error: <what went wrong>
→ <why it happened>
→ <how to fix it>
```

Example:
```
Error: Property not found
→ Property ID 12345 does not exist or is not accessible with current credentials
→ Run `ga4 properties list --account-id <id>` to see available properties
```

---

## Dry-run Mode

All mutating commands support `--dry-run`. When passed:
- No API write call is made.
- Output shows exactly what would be sent to the API (formatted as JSON).
- Exit code is `0`.

---

## Batch Operations

`properties create`, `datastreams create`, and `audiences create` accept a `--batch <csv-file>` flag. The CSV columns map to the command's flags. Each row is executed sequentially. A summary table is printed at the end showing success/failure per row.

---

## Technical Design

### Package Layout (`src/` layout)

```
ga4-cli/
├── src/
│   └── ga4/
│       ├── __init__.py
│       ├── cli.py              # typer app, registers command groups
│       ├── auth.py             # credential resolution and client factory
│       ├── config.py           # ~/.config/ga4/config.toml read/write
│       ├── output.py           # table/json/csv rendering via rich
│       ├── commands/
│       │   ├── accounts.py
│       │   ├── properties.py
│       │   ├── datastreams.py
│       │   ├── reports.py
│       │   ├── realtime.py
│       │   ├── metadata.py
│       │   ├── audiences.py
│       │   ├── events.py
│       │   └── user_properties.py
│       └── models/
│           ├── account.py
│           ├── property.py
│           ├── datastream.py
│           ├── report.py
│           ├── metadata.py
│           ├── audience.py
│           └── event.py
├── tests/
│   ├── test_accounts.py
│   ├── test_properties.py
│   ├── test_reports.py
│   ├── test_metadata.py
│   └── ...
├── pyproject.toml
└── uv.lock
```

### Key dependencies

| Package | Purpose |
|---|---|
| `typer` | CLI framework |
| `rich` | Table/color output |
| `pydantic` | All request/response models |
| `google-analytics-data` | GA4 Data API (reports, realtime, metadata) |
| `google-analytics-admin` | GA4 Admin API (accounts, properties, streams) |
| `google-auth` | Auth primitives |
| `google-auth-oauthlib` | OAuth2 browser flow |

Dev: `pytest`, `pytest-cov`, `ruff`, `mypy`
Package manager: `uv`

### Development approach

- **TDD**: every command has a test written before implementation.
- **Pydantic models** for all request inputs and API response shapes. Commands call `model.model_validate(api_response)` before rendering.
- No global state — credentials and config are passed explicitly through a shared `Context` object injected via typer's `typer.Context`.

---

## Phases

### Phase 1 — Admin parity (MVP)
- `auth`, `accounts`, `properties`, `datastreams`, `config`
- `table` and `json` output
- Service account auth

### Phase 2 — Reporting and metadata
- `reports run`, `realtime run`
- `metadata dimensions`, `metadata metrics`, `metadata compatibility`
- OAuth2 and token auth
- `csv` output, `--output` flag

### Phase 3 — Advanced resources
- `audiences`, `events`, `user-properties`
- `--dry-run`, `--batch`
- `properties clone`
- Shell completion (bash, zsh, fish)

### Phase 4 — Polish and publish
- Comprehensive error messages with remediation hints
- Progress indicators for long-running operations
- PyPI release
- Public GitHub repo with CI (ruff, mypy, pytest)
- `CHANGELOG.md` and versioned releases

---

## Success Metrics

- Covers 100% of GA4 Admin API resource types.
- `ga4 metadata compatibility` correctly identifies incompatible dimension/metric pairs.
- All commands have `--dry-run` support where applicable.
- `>= 90%` test coverage.
- Zero runtime imports of optional dependencies when not needed.
