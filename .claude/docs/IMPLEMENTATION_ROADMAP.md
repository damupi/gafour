# GA4 CLI Implementation Roadmap

## Quick Start Guide

### What We Learned
1. **ga-cli (Python)** = Great for admin operations, limited auth, no reporting
2. **ga4-cli (TypeScript)** = Great for reporting, full auth, missing admin features
3. **Gap:** Nobody has both + advanced features

### Your Advantage
Build the complete solution combining the best of both with Python's simplicity.

---

## Phase-by-Phase Implementation Plan

### Phase 1: Foundation (Week 1-2)
**Goal:** MVP with core functionality

#### Setup & Structure
```
project/
├── pyproject.toml          # Modern Python packaging
├── setup.py                # Legacy support
├── setup.cfg               # Additional config
├── MANIFEST.in
├── src/
│   └── ga4_cli/
│       ├── __init__.py
│       ├── __version__.py
│       ├── cli.py          # Main entry point
│       ├── config.py       # Config management
│       ├── auth.py         # Service account auth
│       ├── api_client.py   # API wrapper
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── accounts.py
│       │   ├── properties.py
│       │   ├── datastreams.py
│       │   └── config.py
│       ├── formatters/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── table.py
│       │   └── json.py
│       └── models/
│           ├── __init__.py
│           ├── account.py
│           └── property.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_cli.py
│   ├── test_auth.py
│   ├── test_commands.py
│   └── test_formatters.py
├── docs/
│   ├── index.rst
│   ├── installation.rst
│   ├── authentication.rst
│   └── commands.rst
├── .github/
│   └── workflows/
│       ├── test.yml
│       └── lint.yml
└── README.md
```

#### Core Implementation
```python
# Basic CLI structure (click-based)
import click
from . import commands

@click.group()
@click.version_option()
def cli():
    """GA4 CLI - Command-line tool for Google Analytics 4"""
    pass

cli.add_command(commands.accounts.accounts)
cli.add_command(commands.properties.properties)
cli.add_command(commands.datastreams.datastreams)
cli.add_command(commands.config.config)
```

#### Deliverables
- Service account authentication working
- Account list/get commands
- Property list/get/create/delete commands
- Data stream list/get/create commands
- Table and JSON output
- Config init/show commands
- 100+ lines of tests
- Basic README

### Phase 2: Enhance Auth & Add Reporting (Week 3-4)
**Goal:** Multi-auth support + reporting capability

#### Authentication Expansion
```python
# Add to auth.py
class GoogleAuth:
    @staticmethod
    def service_account(credentials_path):
        # Service account flow
        pass
    
    @staticmethod
    def oauth2(scopes):
        # OAuth2 flow with browser redirect
        pass
    
    @staticmethod
    def access_token(token):
        # Direct token validation
        pass
```

#### Reporting Commands
```python
# commands/reports.py
@reports.command()
@click.option('--property-id', required=True)
@click.option('--metrics', required=True, multiple=True)
@click.option('--start-date', required=True)
@click.option('--end-date', required=True)
@click.option('--dimensions', multiple=True)
@click.option('--filters')
@click.option('--limit', default=1000)
@click.option('--offset', default=0)
@click.option('--order-by')
@click.option('--format', type=click.Choice(['table', 'json', 'csv']))
def run(property_id, metrics, start_date, end_date, dimensions, 
        filters, limit, offset, order_by, format):
    """Run an analytics report"""
    pass
```

#### Real-time Queries
```python
# commands/realtime.py
@realtime.command()
@click.option('--property-id', required=True)
@click.option('--dimensions', multiple=True)
@click.option('--metrics', multiple=True)
def run(property_id, dimensions, metrics):
    """Query real-time data"""
    pass
```

#### Metadata Commands
```python
# commands/metadata.py
@metadata.command()
@click.option('--property-id', required=True)
@click.option('--type', type=click.Choice(['dimensions', 'metrics']))
@click.option('--search')
@click.option('--filter')
def list_items(property_id, type, search, filter):
    """List and search available dimensions/metrics"""
    pass
```

#### Output Formats Enhancement
```python
# formatters/csv.py - NEW
class CSVFormatter:
    def format(self, data, headers=None):
        """Convert data to CSV"""
        pass
```

#### Deliverables
- OAuth2 authentication working
- Direct token support
- Report execution with filters/dimensions
- Real-time data queries
- Metadata browsing with search
- CSV export format
- 200+ lines of tests
- Auth documentation

### Phase 3: Advanced Features (Week 5-6)
**Goal:** Differentiate from competitors

#### Dry-run Implementation
```python
# utils/dry_run.py
class DryRun:
    def __init__(self, enabled=False):
        self.enabled = enabled
    
    def preview(self, operation, data):
        """Show what would happen without executing"""
        if self.enabled:
            click.echo(f"Would {operation}: {data}")
            raise SystemExit(0)
```

#### Batch Operations
```python
# commands/batch.py
@properties.command()
@click.option('--batch', type=click.File('r'), required=True)
@click.option('--dry-run', is_flag=True)
def create_batch(batch, dry_run):
    """Create multiple properties from CSV"""
    # CSV: account_id,name,timezone,currency
    pass
```

#### Property Cloning
```python
# commands/properties.py - ADD
@properties.command()
@click.option('--property-id', required=True)
@click.option('--name', required=True)
@click.option('--account-id', required=True)
@click.option('--copy-streams', is_flag=True, default=True)
def clone(property_id, name, account_id, copy_streams):
    """Clone a property with settings and streams"""
    pass
```

#### Audience Management
```python
# commands/audiences.py - NEW
@audiences.command()
@click.option('--property-id', required=True)
def list(property_id):
    """List audiences"""
    pass

@audiences.command()
@click.option('--property-id', required=True)
@click.option('--name', required=True)
@click.option('--definition', required=True)
def create(property_id, name, definition):
    """Create an audience"""
    pass
```

#### Event Management
```python
# commands/events.py - NEW
@events.command()
@click.option('--property-id', required=True)
def list(property_id):
    """List custom events"""
    pass

@events.command()
@click.option('--property-id', required=True)
@click.option('--name', required=True)
@click.option('--description')
def create(property_id, name, description):
    """Create a custom event"""
    pass
```

#### Error Handling Enhancement
```python
# utils/errors.py
class GA4Error(Exception):
    def __init__(self, message, hint=None, command=None):
        self.message = message
        self.hint = hint
        self.command = command
    
    def formatted(self):
        output = f"Error: {self.message}"
        if self.hint:
            output += f"\n→ {self.hint}"
        if self.command:
            output += f"\n→ Try: {self.command}"
        return output
```

#### Deliverables
- Dry-run for all write operations
- Batch creation from CSV
- Property cloning
- Audience CRUD
- Event CRUD
- Improved error messages
- 300+ lines of tests
- Advanced features documentation

### Phase 4: Polish & Distribution (Week 7-8)
**Goal:** Production-ready tool

#### Input Validation
```python
# utils/validators.py
class Validators:
    @staticmethod
    def validate_property_id(property_id):
        if not property_id.isdigit():
            raise GA4Error(
                f"Property ID must be numeric, got {property_id}",
                hint="Property IDs are found in Analytics settings"
            )
    
    @staticmethod
    def validate_timezone(timezone):
        if timezone not in pytz.all_timezones:
            raise GA4Error(
                f"Unknown timezone: {timezone}",
                hint="Run 'ga4 timezones list' for valid options"
            )
```

#### Progress Indicators
```python
# utils/progress.py
from rich.progress import Progress

def long_operation(operation_name, items):
    with Progress() as progress:
        task = progress.add_task(operation_name, total=len(items))
        for item in items:
            # Process item
            progress.update(task, advance=1)
```

#### Interactive Prompts
```python
# utils/prompts.py
def confirm_operation(operation, details):
    """Prompt user before destructive operation"""
    click.echo(f"About to {operation}:")
    for key, value in details.items():
        click.echo(f"  {key}: {value}")
    
    return click.confirm("Continue?", default=False)
```

#### Shell Completion
```bash
# Install completion for different shells
_GA4_COMPLETE=bash_source ga4 > ~/.bash_completion.d/ga4
_GA4_COMPLETE=zsh_source ga4 > ~/.zsh/completions/_ga4
```

#### Documentation
```
docs/
├── index.md
├── installation.md
├── authentication/
│   ├── oauth2.md
│   ├── service-account.md
│   └── tokens.md
├── commands/
│   ├── accounts.md
│   ├── properties.md
│   ├── reports.md
│   ├── realtime.md
│   ├── audiences.md
│   ├── events.md
│   └── metadata.md
├── guides/
│   ├── getting-started.md
│   ├── batch-operations.md
│   ├── automation.md
│   └── troubleshooting.md
└── examples/
    ├── list-properties.sh
    ├── run-report.sh
    ├── export-to-csv.sh
    └── batch-clone.sh
```

#### Testing Coverage
```python
# Test structure
tests/
├── unit/
│   ├── test_auth.py
│   ├── test_formatters.py
│   ├── test_validators.py
│   └── test_models.py
├── integration/
│   ├── test_commands.py
│   ├── test_api_integration.py
│   └── test_auth_flows.py
├── e2e/
│   ├── test_workflows.py
│   └── test_error_handling.py
└── fixtures/
    ├── mock_responses.py
    ├── test_data.py
    └── fake_api.py
```

#### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest --cov=ga4_cli
      - run: mypy src/
      - run: black --check src/
      - run: flake8 src/
```

#### PyPI Distribution
```toml
# pyproject.toml
[project]
name = "ga4-cli"
version = "1.0.0"
description = "Complete CLI for Google Analytics 4"
authors = [{name = "Your Name", email = "you@example.com"}]
requires-python = ">=3.9"
dependencies = [
    "click>=8.0",
    "google-analytics-admin>=0.27.0",
    "google-auth>=2.0",
    "google-auth-oauthlib>=0.4.0",
    "rich>=13.0",
    "pytz>=2023.3",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "mypy>=1.0",
    "black>=23.0",
    "flake8>=5.0",
    "isort>=5.0",
    "sphinx>=5.0",
]

[project.scripts]
ga4 = "ga4_cli.cli:cli"
```

#### Deliverables
- Full test coverage (80%+)
- Type hints throughout
- Shell completion
- Comprehensive documentation
- CI/CD pipeline
- PyPI package ready
- Release on PyPI
- GitHub releases with binaries

---

## Development Best Practices

### Code Organization
```
ga4_cli/
├── __init__.py          # Package initialization
├── __version__.py       # Version string (single source of truth)
├── cli.py              # Main CLI group
├── config.py           # Configuration management
├── auth.py             # Authentication core
├── api_client.py       # Google Analytics API wrapper
├── commands/           # Command groups
├── formatters/         # Output formatters
├── models/             # Data models (Pydantic)
└── utils/              # Utilities (validation, errors, etc)
```

### Type Hints Pattern
```python
from typing import Dict, List, Optional
from pydantic import BaseModel

class Account(BaseModel):
    account_id: str
    display_name: str
    
def list_accounts(
    credentials: str,
    format: str = "table",
) -> List[Account]:
    """List all GA4 accounts."""
    pass
```

### Error Handling Pattern
```python
try:
    # Do something
    pass
except google.auth.exceptions.DefaultCredentialsError as e:
    raise GA4Error(
        "Could not find valid credentials",
        hint="Run 'ga4 auth init' or set GOOGLE_APPLICATION_CREDENTIALS",
        command="ga4 auth init"
    )
except Exception as e:
    raise GA4Error(f"Unexpected error: {e}")
```

### Testing Pattern
```python
def test_list_accounts(mock_analytics_admin, capsys):
    """Test listing accounts returns proper format"""
    # Arrange
    mock_analytics_admin.list_accounts.return_value = [...]
    
    # Act
    result = commands.accounts.list()
    
    # Assert
    assert "Account ID" in capsys.readouterr().out
    assert len(result) == expected_count
```

---

## Success Metrics

### Code Quality
- [ ] 80%+ test coverage
- [ ] All type hints in place
- [ ] Zero linting errors
- [ ] No security vulnerabilities

### Feature Completeness
- [ ] All commands documented
- [ ] All error messages helpful
- [ ] All auth methods working
- [ ] All output formats available

### User Experience
- [ ] Installation < 2 minutes
- [ ] Setup < 5 minutes
- [ ] First command in < 1 minute
- [ ] Documentation covers 95% of use cases

### Distribution
- [ ] PyPI listing active
- [ ] pip install works smoothly
- [ ] GitHub releases with binaries
- [ ] 100+ GitHub stars (target)

---

## Resource Estimates

| Phase | Duration | Team Size | Key Deliverables |
|-------|----------|-----------|------------------|
| 1 | 2 weeks | 1 | MVP with admin operations |
| 2 | 2 weeks | 1 | Reporting + real-time |
| 3 | 2 weeks | 1 | Advanced features |
| 4 | 2 weeks | 1-2 | Polish + distribution |
| **Total** | **8 weeks** | **1-2** | **Production GA4 CLI** |

---

## Risk Mitigation

### Technical Risks
- **Google API Changes:** Monitor API announcements, use version constraints
- **Auth Issues:** Comprehensive testing with different credential types
- **Performance:** Cache metadata, pagination for large datasets

### User Experience Risks
- **Command Learning Curve:** Excellent help text, examples, interactive guide
- **Breaking Changes:** Semantic versioning, deprecation warnings
- **Documentation Gaps:** User feedback loop, community contributions

### Distribution Risks
- **Dependency Conflicts:** Regular dependency updates, CI testing
- **Python Version Support:** Test on 3.9, 3.10, 3.11, 3.12
- **Platform Support:** Test on Linux, macOS, Windows

---

## Success Story

Upon completion, you'll have:

1. **Complete Feature Set:** Everything users need in one tool
2. **Flexible Authentication:** OAuth2, service account, tokens
3. **Professional Quality:** Type hints, tests, docs, CI/CD
4. **Production Ready:** Error handling, validation, recovery
5. **Easy to Use:** Clear commands, helpful errors, examples
6. **Easy to Maintain:** Pure Python, well-organized, well-tested
7. **Community Ready:** PyPI distribution, GitHub collaboration

This positions your GA4 CLI as the definitive solution for command-line GA4 management.

