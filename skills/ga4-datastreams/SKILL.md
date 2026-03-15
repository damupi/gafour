---
name: ga4-datastreams
version: 1.0.0
description: "List and inspect data streams for a GA4 property, including web measurement IDs."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["ga4"]
    cliHelp: "ga4 datastreams --help"
---

# ga4 datastreams

> **PREREQUISITE:** The `ga4` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/ga4-cli#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/ga4-cli#authentication) section. Run `ga4 auth status` to verify.

```bash
ga4 datastreams <command> <property-id> [flags]
```

## Commands

| Command | Description |
|---------|-------------|
| `datastreams list <property-id>` | List all data streams for a property. |
| `datastreams get <property-id> <stream-id>` | Get details for a specific data stream. |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

## Response structure (JSON)

### `datastreams list`

```json
[
  {
    "name": "properties/123456789/dataStreams/9876543",
    "display_name": "My Website Stream",
    "type_": "WEB_DATA_STREAM",
    "create_time": "2021-03-10 12:00:00+00:00",
    "update_time": "2024-05-20 09:00:00+00:00",
    "web_stream_data": {
      "default_uri": "https://www.example.com",
      "measurement_id": "G-XXXXXXXXXX"
    }
  }
]
```

### `datastreams get`

Single object with the same fields as above.

`web_stream_data` is present for web streams and contains the `measurement_id` (the `G-XXXXXXXXXX` tag used in gtag.js). The numeric stream ID is the trailing segment of `name`.

## Examples

```bash
# List all streams for a property
ga4 datastreams list 123456789

# Get a specific stream (includes measurement ID)
ga4 datastreams get 123456789 9876543
```
