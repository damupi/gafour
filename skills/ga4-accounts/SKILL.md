---
name: ga4-accounts
version: 1.0.0
description: "List and inspect GA4 accounts accessible to the authenticated credential."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["ga4"]
    cliHelp: "ga4 accounts --help"
---

# ga4 accounts

> **PREREQUISITE:** The `ga4` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/ga4-cli#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/ga4-cli#authentication) section. Run `ga4 auth status` to verify.

```bash
ga4 accounts <command> [flags]
```

## Commands

| Command | Description |
|---------|-------------|
| `accounts list` | List all GA4 accounts accessible to the credential. |
| `accounts get <account-id>` | Get details for a specific account. |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

## Response structure (JSON)

### `accounts list`

```json
[
  {
    "name": "accounts/123456",
    "display_name": "Acme Corp",
    "region_code": "US",
    "create_time": "2021-01-15 10:30:00+00:00",
    "update_time": "2024-06-01 08:00:00+00:00"
  }
]
```

### `accounts get`

```json
{
  "name": "accounts/123456",
  "display_name": "Acme Corp",
  "region_code": "US",
  "create_time": "2021-01-15 10:30:00+00:00",
  "update_time": "2024-06-01 08:00:00+00:00"
}
```

The numeric account ID is the trailing segment of `name` (e.g. `"accounts/123456"` → `"123456"`).

## Examples

```bash
# List all accessible accounts
ga4 accounts list

# Get details for a specific account
ga4 accounts get 123456

# List accounts as a table
ga4 accounts list --format table
```
