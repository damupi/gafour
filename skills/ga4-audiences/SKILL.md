---
name: ga4-audiences
version: 1.0.0
description: "List and inspect audiences defined on a GA4 property."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["ga4"]
    cliHelp: "ga4 audiences --help"
---

# ga4 audiences

> **PREREQUISITE:** The `ga4` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/ga4-cli#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/ga4-cli#authentication) section. Run `ga4 auth status` to verify.

```bash
ga4 audiences <command> <property-id> [flags]
```

## Commands

| Command | Description |
|---------|-------------|
| `audiences list <property-id>` | List all audiences for a property. |
| `audiences get <property-id> <audience-id>` | Get details for a specific audience. |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

## Response structure (JSON)

### `audiences list`

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

### `audiences get`

Single object with the same fields as above.

The numeric audience ID is the trailing segment of `name`.

## Examples

```bash
# List all audiences for a property
ga4 audiences list 123456789

# Get a specific audience
ga4 audiences get 123456789 987654
```
