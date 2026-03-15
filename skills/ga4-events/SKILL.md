---
name: ga4-events
version: 1.0.0
description: "List event create rules for a GA4 data stream."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["ga4"]
    cliHelp: "ga4 events --help"
---

# ga4 events

> **PREREQUISITE:** The `ga4` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/ga4-cli#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/ga4-cli#authentication) section. Run `ga4 auth status` to verify.

```bash
ga4 events <command> <property-id> <stream-id> [flags]
```

## Commands

| Command | Description |
|---------|-------------|
| `events list <property-id> <stream-id>` | List all event create rules for a data stream. |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

## Response structure (JSON)

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

The stream ID required here is the numeric ID from `ga4 datastreams list`. Use `ga4 datastreams list <property-id>` to discover available stream IDs.

## Examples

```bash
# List event create rules for a stream
ga4 events list 123456789 9876543
```
