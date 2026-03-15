---
name: ga4-key-events
version: 1.0.0
description: "List key events (formerly conversions) configured on a GA4 property."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["ga4x"]
    cliHelp: "ga4x key-events --help"
---

# ga4 key-events

> **PREREQUISITE:** The `ga4x` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/ga4-cli#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/ga4-cli#authentication) section. Run `ga4x auth status` to verify.

```bash
ga4x key-events <command> <property-id> [flags]
```

## Commands

| Command | Description |
|---------|-------------|
| `key-events list <property-id>` | List all key events for a property. |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

## Response structure (JSON)

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

## Examples

```bash
# List all key events for a property
ga4x key-events list 123456789
```
