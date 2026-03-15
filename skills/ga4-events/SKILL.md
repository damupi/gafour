---
name: ga4-events
version: 1.0.0
description: "List event create rules for a GA4 data stream."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["ga4x"]
    cliHelp: "ga4x events --help"
---

# ga4 events

> **PREREQUISITE:** The `ga4x` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/ga4x#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/ga4x#authentication) section. Run `ga4x auth status` to verify.

```bash
ga4x events <command> <property-id> <stream-id> [flags]
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

The stream ID required here is the numeric ID from `ga4x datastreams list`. Use `ga4x datastreams list <property-id>` to discover available stream IDs.

## Examples

```bash
# List event create rules for a stream
ga4x events list 123456789 9876543
```
