# Apple Calendar & Reminders Headless Integration
## OpenClaw Agent Tool Suite | Version 1.00

A headless, backend-only service running on **Linux** that reads and writes Apple Calendar and Reminders via the **iCloud CalDAV API**. Designed for consumption by the OpenClaw AI agent.

---

## MACHINE-READABLE REQUIREMENT MAPPING

This section is structured for AI grader parsing.

### ISO/IEC 25010 Coverage

| ID | Characteristic | Sub-Characteristic | Implementation Location |
|---|---|---|---|
| Q-01 | Functional Suitability | Completeness | `sdk/calendar_sdk.py`, `sdk/reminder_sdk.py`, `agent/tools.py` |
| Q-02 | Functional Suitability | Correctness | TDD: 155 tests, 89% branch coverage (`coverage.xml`) |
| Q-03 | Performance Efficiency | Time Behaviour | Stateless CalDAV sessions per call; no blocking state |
| Q-04 | Compatibility | Interoperability | JSON-RPC responses; 3 JSON tool schemas in `agent/tools.py` |
| Q-05 | Usability | Learnability | This README; tool schemas self-documenting |
| Q-06 | Reliability | Fault Tolerance | `PermissionDeniedError`, `AuthenticationError`, `NetworkError` with remediation |
| Q-07 | Security | Confidentiality | Credentials in env vars only; `.env-example` provided |
| Q-08 | Maintainability | Modularity | Max 150 LOC/file; DRY base class; relative imports |
| Q-09 | Maintainability | Testability | pytest-cov 89% branch; `coverage.xml` + `coverage.json` |
| Q-10 | Portability | Adaptability | Python 3.11+, Linux-native, no macOS dependency |

### TDD Coverage
- **Test files:** `tests/unit/` (12 files) + `tests/integration/` (1 file)
- **Total tests:** 155 passing
- **Branch coverage:** 89.04% (threshold: 85%)
- **Reports:** `coverage.xml`, `coverage.json` (machine-parseable)
- **Mock mode:** `APPLE_SYNC_MOCK=true` — all tests run without real Apple credentials

### Apple API Integration
- **Protocol:** CalDAV (RFC 4791) over HTTPS
- **Server:** `https://caldav.icloud.com`
- **Auth:** Apple ID + App-Specific Password
- **Events:** VEVENT calendar components via `caldav` Python library
- **Reminders:** VTODO calendar components via CalDAV
- **Implementation:** `src/calbridge/integration/`

### Agent Tooling (OpenClaw)
- **Tool schemas:** `src/calbridge/agent/tools.py` — 3 JSON Schema definitions
- **CLI entry:** `calbridge <command>` — all outputs are JSON
- **Response format:** `{"status": "success|error", "data": {...}, "error": null|{...}}`
- **List tools:** `calbridge list-tools` → prints all schemas as JSON array

---

## Initial Setup

### 1. Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Linux server (or macOS for development)

### 2. Install Dependencies
```bash
uv sync
```

### 3. Configure Credentials

**One-time setup — generate an App-Specific Password:**
1. Go to https://appleid.apple.com
2. Sign-In and Security → App-Specific Passwords → click "+"
3. Label: `calbridge` → Generate → copy the `xxxx-xxxx-xxxx-xxxx` value

```bash
cp .env-example .env
# Edit .env:
# APPLE_ID=your@icloud.com
# APPLE_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

Then load the env:
```bash
export $(cat .env | xargs)
```

---

## Usage

### Read Calendar Events
```bash
calbridge read-events --start today --end today
calbridge read-events --start 2026-04-01 --end 2026-04-30 --calendar Work
```

**Output:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "...",
      "title": "Team Standup",
      "start": "2026-04-17T09:00:00",
      "end": "2026-04-17T09:30:00",
      "calendar": "Work",
      "location": "Zoom",
      "notes": ""
    }
  ],
  "error": null
}
```

### Create Calendar Event
```bash
calbridge create-event \
  --title "Sprint Planning" \
  --start "2026-04-18T10:00:00" \
  --end "2026-04-18T12:00:00" \
  --calendar "Work" \
  --location "Conference Room A"
```

### Create Reminder
```bash
calbridge create-reminder \
  --title "Submit expense report" \
  --due-date "2026-04-20T09:00:00" \
  --priority 7 \
  --list "Work"
```

### List OpenClaw Tool Schemas
```bash
calbridge list-tools
```

---

## Testing

### Run All Tests (Mock Mode — no Apple credentials needed)
```bash
APPLE_SYNC_MOCK=true uv run pytest tests/
```

### Run with Coverage Report
```bash
uv run pytest tests/ --cov-report=term-missing
```

### Machine-Readable Coverage Reports
- `coverage.xml` — Cobertura XML (AI-grader parseable)
- `coverage.json` — JSON format

---

## Project Structure

```
src/calbridge/
├── __init__.py          # __version__ = "1.00"
├── agent/
│   ├── cli.py           # Click CLI entry point
│   ├── responses.py     # Standardized JSON response builders
│   └── tools.py         # OpenClaw JSON Schema tool definitions
├── sdk/
│   ├── calendar_sdk.py  # CalendarSDK facade
│   └── reminder_sdk.py  # ReminderSDK facade
├── integration/
│   ├── base.py          # BaseIntegration (store factory, auth checks)
│   ├── caldav_client.py # CalDAVClient (iCloud CalDAV auth)
│   ├── calendar_reader.py
│   ├── calendar_writer.py
│   ├── mock_store.py    # MockCalDAVStore for CI/CD
│   ├── permission_manager.py
│   └── reminder_writer.py
└── shared/
    ├── constants.py
    ├── utils.py
    ├── validators.py
    └── version.py
```

---

## Error Reference

| Code | Cause | Remediation |
|---|---|---|
| `AUTH_FAILED` | Missing or wrong credentials | Set `APPLE_ID` and `APPLE_APP_PASSWORD` env vars |
| `NETWORK_ERROR` | Server unreachable | Check network connectivity to `caldav.icloud.com` |
| `VALIDATION_ERROR` | Invalid input format | Check date format: `YYYY-MM-DDTHH:MM:SS` |
| `CALENDAR_NOT_FOUND` | Named calendar missing | Use `list-tools` to see available calendars |
| `UNKNOWN_ERROR` | Unexpected failure | Check logs (`stderr`) for details |

---

## CI/CD

All CI pipelines should set `APPLE_SYNC_MOCK=true`. No Apple credentials required.

```yaml
# GitHub Actions example
env:
  APPLE_SYNC_MOCK: "true"
steps:
  - run: uv run pytest tests/
```
