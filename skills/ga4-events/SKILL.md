---
name: ga4-events
version: 1.0.0
description: "List event create rules for a GA4 data stream."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["gafour"]
    cliHelp: "gafour events --help"
---

# ga4 events

> **PREREQUISITE:** The `gafour` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/gafour#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/gafour#authentication) section. Run `gafour auth status` to verify.

```bash
gafour events <command> <property-id> <stream-id> [flags]
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

The stream ID required here is the numeric ID from `gafour datastreams list`. Use `gafour datastreams list <property-id>` to discover available stream IDs.

## Examples

```bash
# List event create rules for a stream
gafour events list 123456789 9876543
```
