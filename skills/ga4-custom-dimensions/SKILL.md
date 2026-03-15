---
name: ga4-custom-dimensions
version: 1.0.0
description: "List custom dimensions registered on a GA4 property."
metadata:
  openclaw:
    category: "analytics"
    requires:
      bins: ["gafour"]
    cliHelp: "gafour custom-dimensions --help"
---

# ga4 custom-dimensions

> **PREREQUISITE:** The `gafour` CLI must be installed and authenticated before using this skill.
> - Installation: see the [Installation](https://github.com/damupi/gafour#installation) section of the README.
> - Authentication: see the [Authentication](https://github.com/damupi/gafour#authentication) section. Run `gafour auth status` to verify.

```bash
gafour custom-dimensions <command> <property-id> [flags]
```

## Commands

| Command | Description |
|---------|-------------|
| `custom-dimensions list <property-id>` | List all custom dimensions for a property. |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format`, `-f` | `json` | Output format: `json`, `table`, `csv`. |
| `--output`, `-o` | *(stdout)* | Write output to a file path. |

## Response structure (JSON)

```json
[
  {
    "name": "properties/123456789/customDimensions/cd1",
    "parameter_name": "plan_type",
    "display_name": "Plan Type",
    "description": "The user's subscription plan.",
    "scope": "USER",
    "disallow_ads_personalization": false
  }
]
```

`scope` values: `EVENT`, `USER`, `DIMENSION_SCOPE_UNSPECIFIED`.

## Examples

```bash
# List all custom dimensions for a property
gafour custom-dimensions list 123456789
```
