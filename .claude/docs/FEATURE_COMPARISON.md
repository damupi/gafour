# GA4 CLI Tools - Feature Comparison Matrix

## Quick Reference: Feature Availability

| Feature | ga-cli | ga4-cli | Your Tool (Recommended) |
|---------|--------|---------|------------------------|
| **Authentication** | | | |
| Service Account | ✓ | ✓ | ✓ |
| OAuth2 | ✗ | ✓ | ✓ |
| Direct Token | ✗ | ✓ | ✓ |
| **Account Management** | | | |
| List Accounts | ✓ | ✗ | ✓ |
| Get Account Details | ✓ | ✗ | ✓ |
| **Properties Management** | | | |
| List Properties | ✓ | ✓ | ✓ |
| Get Property Details | ✓ | ✓ | ✓ |
| Create Properties | ✓ | ✗ | ✓ |
| Update Properties | ✗ | ✗ | ✓ |
| Delete Properties | ✓ | ✗ | ✓ |
| Clone Properties | ✗ | ✗ | ✓ |
| **Data Streams** | | | |
| List Data Streams | ✓ | ✗ | ✓ |
| Get Stream Details | ✓ | ✗ | ✓ |
| Create Data Streams | ✓ | ✗ | ✓ |
| Delete Data Streams | ✗ | ✗ | ✓ |
| **Reporting** | | | |
| Run Custom Reports | ✗ | ✓ | ✓ |
| Filter Reports | ✗ | ✓ | ✓ |
| Sort Reports | ✗ | ✓ | ✓ |
| Pagination (limit/offset) | ✗ | ✓ | ✓ |
| Save Reports | ✗ | ✗ | ✓ |
| **Real-time Data** | | | |
| Query Real-time Data | ✗ | ✓ | ✓ |
| **Metadata** | | | |
| List Dimensions | ✗ | ✓ | ✓ |
| List Metrics | ✗ | ✓ | ✓ |
| Search Metadata | ✗ | ✗ | ✓ |
| Get Metadata Details | ✗ | ✗ | ✓ |
| **Events** | | | |
| List Events | ✗ | ✗ | ✓ |
| Get Event Details | ✗ | ✗ | ✓ |
| Create Custom Events | ✗ | ✗ | ✓ |
| **Audiences** | | | |
| List Audiences | ✗ | ✗ | ✓ |
| Get Audience Details | ✗ | ✗ | ✓ |
| Create Audiences | ✗ | ✗ | ✓ |
| Delete Audiences | ✗ | ✗ | ✓ |
| **User Properties** | | | |
| List User Properties | ✗ | ✗ | ✓ |
| Get User Property Details | ✗ | ✗ | ✓ |
| **Output Formats** | | | |
| Table Output | ✓ | ✓ | ✓ |
| JSON Output | ✓ | ✓ | ✓ |
| CSV Output | ✗ | ✓ | ✓ |
| **Additional Features** | | | |
| Configuration Management | ✓ | Basic | ✓ |
| Dry-run Mode | ✗ | ✗ | ✓ |
| Batch Operations | ✗ | ✗ | ✓ |
| Interactive Help | ✓ | ✓ | ✓ |
| Error Remediation Tips | ✗ | ✗ | ✓ |
| Progress Indicators | ✗ | ✗ | ✓ |
| Input Validation | Basic | Basic | ✓ |
| Quiet Mode | ✗ | ✓ | ✓ |

---

## Detailed Feature Breakdown

### Authentication & Configuration

#### ga-cli
- **Methods:** Service account only
- **Config Location:** Project-level
- **Environment Variable:** `GOOGLE_APPLICATION_CREDENTIALS`
- **Setup:** `ga-cli config init`
- **Flexibility:** Low (single method)

#### ga4-cli
- **Methods:** OAuth2 (interactive), Service account, Direct token
- **Config Location:** `~/.config/ga4-cli/config.json`
- **Environment Variable:** Not specified
- **Setup:** `ga4 auth login`
- **Flexibility:** High (three methods, user choice)

#### Recommended Approach
- **Methods:** OAuth2, Service account, Direct token
- **Config Location:** `~/.config/ga4-cli/config.json` (follow ga4-cli standard)
- **Environment Variables:** `GA4_SERVICE_ACCOUNT_FILE`, `GA4_ACCESS_TOKEN`, `GOOGLE_APPLICATION_CREDENTIALS`
- **Setup:** Interactive `ga4 auth init` wizard with method selection
- **Flexibility:** Maximum (three methods + environment variables)

---

### Command Hierarchy & UX

#### ga-cli Structure
```
ga-cli
├── config [init, show]
├── accounts [list, get]
├── properties [list, get, create, delete]
└── datastreams [list, get, create]
```
**Assessment:**
- Pro: Logical grouping by resource type
- Con: Limited to admin operations only
- UX: Simple, discoverable

#### ga4-cli Structure
```
ga4
├── auth [login, status, logout]
├── properties [list, get]
├── reports [run]
├── realtime [run]
├── dimensions [list]
├── metrics [list]
```
**Assessment:**
- Pro: Reporting focused, metadata exploration
- Con: Missing admin operations
- UX: Good for analysts, not admins

#### Recommended Structure
```
ga4
├── auth [login, status, logout, switch]
├── accounts [list, get]
├── properties [list, get, create, update, delete, clone]
├── datastreams [list, get, create, delete]
├── reports [run, list, save]
├── realtime [run]
├── metadata [list, search, describe]
├── events [list, get, create]
├── audiences [list, get, create, delete]
├── user-properties [list, get]
└── config [init, show, set, remove]
```
**Assessment:**
- Pro: Complete feature coverage
- Con: More commands to learn (mitigated by good help)
- UX: Logical, hierarchical, consistent

---

### Output Formats

#### ga-cli
```
Available: table, json
Example: ga-cli properties list 123456 --format json
```
- **Table Format:** Rich library, colored, padded
- **JSON Format:** Full structure, script-friendly
- **Missing:** CSV (data pipeline limitation)

#### ga4-cli
```
Available: json, table, csv
Example: ga4 reports run --format csv > report.csv
```
- **Table Format:** Human-readable
- **JSON Format:** Nested structure
- **CSV Format:** Excellent for Excel, data tools
- **Enhancement:** Quiet mode for scripting

#### Recommended Approach
```
Available: json, table, csv (default: table)
Global Flags:
  --format {json|table|csv}
  --output FILE
  --quiet
  --no-header (csv only)
  --delimiter CHAR (csv only)
```
- All three formats
- Optional output redirection to file
- CSV customization options
- Quiet mode for automation

---

### Report Capabilities

#### ga-cli
- Not supported
- Significant limitation for analytics use case

#### ga4-cli
```
ga4 reports run \
  --property-id 123456 \
  --metrics users,sessions \
  --start-date 2026-01-01 \
  --end-date 2026-03-14 \
  --dimensions date,country \
  --limit 1000 \
  --offset 0 \
  --order-by users:desc
```
- Good: Filters, dimensions, sorting
- Limited: No sampling control, no saved reports
- Missing: Report scheduling

#### Recommended Approach
```
ga4 reports run \
  --property-id 123456 \
  --metrics users,sessions,engagement_rate \
  --start-date 2026-01-01 \
  --end-date 2026-03-14 \
  --dimensions date,country,device \
  --filters "country==US" \
  --limit 10000 \
  --offset 0 \
  --order-by users:desc \
  --format csv \
  --output report.csv

ga4 reports save my-daily-report \
  --property-id 123456 \
  --metrics users,sessions \
  --start-date 2026-01-01 \
  --dimensions date \
  --schedule daily
```
- All ga4-cli capabilities
- Additional: Save reports, scheduling
- Better: Validation, error messages

---

### Metadata Operations

#### ga-cli
- Not supported
- Cannot explore available metrics/dimensions

#### ga4-cli
```
ga4 dimensions list --property-id 123456
ga4 metrics list --property-id 123456
```
- Basic: Just lists dimensions and metrics
- Limited: No search or filtering

#### Recommended Approach
```
ga4 metadata list dimensions --property-id 123456
  [--search "device" --filter "required=true"]

ga4 metadata list metrics --property-id 123456
  [--search "revenue" --filter "type=currency"]

ga4 metadata describe dimension country \
  --property-id 123456
  # Shows: description, type, allowed values, compatibility
```
- Better naming (metadata vs raw commands)
- Search within results
- Type filtering
- Detailed metadata descriptions

---

### Advanced Features Comparison

#### Dry-run Mode
- **ga-cli:** ✗ Not supported
- **ga4-cli:** ✗ Not supported
- **Recommended:** ✓ `--dry-run` flag for all write operations

```bash
ga4 properties create \
  --account-id 123456 \
  --name "Test Property" \
  --timezone "America/New_York" \
  --dry-run
# Shows: "Would create property with these settings..."
```

#### Batch Operations
- **ga-cli:** ✗ Not supported
- **ga4-cli:** ✗ Not supported
- **Recommended:** ✓ Batch CSV processing

```bash
ga4 properties create --batch properties.csv
# Properties.csv: account_id, name, timezone, currency
```

#### Property Cloning
- **ga-cli:** ✗ Not supported
- **ga4-cli:** ✗ Not supported
- **Recommended:** ✓ Clone with data stream and settings

```bash
ga4 properties clone \
  --property-id 123456 \
  --name "Clone of Property" \
  --account-id 789012
  # Copies settings, streams, goals, conversions
```

#### Error Recovery
- **ga-cli:** Basic error messages
- **ga4-cli:** Basic error messages
- **Recommended:** ✓ Helpful error messages with remediation

```
Error: Invalid property ID
→ Property ID must be numeric (got: "abc123")
→ Find your property ID: ga4 properties list --account-id 123456
→ Or check Google Analytics UI at analytics.google.com
```

---

## Implementation Priority

### Phase 1 (MVP - Parity with ga-cli)
```
✓ Service account auth
✓ Account management (list, get)
✓ Property CRUD operations
✓ Data stream management
✓ Table and JSON output
✓ Configuration management
```

### Phase 2 (Add ga4-cli features)
```
✓ OAuth2 authentication
✓ Direct token support
✓ Report execution (with filters)
✓ Real-time data queries
✓ Metadata browsing (dimensions/metrics)
✓ CSV export format
✓ Quiet mode for automation
```

### Phase 3 (Enhanced features)
```
✓ Dry-run mode
✓ Batch operations
✓ Property cloning
✓ Audience management
✓ Event management
✓ User property operations
✓ Report saving/scheduling
✓ Advanced metadata search
```

### Phase 4 (Polish & Distribution)
```
✓ Comprehensive error handling
✓ Input validation
✓ Progress indicators
✓ Interactive prompts
✓ Shell completion (bash, zsh)
✓ Detailed documentation
✓ Examples and tutorials
✓ PyPI distribution
```

---

## Key Differentiators vs. Competitors

| Differentiator | Value Proposition |
|---|---|
| **Complete Feature Set** | Do everything in one tool (admin + analytics) |
| **Flexible Auth** | Choose what works for your workflow |
| **Better Metadata** | Search and filter dimensions/metrics |
| **Safety First** | Dry-run mode prevents accidents |
| **Batch Operations** | Process multiple items efficiently |
| **Helpful Errors** | Know how to fix problems fast |
| **Pure Python** | Easy to contribute and maintain |
| **Production Ready** | Better error handling and edge cases |
| **Better Docs** | Real-world examples and workflows |
| **User Properties** | Missing in competitors |
| **Audiences** | Missing in competitors |
| **Events** | Missing in competitors |

