# GA4 CLI Commands - Comparative Reference Guide

## Quick Command Map

### Authentication

#### ga-cli (Python)
```bash
ga-cli config init
ga-cli config show
```

#### ga4-cli (TypeScript)
```bash
ga4 auth login
ga4 auth status
ga4 auth logout
```

#### Recommended (Your Tool)
```bash
ga4 auth init
ga4 auth login
ga4 auth status
ga4 auth logout
ga4 auth switch ACCOUNT_ID
ga4 config show
ga4 config set KEY VALUE
```

---

### Account Operations

#### ga-cli (Python)
```bash
ga-cli accounts list
ga-cli accounts get ACCOUNT_ID
```

#### ga4-cli (TypeScript)
NOT SUPPORTED

#### Recommended (Your Tool)
```bash
ga4 accounts list
ga4 accounts list --format json
ga4 accounts get ACCOUNT_ID
```

---

### Properties Management

#### ga-cli (Python)
```bash
ga-cli properties list ACCOUNT_ID
ga-cli properties get PROPERTY_ID
ga-cli properties create ACCOUNT_ID --name "Name" --timezone TZ --currency USD
ga-cli properties delete PROPERTY_ID
```

#### ga4-cli (TypeScript)
```bash
ga4 properties list
ga4 properties get PROPERTY_ID
```

#### Recommended (Your Tool)
```bash
ga4 properties list ACCOUNT_ID
ga4 properties get PROPERTY_ID
ga4 properties create ACCOUNT_ID --name "Name" --timezone TZ --currency USD
ga4 properties update PROPERTY_ID --timezone TZ
ga4 properties delete PROPERTY_ID
ga4 properties clone PROPERTY_ID --name "Clone" --account-id DEST_ACCOUNT
```

---

### Data Streams Management

#### ga-cli (Python)
```bash
ga-cli datastreams list PROPERTY_ID
ga-cli datastreams get PROPERTY_ID STREAM_ID
ga-cli datastreams create PROPERTY_ID --name "Stream" --url "https://example.com"
```

#### ga4-cli (TypeScript)
NOT SUPPORTED

#### Recommended (Your Tool)
```bash
ga4 datastreams list PROPERTY_ID
ga4 datastreams get PROPERTY_ID STREAM_ID
ga4 datastreams create PROPERTY_ID --type web --name "Stream" --url "https://example.com"
ga4 datastreams delete PROPERTY_ID STREAM_ID
```

---

### Reports

#### ga-cli (Python)
NOT SUPPORTED

#### ga4-cli (TypeScript)
```bash
ga4 reports run --property-id ID --metrics users,sessions --start-date 2026-01-01
```

#### Recommended (Your Tool)
```bash
ga4 reports run --property-id ID --metrics users,sessions --start-date 2026-01-01 --end-date 2026-03-14
ga4 reports run --property-id ID --metrics users --dimensions date,country --format csv
ga4 reports save daily-summary --property-id ID --metrics users
ga4 reports list --property-id ID
```

---

### Real-time Data

#### ga-cli (Python)
NOT SUPPORTED

#### ga4-cli (TypeScript)
```bash
ga4 realtime run --property-id ID
```

#### Recommended (Your Tool)
```bash
ga4 realtime run --property-id ID
ga4 realtime run --property-id ID --dimensions country,source
```

---

### Metadata Operations

#### ga-cli (Python)
NOT SUPPORTED

#### ga4-cli (TypeScript)
```bash
ga4 dimensions list --property-id ID
ga4 metrics list --property-id ID
```

#### Recommended (Your Tool)
```bash
ga4 metadata list dimensions --property-id ID
ga4 metadata list metrics --property-id ID
ga4 metadata list dimensions --property-id ID --search "device"
ga4 metadata describe dimension country --property-id ID
```

---

### Events Management

#### NOT IN COMPETITORS

#### Recommended (Your Tool)
```bash
ga4 events list --property-id ID
ga4 events get --property-id ID --event-name purchase
ga4 events create --property-id ID --event-name custom --description "Custom event"
ga4 events delete --property-id ID --event-name old_event
```

---

### Audience Management

#### NOT IN COMPETITORS

#### Recommended (Your Tool)
```bash
ga4 audiences list --property-id ID
ga4 audiences get --property-id ID --audience-id AUDIENCE_ID
ga4 audiences create --property-id ID --name "High-Value" --definition "sessions_value > 100"
ga4 audiences delete --property-id ID --audience-id AUDIENCE_ID
```

---

## Global Flags

### All Commands Support
```bash
--format TABLE|JSON|CSV          Output format
--output FILE                    Save output to file
--quiet                          Suppress non-essential output
--verbose                        Detailed output
--no-color                       Disable colored output
--help                           Show help
```

### Write Operation Flags
```bash
--dry-run                        Preview without executing
--force                          Skip confirmation
```

---

## Feature Availability Summary

| Feature | ga-cli | ga4-cli | Your Tool |
|---------|--------|---------|-----------|
| Account management | Yes | No | Yes |
| Property CRUD | Yes | Partial | Yes |
| Data streams | Yes | No | Yes |
| Reports | No | Yes | Yes |
| Real-time | No | Yes | Yes |
| Metadata | No | Yes | Yes |
| Events | No | No | Yes |
| Audiences | No | No | Yes |
| Batch ops | No | No | Yes |
| Dry-run | No | No | Yes |
| OAuth2 | No | Yes | Yes |
| CSV export | No | Yes | Yes |

