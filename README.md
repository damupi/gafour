# gafour

A comprehensive command-line interface for Google Analytics 4 — run reports, inspect metadata, check dimension/metric compatibility, manage properties, and more.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Configuration](#configuration)
- [Commands](#commands)
- [Output Formats](#output-formats)
- [Environment Variables](#environment-variables)

---

## Prerequisites

- **Python 3.11+**
- A **Google Cloud project** with the following APIs enabled:
  - [Google Analytics Data API](https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com)
  - [Google Analytics Admin API](https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com)
- A **Service Account** (recommended) or an **access token** with access to your GA4 properties

---

## Installation

### From PyPI (recommended)

```bash
pip install gafour
```

Or with `uv`:

```bash
uv tool install gafour
```

### From source

```bash
git clone https://github.com/damupi/gafour.git
cd gafour
pip install -e .
```

Or with `uv`:

```bash
git clone https://github.com/damupi/gafour.git
cd gafour
uv sync
uv run gafour --help
```

> **Note:** When installed from source with `uv sync`, prefix all commands with `uv run` (e.g. `uv run gafour accounts list`) or activate the virtual environment first with `source .venv/bin/activate`.

Verify the installation:

```bash
gafour --version
```

---

## Quick Start

```bash
# 1. Run the setup wizard
gafour config init

# 2. Verify authentication
gafour auth status

# 3. List your accounts
gafour accounts list

# 4. List properties for an account
gafour properties list --account-id 123456

# 5. Run a report
gafour reports run \
  --property-id 123456789 \
  --metrics activeUsers,sessions \
  --start-date 2026-01-01 \
  --end-date 2026-03-14 \
  --dimensions date,country
```

---

## Authentication

`gafour` supports two authentication methods.

### Option A — Service Account (recommended for scripts and CI)

1. Go to [Google Cloud Console → IAM & Admin → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Create a service account and download the JSON key file
3. Grant the service account **Viewer** access in GA4 → Admin → Account / Property Access Management
4. Configure the CLI:

```bash
gafour config set auth_method service-account
gafour config set key_file /path/to/key.json
```

Or set the standard Application Default Credentials environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### Option B — Access Token

Use a short-lived OAuth2 access token (useful in automated environments where a token is already available):

```bash
gafour config set auth_method token
gafour config set access_token YOUR_ACCESS_TOKEN
```

Or via environment variable:

```bash
export GA4_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
```

### Verify

```bash
gafour auth status
```

---

## Configuration

Run the interactive wizard to set up everything at once:

```bash
gafour config init
```

Or set individual values:

```bash
gafour config set auth_method service-account
gafour config set key_file /path/to/key.json
gafour config set default_property_id 123456789   # skip --property-id on every command
gafour config set output_format table              # table | json | csv
```

View current config:

```bash
gafour config show
```

Clear a value back to its default:

```bash
gafour config unset default_property_id
```

Config is stored at `~/.config/ga4/config.json`.

---

## Commands

### Accounts

```bash
gafour accounts list                        # list all accessible accounts
gafour accounts get <account-id>            # get account details
```

### Properties

```bash
gafour properties list --account-id <id>   # list properties for an account
gafour properties get <property-id>        # get property details
```

### Data Streams

```bash
gafour datastreams list <property-id>               # list data streams
gafour datastreams get <property-id> <stream-id>    # get stream details (includes measurement ID)
```

### Reports

```bash
gafour reports run \
  --property-id 123456789 \
  --metrics activeUsers,sessions,engagementRate \
  --start-date 2026-01-01 \
  --end-date 2026-03-14 \
  --dimensions date,country,deviceCategory \
  --order-by sessions:desc \
  --limit 100 \
  --filter 'country = "Spain" AND NOT deviceCategory = "tablet"' \
  --output report.json
```

#### Filter DSL

`--filter` and `--metric-filter` accept a DSL expression:

| Operator | Applies to | Example |
|----------|-----------|---------|
| `=` | string / number | `country = "Spain"` |
| `!=` | string / number | `deviceCategory != "tablet"` |
| `beginsWith` | string | `pagePath beginsWith "/"` |
| `endsWith` | string | `pagePath endsWith ".html"` |
| `contains` | string | `pageTitle contains "Blog"` |
| `matches` | string | `pagePath matches "^/blog/.*"` |
| `<` `<=` `>` `>=` | number | `sessions > 100` |
| `AND` / `OR` / `NOT` | — | `country = "Spain" AND NOT deviceCategory = "tablet"` |
| `(...)` | — | `(country = "Spain" OR country = "France") AND sessions > 100` |

`AND` binds tighter than `OR`. Use parentheses to override.

### Realtime

```bash
gafour realtime run --property-id 123456789
gafour realtime run --property-id 123456789 --metrics activeUsers --dimensions country
```

### Metadata

```bash
# List all available dimensions
gafour metadata dimensions --property-id 123456789

# Search dimensions by name
gafour metadata dimensions --property-id 123456789 --search device

# List all available metrics
gafour metadata metrics --property-id 123456789 --search revenue

# Check which dimensions and metrics can be queried together
gafour metadata compatibility \
  --property-id 123456789 \
  --dimensions date,country \
  --metrics activeUsers,sessions

# Show only incompatible combinations
gafour metadata compatibility \
  --property-id 123456789 \
  --dimensions date,country \
  --metrics activeUsers,sessions \
  --filter incompatible
```

### Key Events

```bash
gafour key-events list <property-id>       # list all key events (formerly conversions)
```

### Custom Dimensions & Metrics

```bash
gafour custom-dimensions list <property-id>   # list custom dimensions
gafour custom-metrics list <property-id>      # list custom metrics
```

### Audiences

```bash
gafour audiences list <property-id>                    # list all audiences
gafour audiences get <property-id> <audience-id>       # get audience details
```

### Events

```bash
gafour events list <property-id> <stream-id>   # list event create rules for a stream
```

### Auth

```bash
gafour auth login --method service-account     # configure credentials
gafour auth status                             # verify connectivity
gafour auth logout                             # remove stored credentials
```

### Config

```bash
gafour config init                             # interactive setup wizard
gafour config show                             # print current config as JSON
gafour config set <key> <value>               # set a config value
gafour config unset <key>                     # reset a config value to default
```

---

## Output Formats

**`reports run` and `realtime run`** always output JSON (structured for agent/programmatic consumption).

All other commands (`accounts`, `properties`, `datastreams`, etc.) support `--format` and `--output`:

```bash
# Human-readable table (default)
gafour accounts list --format table

# Machine-readable JSON
gafour accounts list --format json

# CSV for spreadsheets
gafour accounts list --format csv --output accounts.csv
```

---

## Environment Variables

Environment variables override values in the config file.

| Variable | Description |
|---|---|
| `GA4_AUTH_METHOD` | Auth method: `service-account`, `token` |
| `GA4_KEY_FILE` | Path to service account JSON key |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON key (ADC standard) |
| `GA4_ACCESS_TOKEN` | Direct access token |
| `GA4_PROPERTY_ID` | Default property ID (skips `--property-id` flag) |

---

## Acknowledgements

This project was inspired by the work of [FunnelEnvy/gafour](https://github.com/FunnelEnvy/gafour) and the [`gafour` package on PyPI](https://pypi.org/project/gafour/). Many thanks to the authors for pioneering a GA4 command-line interface.

---

## License

MIT
