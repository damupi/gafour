# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

A GA4 CLI tool that improves on existing options by offering:
- Advanced filtering with a DSL (`--filter`, `--metric-filter`) supporting AND/OR/NOT/grouping
- Metadata retrieval (available dimensions/metrics per property)
- Compatibility checking (which dimensions/metrics can be queried together)
- Account summaries (list accounts, properties, data streams)
- Report running with JSON output aligned to the GA4 RunReportResponse structure

## Relevant Google APIs

- **Google Analytics Data API v1** — run reports, fetch metadata, check dimension/metric compatibility
- **Google Analytics Admin API v1** — account/property management, data streams, audiences, key events, custom dimensions, custom metrics
- Auth: OAuth 2.0 (browser flow via `InstalledAppFlow`), Service Account (JSON key), or raw Bearer token

## Tech Stack

**Package manager:** `uv`

**Runtime dependencies:**
- `google-analytics-data` — GA4 Data API client
- `google-analytics-admin` — GA4 Admin API client
- `google-auth` — credential handling and token refresh
- `google-auth-oauthlib` — OAuth2 browser flow (`InstalledAppFlow`)
- `typer` — CLI framework
- `rich` — terminal output (tables, JSON, color)
- `pydantic` — input/output validation and models for all GA4 request/response shapes

**Dev dependencies:**
- `pytest` + `pytest-cov` — TDD, unit and integration tests
- `ruff` — linting and formatting
- `mypy` — static type checking

## Development Approach

- **TDD**: write tests before implementation. Every command has a corresponding test module.
- **Pydantic models** for all GA4 request inputs (filters, date ranges, dimensions, metrics) and parsed responses.
- Pure CLI — no MCP layer. The MCP GA4 server (`damupi/mcp-ga4-resources`) is used as a code reference/foundation for GA4 API call patterns.

## Delivery Goals

1. Working Python CLI published to PyPI
2. Public GitHub repo created once the CLI is stable

## Documentation

All project docs live in `.claude/docs/`:
- `PRD.md` — full product requirements, command reference, phases
- `ADDITIONAL_RESEARCH.md` — patterns from GWS CLI and mcp-ga4-resources
- `GA4_CLI_RESEARCH.md` — competitive analysis (ga-cli vs ga4-cli)
- `FEATURE_COMPARISON.md` — feature matrix across tools

## Commands (to be added once scaffolded)

```bash
uv run gafour --help          # run CLI
uv run pytest              # run all tests
uv run pytest tests/test_accounts.py  # run single test module
uv run ruff check .        # lint
uv run mypy .              # type check
```

## Package Layout

Uses `src/` layout:

```
ga4-cli/
├── src/
│   └── ga4/          # installable package
│       ├── __init__.py
│       ├── cli.py    # typer app entry point
│       ├── commands/ # one module per command group
│       ├── models/   # pydantic models
│       └── auth.py   # credential helpers
├── tests/
├── pyproject.toml
└── uv.lock
```

Package name: `gafour`, entry point: `gafour` command.

# Release Management Protocol

This repository uses **Google's `release-please`** GitHub Action to automate versioning and changelog generation. All AI agents and automated processes must strictly follow this workflow.

## 1. Commit Message Standard (Mandatory)
All commits must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. This is the **only** way the system determines version bumps.

### Commit types

| Type | Description | Version bump |
|------|-------------|--------------|
| `feat:` | A new feature | Minor (e.g., 1.0.0 → 1.1.0) |
| `fix:` | A bug fix | Patch (e.g., 1.0.0 → 1.0.1) |
| `docs:` | Documentation changes | None |
| `style:` | Code style changes (formatting, indentation) | None |
| `refactor:` | Code refactoring | None |
| `test:` | Add or modify tests | None |
| `chore:` | General chores or maintenance tasks | None |
| `feat!:` / `fix!:` | Breaking change | Major (e.g., 1.0.0 → 2.0.0) |

> **Note:** Always include a clear description in the commit message, as this text is automatically pulled into the `CHANGELOG.md`.

## 2. The Release PR Workflow
1.  **Automation:** When a commit is merged to the main branch, `release-please` will automatically create or update a "Release PR."
2.  **No Manual Edits:** Do **not** manually edit `CHANGELOG.md` or `package.json`/version files. The action handles these updates within the Release PR.
3.  **Triggering Releases:** A formal release (tagging and GitHub Release creation) only occurs when the **Release PR** itself is merged into the main branch.

## 3. Agent Constraints
* **Verification:** Before proposing a commit, verify that the prefix accurately reflects the impact of the code changes.
* **Consistency:** If multiple changes are made, use the highest impact prefix (e.g., if a fix and a feature are combined, use `feat:`).
* **Conflict Resolution:** If a Release PR has a merge conflict, notify the user immediately; do not attempt to force-push to the release branch unless specifically instructed.

## Architecture Notes

### Output conventions
- `reports run` and `realtime run` — **JSON only**, always aligned to the GA4 `RunReportResponse` / `RunRealtimeReportResponse` proto structure.
- All admin commands (`accounts`, `properties`, `datastreams`, etc.) — support `--format table|json|csv` (table is the default).

### Auth (`src/gafour/auth.py`)
- Config lives at `~/.config/gafour/config.json`
- Three auth methods: `oauth2` (default recommended), `service-account`, `token`
- `ANALYTICS_SCOPES` is defined in `config.py` — import from there, never hardcode
- `_build_oauth2_credentials(config)` — builds `Credentials` from stored dict, auto-refreshes if expired, persists new token back to config
- `_serialize_credentials(creds)` — converts a `Credentials` object to a JSON-safe dict for storage
- OAuth2 client secret expected at `~/.config/gafour/client_secret.json` (prompted on first login)

### Filter DSL (`src/gafour/filters.py`)
- `parse_filter_expression(str) -> FilterExpression` — converts the `--filter` / `--metric-filter` string into a `FilterExpression` Pydantic model.
- `filter_expression_to_proto(FilterExpression) -> ProtoFilterExpression` — converts the Pydantic model to the GA4 proto required by the API client.
- `models/report.py` is proto-free; all proto imports live in `filters.py` and command handlers.

### Pydantic models (`src/gafour/models/`)
- All GA4 request inputs and responses are Pydantic models.
- `FilterExpression`, `FilterField`, `StringFilter`, `NumericFilter`, `NumericValue` mirror the GA4 FilterExpression proto hierarchy.
- `ReportRequest.dimension_filter` and `metric_filter` are typed `FilterExpression | None`, not `str`.
