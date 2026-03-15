# ga4-cli

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
pip install ga4-cli
```

Or with `uv`:

```bash
uv tool install ga4-cli
```

### From source

```bash
git clone https://github.com/damupi/ga4-cli.git
cd ga4-cli
pip install -e .
```

Or with `uv`:

```bash
git clone https://github.com/damupi/ga4-cli.git
cd ga4-cli
uv sync
uv run ga4 --help
```

> **Note:** When installed from source with `uv sync`, prefix all commands with `uv run` (e.g. `uv run ga4 accounts list`) or activate the virtual environment first with `source .venv/bin/activate`.

Verify the installation:

```bash
ga4 --version
```

---

## Quick Start

```bash
# 1. Run the setup wizard
ga4 config init

# 2. Verify authentication
ga4 auth status

# 3. List your accounts
ga4 accounts list

# 4. List properties for an account
ga4 properties list --account-id 123456

# 5. Run a report
ga4 reports run \
  --property-id 123456789 \
  --metrics activeUsers,sessions \
  --start-date 2026-01-01 \
  --end-date 2026-03-14 \
  --dimensions date,country
```

---

## Authentication

`ga4-cli` supports two authentication methods.

### Option A — Service Account (recommended for scripts and CI)

1. Go to [Google Cloud Console → IAM & Admin → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Create a service account and download the JSON key file
3. Grant the service account **Viewer** access in GA4 → Admin → Account / Property Access Management
4. Configure the CLI:

```bash
ga4 config set auth_method service-account
ga4 config set key_file /path/to/key.json
```

Or set the standard Application Default Credentials environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### Option B — Access Token

Use a short-lived OAuth2 access token (useful in automated environments where a token is already available):

```bash
ga4 config set auth_method token
ga4 config set access_token YOUR_ACCESS_TOKEN
```

Or via environment variable:

```bash
export GA4_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
```

### Verify

```bash
ga4 auth status
```

---

## Configuration

Run the interactive wizard to set up everything at once:

```bash
ga4 config init
```

Or set individual values:

```bash
ga4 config set auth_method service-account
ga4 config set key_file /path/to/key.json
ga4 config set default_property_id 123456789   # skip --property-id on every command
ga4 config set output_format table              # table | json | csv
```

View current config:

```bash
ga4 config show
```

Clear a value back to its default:

```bash
ga4 config unset default_property_id
```

Config is stored at `~/.config/ga4/config.json`.

---

## Commands

### Accounts

```bash
ga4 accounts list                        # list all accessible accounts
ga4 accounts get <account-id>            # get account details
```

### Properties

```bash
ga4 properties list --account-id <id>   # list properties for an account
ga4 properties get <property-id>        # get property details
```

### Data Streams

```bash
ga4 datastreams list <property-id>               # list data streams
ga4 datastreams get <property-id> <stream-id>    # get stream details (includes measurement ID)
```

### Reports

```bash
ga4 reports run \
  --property-id 123456789 \
  --metrics activeUsers,sessions,engagementRate \
  --start-date 2026-01-01 \
  --end-date 2026-03-14 \
  --dimensions date,country,deviceCategory \
  --order-by sessions:desc \
  --limit 100 \
  --format csv \
  --output report.csv
```

### Realtime

```bash
ga4 realtime run --property-id 123456789
ga4 realtime run --property-id 123456789 --metrics activeUsers --dimensions country
```

### Metadata

```bash
# List all available dimensions
ga4 metadata dimensions --property-id 123456789

# Search dimensions by name
ga4 metadata dimensions --property-id 123456789 --search device

# List all available metrics
ga4 metadata metrics --property-id 123456789 --search revenue

# Check which dimensions and metrics can be queried together
ga4 metadata compatibility \
  --property-id 123456789 \
  --dimensions date,country \
  --metrics activeUsers,sessions

# Show only incompatible combinations
ga4 metadata compatibility \
  --property-id 123456789 \
  --dimensions date,country \
  --metrics activeUsers,sessions \
  --filter incompatible
```

### Key Events

```bash
ga4 key-events list <property-id>       # list all key events (formerly conversions)
```

### Custom Dimensions & Metrics

```bash
ga4 custom-dimensions list <property-id>   # list custom dimensions
ga4 custom-metrics list <property-id>      # list custom metrics
```

### Audiences

```bash
ga4 audiences list <property-id>                    # list all audiences
ga4 audiences get <property-id> <audience-id>       # get audience details
```

### Events

```bash
ga4 events list <property-id> <stream-id>   # list event create rules for a stream
```

### Auth

```bash
ga4 auth login --method service-account     # configure credentials
ga4 auth status                             # verify connectivity
ga4 auth logout                             # remove stored credentials
```

### Config

```bash
ga4 config init                             # interactive setup wizard
ga4 config show                             # print current config as JSON
ga4 config set <key> <value>               # set a config value
ga4 config unset <key>                     # reset a config value to default
```

---

## Output Formats

All `list`, `get`, and `run` commands support `--format` and `--output`:

```bash
# Human-readable table (default)
ga4 accounts list --format table

# Machine-readable JSON
ga4 accounts list --format json

# CSV for spreadsheets or data pipelines
ga4 reports run ... --format csv --output report.csv
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

## License

MIT
