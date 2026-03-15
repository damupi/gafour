# Additional Research — Google Workspace CLI & mcp-ga4-resources

**Sources:** `googleworkspace/cli`, `damupi/mcp-ga4-resources`
**Purpose:** Extract patterns for the Python GA4 CLI implementation

---

## From Google Workspace CLI

### Command naming: service → resource → method

Pattern: `gws <service> <resource> <method> [flags]`

Translated to GA4:
```bash
ga4 accounts list
ga4 properties get <id>
ga4 reports run --property-id <id>
ga4 metadata list dimensions --property-id <id>
```

### Pagination flags

```bash
--page-all            # auto-paginate, stream results as NDJSON
--page-limit <n>      # max pages (default 10, 0 = unlimited)
--page-delay <ms>     # rate-limiting delay between requests
```

NDJSON output (one JSON object per line) — memory efficient and pipe-friendly.

### Dry-run mode

`--dry-run` on all write commands prints the request payload without executing.

### Semantic exit codes

```
0 = success
1 = API error (4xx/5xx)
2 = auth error
3 = validation/argument error
4 = config error
5 = network error
```

### Configuration cascade (priority order)

1. CLI flag (`--credentials-file`)
2. Environment variables (`GA4_SERVICE_ACCOUNT_FILE`, `GA4_ACCESS_TOKEN`, `GOOGLE_APPLICATION_CREDENTIALS`)
3. Config file (`~/.config/ga4/config.toml`)

### Config directory structure

```
~/.config/ga4/
├── config.toml
├── credentials.json
└── cache/
    ├── properties.json
    └── metadata.json
```

---

## From damupi/mcp-ga4-resources

### Pydantic model patterns

```python
class ReportRequest(BaseModel):
    property_id: str = Field(..., description="GA4 Property ID")
    metrics: List[str] = Field(..., description="Metric names")
    start_date: str = Field(..., description="YYYY-MM-DD")
    end_date: str = Field(..., description="YYYY-MM-DD")
    dimensions: Optional[List[str]] = None
    filters: Optional[str] = None
    limit: int = Field(default=10000, ge=1, le=100000)
    offset: int = Field(default=0, ge=0)

class ReportResponse(BaseModel):
    property_id: str
    rows: List[Row]
    row_count: int
    totals: Optional[List[dict]] = None
```

All CLI command inputs and API responses should be wrapped in Pydantic models before any rendering.

### GA4 Data API call pattern

```python
response = analytics_data.run_report(
    property=f"properties/{property_id}",
    request_body={
        "dimensions": [{"name": d} for d in dimensions],
        "metrics": [{"name": m} for m in metrics],
        "date_ranges": [{"start_date": start, "end_date": end}],
        "limit": limit,
    }
)
```

### GA4 Admin API call pattern

```python
# List properties
response = analytics_admin.list_properties(parent=f"accounts/{account_id}")

# Create property
response = analytics_admin.create_property(
    parent=f"accounts/{account_id}",
    property={"display_name": name, "time_zone": timezone}
)
```

### Error handling for GA4 API errors

```python
from google.api_core import exceptions

try:
    response = client.run_report(...)
except exceptions.InvalidArgument as e:
    raise GA4Error("Invalid argument", hint=e.message, exit_code=3)
except exceptions.PermissionDenied as e:
    raise GA4Error("Permission denied", hint=e.message, exit_code=2)
except exceptions.NotFound as e:
    raise GA4Error("Resource not found", hint=e.message, exit_code=1)
```

### Auth patterns

**Service account:**
```python
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file(
    key_path,
    scopes=["https://www.googleapis.com/auth/analytics.readonly"]
)
```

**OAuth2 browser flow:**
```python
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes=[...])
credentials = flow.run_local_server(port=0)
```

---

## Semantic error pattern (to implement in `ga4/errors.py`)

```python
class GA4CLIError(Exception):
    def __init__(self, message: str, hint: str = None,
                 recovery_command: str = None, exit_code: int = 1):
        self.message = message
        self.hint = hint
        self.recovery_command = recovery_command
        self.exit_code = exit_code
```

Rendered as:
```
Error: <message>
→ <hint>
→ Try: <recovery_command>
```
