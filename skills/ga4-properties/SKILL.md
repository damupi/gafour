---
name: ga4-properties
version: 1.0.0
description: "List and inspect GA4 properties within an account."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["gafour"]
    cliHelp: "gafour properties --help"
---

# ga4 properties

> **PREREQUISITE:** The `gafour` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/gafour#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/gafour#authentication) section. Run `gafour auth status` to verify.

```bash
gafour properties <command> [flags]
```

## Commands

| Command | Description |
|---------|-------------|
| `properties list --account-id <id>` | List all properties for a given account. |
| `properties get <property-id>` | Get details for a specific property. |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--account-id`, `-a` | *(required for list)* | Numeric account ID to filter by. |
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

## Response structure (JSON)

### `properties list`

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

### `properties get`

Single object with the same fields as above.

The numeric property ID is the trailing segment of `name` (e.g. `"properties/123456789"` → `"123456789"`). Use this ID as `--property-id` in report and metadata commands.

## Examples

```bash
# List properties for account 123456
gafour properties list --account-id 123456

# Get details for a specific property
gafour properties get 123456789
```
