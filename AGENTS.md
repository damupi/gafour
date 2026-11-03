# AGENTS.md

This file provides guidance to coding agents working in this repository.

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

## Documentation

All project docs live in `.claude/docs/`:
- `PRD.md` — full product requirements, command reference, phases
- `ADDITIONAL_RESEARCH.md` — patterns from GWS CLI and mcp-ga4-resources
- `GA4_CLI_RESEARCH.md` — competitive analysis (ga-cli vs ga4-cli)
- `FEATURE_COMPARISON.md` — feature matrix across tools

## Commands

```bash
uv run gafour --help          # run CLI
uv run pytest              # run all tests
uv run pytest tests/test_accounts.py  # run single test module
uv run ruff check .        # lint
uv run mypy .              # type check
uv build                   # build wheel and source distribution
```

## Package Layout

Uses `src/` layout:

```
gafour/
├── src/
│   └── gafour/       # installable package
│       ├── __init__.py
│       ├── cli.py    # Typer app entry point
│       ├── commands/ # one module per command group
│       ├── models/   # Pydantic models
│       ├── auth.py   # credential helpers
│       └── update.py # bounded GitHub release checks and safe upgrades
├── tests/
├── skills/
├── agents/
├── pyproject.toml
└── uv.lock
```

Package name: `gafour`, entry point: `gafour` command.

## Agent integrations

- `skills/gafour-cli/` is the single source of truth for the distributable CLI skill.
- `agents/google-analyst.md` is the public, user-neutral GA4 reporting agent. Do not copy private memory, local paths, credentials, or machine-specific configuration into it.
- Keep the skill, public agent, implemented CLI, and `README.md` aligned.
- `skills/gafour-cli/compatibility.json` records the reviewed CLI version and is synchronized by Release Please.
- Do not duplicate CLI command reference material in the public agent or create separate per-command skills.
- Do not restore `docs/skills.md`.
- Validate the skill package and local Markdown links after changing agent integration documentation.

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
2.  **No Manual Edits:** Do **not** manually edit `CHANGELOG.md` or `pyproject.toml`/version files. The action handles these updates within the Release PR. The only exception is correcting entries of already-published releases (e.g. removing duplicates); commit that as `chore:` so it does not show up in the next changelog.
3.  **Triggering Releases:** A formal release (tagging and GitHub Release creation) only occurs when the **Release PR** itself is merged into the main branch.
4.  **Version synchronization:** Release Please updates `.release-please-manifest.json`, `pyproject.toml`, `src/gafour/__init__.py`, `skills/gafour-cli/compatibility.json`, and the `gafour` package entry in `uv.lock`.
5.  **Distribution:** Releases are GitHub-only. Never add a bare PyPI install path. The release workflow validates the tag and uploads wheel and source artifacts to the GitHub Release.

## 3. Merging (Squash Only)
`release-please` reads every commit on `main`, including merge commits and any conventional-commit lines inside a commit body. A merge commit ("Merge pull request #N …") carries the PR title in its body, so the same change gets listed twice in the changelog.

* **Always squash-merge PRs** (`gh pr merge <N> --squash`). The repository only allows squash merges, uses the PR title as the commit title and leaves the body blank.
* **The PR title is the commit message**, so it must be a valid Conventional Commit (`feat: …`, `fix: …`).
* **Never create merge commits on `main` locally** (`git merge` + `git push`). Rebase or squash first.
* **Do not put extra `feat:`/`fix:` lines in commit bodies**; `release-please` treats each one as a separate changelog entry.

## 4. Agent Constraints
* **Verification:** Before proposing a commit, verify that the prefix accurately reflects the impact of the code changes.
* **Consistency:** If multiple changes are made, use the highest impact prefix (e.g., if a fix and a feature are combined, use `feat:`).
* **Conflict Resolution:** If a Release PR has a merge conflict, notify the user immediately; do not attempt to force-push to the release branch unless specifically instructed.

## Architecture Notes

### Output conventions
- `reports run` and `realtime run` — **JSON only**, always aligned to the GA4 `RunReportResponse` / `RunRealtimeReportResponse` proto structure.
- All admin read commands (`accounts`, `properties`, `datastreams`, etc.) support `--format table|json|csv` (JSON is the default).

### Updates (`src/gafour/update.py`)
- `gafour version [--json]` compares the installed distribution with the latest stable public GitHub release.
- `gafour upgrade [--yes]` installs an explicit `vX.Y.Z` tag from `damupi/gafour` for `uv` or pip installs.
- Editable installs are never overwritten; users receive checkout guidance instead.
- Release checks are bounded, cached once daily, disabled in CI/non-TTY sessions, and isolated from credentials, headers, askpass, `.curlrc`, and Git URL rewrites.

### Auth (`src/gafour/auth.py`)
- Config lives at `~/.config/gafour/config.json`
- Three auth methods: `oauth2`, `service-account` (default), `token`
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
