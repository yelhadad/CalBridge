# Apple Integration PRD
## iCloud CalDAV API — Linux Headless Integration
**Version:** 1.00

---

## 1. Protocol: CalDAV over HTTPS

Apple exposes Calendar and Reminders via the **CalDAV** standard (RFC 4791) at:
- Base URL: `https://caldav.icloud.com`
- Principal discovery: `PROPFIND /.well-known/caldav`
- Calendar home: returned in PROPFIND response for authenticated user

All data is serialized as **iCalendar (RFC 5545)** format:
- Calendar events = `VEVENT` components
- Reminders = `VTODO` components

---

## 2. Authentication

### 2.1 Apple App-Specific Password (Required)
iCloud accounts with 2FA (mandatory for most users) cannot use the account password directly for CalDAV.

**One-time setup:**
1. Go to https://appleid.apple.com
2. Sign-In and Security → App-Specific Passwords
3. Click "+" → Label: "calbridge" → Generate
4. Copy the generated password into `APPLE_APP_PASSWORD` env var

### 2.2 Environment Variables
```
APPLE_ID=user@icloud.com
APPLE_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### 2.3 Credential Security
- Credentials stored only in environment variables
- `.env-example` provides template (never populate with real credentials)
- Logs MUST NOT include credentials

---

## 3. CalDAV Discovery Flow

```
Client startup
  └─► caldav.DAVClient(url="https://caldav.icloud.com", username=APPLE_ID, password=APPLE_APP_PASSWORD)
        └─► principal = client.principal()          # PROPFIND to discover user home
              └─► calendars = principal.calendars() # list all calendar/reminder collections
```

---

## 4. Reading Events (VEVENT)

```
CalendarReader.read_events(start, end, calendar_name=None)
  └─► Filter calendars to VEVENT-type (exclude VTODO-only lists)
  └─► calendar.date_search(start=start_dt, end=end_dt, expand=True)
  └─► Parse VEVENTs → list[dict]
```

---

## 5. Creating Events (VEVENT)

```
CalendarWriter.create_event(title, start_datetime, end_datetime, ...)
  └─► Find or use default VEVENT calendar
  └─► Build iCal VEVENT string (uid, dtstart, dtend, summary, ...)
  └─► calendar.save_event(ical_string)
  └─► Return serialized event dict
```

---

## 6. Creating Reminders (VTODO)

```
ReminderWriter.create_reminder(title, notes, due_date, priority, list_name)
  └─► Find or use default VTODO calendar (Reminders list)
  └─► Build iCal VTODO string (uid, summary, description, due, priority)
  └─► calendar.save_todo(ical_string)
  └─► Return serialized reminder dict
```

---

## 7. CI/CD Mock Strategy

All CI pipelines must set `APPLE_SYNC_MOCK=true`. `MockCalDAVStore` provides:
- Pre-seeded VEVENT objects from `tests/fixtures/mock_events.json`
- Pre-seeded VTODO objects from `tests/fixtures/mock_reminders.json`
- Simulates auth failure via `MOCK_AUTH_FAIL=true`

---

## 8. Error Handling

| Scenario | Error Code | Remediation |
|---|---|---|
| Wrong credentials | `AUTH_FAILED` | Check APPLE_ID and APPLE_APP_PASSWORD env vars |
| Network unreachable | `NETWORK_ERROR` | Check server connectivity to caldav.icloud.com |
| Calendar not found | `CALENDAR_NOT_FOUND` | List available calendars with list-tools |
| Validation failure | `VALIDATION_ERROR` | Check input format (dates: YYYY-MM-DDTHH:MM:SS) |
| Unknown error | `UNKNOWN_ERROR` | See logs for details |

---

## 9. Data Privacy

- No calendar data persisted by this application
- Credentials only in memory during request lifetime
- Logs include only metadata (counts, calendar names, timestamps) — no event content
