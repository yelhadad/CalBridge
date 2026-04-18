# Architecture & Design Plan
## Apple Calendar & Reminders Headless Integration (Linux + CalDAV)
**Version:** 1.00 | **C4 Model + ADRs**

---

## C4 Level 1: System Context

```
[OpenClaw Agent] --JSON params--> [calbridge SDK] --CalDAV/HTTPS--> [Apple iCloud CalDAV Server]
```

Runs on: **Linux server** (Python 3.11+, no macOS dependency)

---

## C4 Level 2: Container Diagram

```
calbridge/
├── agent/          CLI + JSON-RPC wrappers (entry points for OpenClaw)
├── sdk/            Business logic orchestration (facade over integration/)
├── integration/    Apple iCloud CalDAV client (reader, writer, auth)
└── shared/         Cross-cutting: constants, version, utils, validators
```

---

## C4 Level 3: Component Diagram

### agent/
- `tools.py` — Tool schema definitions (JSON Schema objects)
- `cli.py` — Click CLI entry point; routes commands to sdk/
- `responses.py` — Standard success/error response builders

### sdk/
- `calendar_sdk.py` — `CalendarSDK`: facade with `read_events()`, `create_event()`
- `reminder_sdk.py` — `ReminderSDK`: facade with `create_reminder()`

### integration/
- `base.py` — `BaseIntegration`: CalDAV client factory, mock mode detection
- `caldav_client.py` — `CalDAVClient`: authenticated session to iCloud CalDAV
- `calendar_reader.py` — `CalendarReader`: VEVENT query over date range
- `calendar_writer.py` — `CalendarWriter`: VEVENT creation via CalDAV PUT
- `reminder_writer.py` — `ReminderWriter`: VTODO creation via CalDAV PUT
- `mock_store.py` — `MockCalDAVStore`: fixture-based mock for CI/CD

### shared/
- `version.py` — `VERSION = "1.00"`
- `constants.py` — iCloud CalDAV URL, date formats, error codes
- `validators.py` — Input validation (dates, strings, priority range)
- `utils.py` — Date parsing helpers, iCal→dict serialization

---

## Architecture Decision Records (ADRs)

### ADR-001: CalDAV over PyObjC
**Decision:** Use the `caldav` Python library to connect to Apple iCloud CalDAV.
**Rationale:** App runs on Linux; PyObjC is macOS-only. CalDAV is the standard protocol Apple exposes for Calendar and Reminders on any platform.
**Consequences:** Requires Apple App-Specific Password; network access to `caldav.icloud.com`.

### ADR-002: Apple Authentication (App-Specific Password)
**Decision:** Use Apple ID + App-Specific Password for CalDAV auth.
**Rationale:** iCloud requires 2FA. App-Specific Passwords bypass 2FA for third-party CalDAV clients.
**Setup:** User generates password at https://appleid.apple.com → Sign-In and Security → App-Specific Passwords.
**Credentials:** Stored in environment variables `APPLE_ID` and `APPLE_APP_PASSWORD`. Never in code.

### ADR-003: Mock Mode for CI/CD
**Decision:** Env var `APPLE_SYNC_MOCK=true` activates `MockCalDAVStore` replacing all network calls.
**Rationale:** CI runners have no Apple credentials. Mock provides deterministic fixture data.
**Implementation:** `BaseIntegration._get_client()` returns `MockCalDAVStore` when mock flag set.

### ADR-004: iCloud CalDAV Discovery
**Decision:** Use CalDAV well-known URL discovery (`https://caldav.icloud.com`) rather than hardcoding principal paths.
**Rationale:** iCloud user home paths vary per account. `caldav` library handles PROPFIND discovery automatically.

### ADR-005: Reminders as VTODO
**Decision:** Apple Reminders are accessed via CalDAV as `VTODO` components in reminder list calendars.
**Rationale:** Apple exposes both Calendar (VEVENT) and Reminders (VTODO) through the same CalDAV endpoint.

### ADR-006: Stateless Execution
**Decision:** Each SDK call opens a fresh CalDAV session. No persistent connection pool.
**Rationale:** OpenClaw invocations are independent. Stateless = no race conditions.

### ADR-007: Response Format
**Decision:** All agent-layer responses: `{"status": "success|error", "data": {...}, "error": null|{...}}`.
**Rationale:** Machine-parseable by OpenClaw.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Platform | Linux server |
| Env Manager | uv |
| CalDAV Client | caldav (PyPI) |
| iCal Parsing | icalendar (transitive via caldav) |
| CLI | Click |
| Linting | Ruff |
| Testing | pytest + pytest-cov |
| Logging | Python logging + JSON config |
| Serialization | stdlib json + dataclasses |

---

## iCloud CalDAV Endpoints

| Resource | URL |
|---|---|
| Base | `https://caldav.icloud.com` |
| Principal | Auto-discovered via PROPFIND |
| Calendars | Listed under user principal |
| Reminders | CalDAV calendars of type `VTODO` |
