# TODO Checklist — Extreme Granularity
## Apple Calendar & Reminders Headless Integration
**Version:** 1.00

---

## PHASE 1: Project Scaffolding
- [x] Create directory tree: src/apple_sync/{sdk,agent,integration,shared}, tests/{unit,integration}, docs/, config/
- [x] Write docs/PRD.md (ISO 25010, functional requirements, non-functional requirements)
- [x] Write docs/PLAN.md (C4 model, ADRs including permissions + mock strategy)
- [x] Write docs/PRD_apple_integration.md (EventKit permissions, TCC, CI/CD mock)
- [x] Write docs/TODO.md (this file)
- [ ] Write docs/PROMPTS_AND_COSTS.md
- [ ] Circular validation: cross-reference TODO vs PRD (docs/CIRCULAR_VALIDATION.md)

## PHASE 2: Configuration Files
- [ ] Write pyproject.toml (uv config, dependencies, ruff rules, pytest-cov 85% enforcement)
- [ ] Write config/logging_config.json (JSON structured logging, version: 1.00)
- [ ] Write config/setup.json (app metadata, version: 1.00)
- [ ] Write config/rate_limits.json (version: 1.00, EventKit rate limits)
- [ ] Write .env-example (APPLE_SYNC_MOCK, MOCK_PERMISSION_STATE)

## PHASE 3: Shared Layer (src/apple_sync/shared/)
- [ ] Write shared/version.py (VERSION = "1.00")
- [ ] Write shared/constants.py (DATE_FORMAT, ERROR_CODES, PRIORITY_RANGE, DEFAULT_CALENDAR)
- [ ] Write shared/validators.py
  - [ ] class InputValidator
    - [ ] validate_date_string(date_str) → raises ValidationError
    - [ ] validate_datetime_string(dt_str) → raises ValidationError
    - [ ] validate_priority(priority) → raises ValidationError (0–9)
    - [ ] validate_non_empty_string(value, field_name) → raises ValidationError
  - [ ] class ValidationError(Exception) — custom error with field + message
- [ ] Write shared/utils.py
  - [ ] parse_date_range(start, end) → (datetime, datetime)
  - [ ] event_to_dict(ek_event) → dict
  - [ ] reminder_to_dict(ek_reminder) → dict
  - [ ] serialize_datetime(dt) → ISO 8601 string

## PHASE 4: Integration Layer (src/apple_sync/integration/)
- [ ] Write integration/base.py
  - [ ] class BaseIntegration (abstract)
    - [ ] __init__(mock_mode: bool)
    - [ ] _get_store() → EKEventStore | MockEventStore
    - [ ] _check_permission(entity_type) → None (raises on failure)
- [ ] Write integration/permission_manager.py
  - [ ] class PermissionDeniedError(Exception)
  - [ ] class PermissionRestrictedError(Exception)
  - [ ] class PermissionManager
    - [ ] check_calendar_permission() → None
    - [ ] check_reminder_permission() → None
    - [ ] _request_access(entity_type) → bool (async bridged to sync)
    - [ ] _log_remediation(entity_type) → None
- [ ] Write integration/mock_store.py
  - [ ] class MockEventStore
    - [ ] __init__() — loads fixtures from tests/fixtures/
    - [ ] calendars(for_entity_type) → [MockCalendar]
    - [ ] predicateForEvents(withStart, end, calendars) → MockPredicate
    - [ ] events(matching_predicate) → [MockEvent]
    - [ ] save(event, span, commit, error) → bool
    - [ ] defaultCalendarForNewEvents → MockCalendar
    - [ ] defaultCalendarForNewReminders → MockList
    - [ ] save(reminder, commit, error) → bool
- [ ] Write integration/calendar_reader.py
  - [ ] class CalendarReader(BaseIntegration)
    - [ ] read_events(start_date, end_date, calendar_name=None) → list[dict]
    - [ ] _build_predicate(store, start, end, calendars) → predicate
    - [ ] _filter_by_calendar(events, calendar_name) → list
- [ ] Write integration/calendar_writer.py
  - [ ] class CalendarWriter(BaseIntegration)
    - [ ] create_event(title, start_dt, end_dt, calendar_name=None, **kwargs) → dict
    - [ ] _get_target_calendar(store, name) → EKCalendar
    - [ ] _build_event(store, title, start, end, calendar, **kwargs) → EKEvent
- [ ] Write integration/reminder_writer.py
  - [ ] class ReminderWriter(BaseIntegration)
    - [ ] create_reminder(title, notes=None, due_date=None, priority=0, list_name=None) → dict
    - [ ] _get_target_list(store, name) → EKCalendar (reminder list)
    - [ ] _build_reminder(store, title, notes, due_date, priority, list_obj) → EKReminder

## PHASE 5: SDK Layer (src/apple_sync/sdk/)
- [ ] Write sdk/calendar_sdk.py
  - [ ] class CalendarSDK
    - [ ] __init__(mock_mode: bool = False)
    - [ ] read_events(start_date, end_date, calendar_name=None) → list[dict]
    - [ ] create_event(title, start_datetime, end_datetime, **kwargs) → dict
- [ ] Write sdk/reminder_sdk.py
  - [ ] class ReminderSDK
    - [ ] __init__(mock_mode: bool = False)
    - [ ] create_reminder(title, **kwargs) → dict

## PHASE 6: Agent Layer (src/apple_sync/agent/)
- [ ] Write agent/tools.py
  - [ ] READ_CALENDAR_TOOL_SCHEMA (JSON schema dict)
  - [ ] CREATE_EVENT_TOOL_SCHEMA (JSON schema dict)
  - [ ] CREATE_REMINDER_TOOL_SCHEMA (JSON schema dict)
  - [ ] ALL_TOOLS list
- [ ] Write agent/responses.py
  - [ ] success_response(data: dict) → dict
  - [ ] error_response(code: str, message: str, remediation: str = "") → dict
- [ ] Write agent/cli.py (Click CLI)
  - [ ] @cli group
  - [ ] @cli.command read-events (--start, --end, --calendar, --output-json)
  - [ ] @cli.command create-event (--title, --start, --end, --calendar, --location, --notes)
  - [ ] @cli.command create-reminder (--title, --notes, --due-date, --priority, --list)
  - [ ] @cli.command list-tools (prints ALL_TOOLS as JSON)

## PHASE 7: Package Init
- [ ] Write src/apple_sync/__init__.py (__all__, __version__, top-level imports)
- [ ] Write src/apple_sync/sdk/__init__.py
- [ ] Write src/apple_sync/agent/__init__.py
- [ ] Write src/apple_sync/integration/__init__.py
- [ ] Write src/apple_sync/shared/__init__.py

## PHASE 8: Test Fixtures
- [ ] Write tests/fixtures/mock_events.json (5+ sample events)
- [ ] Write tests/fixtures/mock_reminders.json (3+ sample reminders)
- [ ] Write tests/conftest.py (shared fixtures: mock_store, mock_mode_env, sample_events)

## PHASE 9: Unit Tests (TDD — tests written FIRST)
- [ ] tests/unit/test_validators.py
  - [ ] test_validate_date_string_valid
  - [ ] test_validate_date_string_invalid
  - [ ] test_validate_datetime_string_valid
  - [ ] test_validate_datetime_string_invalid
  - [ ] test_validate_priority_valid_range
  - [ ] test_validate_priority_out_of_range
  - [ ] test_validate_non_empty_string_valid
  - [ ] test_validate_non_empty_string_empty
- [ ] tests/unit/test_utils.py
  - [ ] test_parse_date_range_valid
  - [ ] test_parse_date_range_today_shorthand
  - [ ] test_parse_date_range_tomorrow_shorthand
  - [ ] test_serialize_datetime_iso8601
  - [ ] test_event_to_dict_structure
  - [ ] test_reminder_to_dict_structure
- [ ] tests/unit/test_permission_manager.py
  - [ ] test_check_calendar_permission_authorized (mock)
  - [ ] test_check_calendar_permission_denied_raises
  - [ ] test_check_reminder_permission_authorized
  - [ ] test_check_reminder_permission_denied_raises
  - [ ] test_remediation_logged_on_denial
- [ ] tests/unit/test_calendar_reader.py
  - [ ] test_read_events_returns_list (mock mode)
  - [ ] test_read_events_today (mock mode)
  - [ ] test_read_events_date_range (mock mode)
  - [ ] test_read_events_filter_by_calendar (mock mode)
  - [ ] test_read_events_empty_result (mock mode)
- [ ] tests/unit/test_calendar_writer.py
  - [ ] test_create_event_success (mock mode)
  - [ ] test_create_event_returns_dict (mock mode)
  - [ ] test_create_event_custom_calendar (mock mode)
  - [ ] test_create_event_invalid_title_raises
  - [ ] test_create_event_invalid_dates_raises
- [ ] tests/unit/test_reminder_writer.py
  - [ ] test_create_reminder_success (mock mode)
  - [ ] test_create_reminder_with_due_date (mock mode)
  - [ ] test_create_reminder_invalid_priority_raises
  - [ ] test_create_reminder_no_title_raises
- [ ] tests/unit/test_calendar_sdk.py
  - [ ] test_sdk_read_events_delegates_to_reader
  - [ ] test_sdk_create_event_delegates_to_writer
- [ ] tests/unit/test_reminder_sdk.py
  - [ ] test_sdk_create_reminder_delegates_to_writer
- [ ] tests/unit/test_responses.py
  - [ ] test_success_response_structure
  - [ ] test_error_response_structure
  - [ ] test_error_response_includes_remediation
- [ ] tests/unit/test_tools.py
  - [ ] test_read_calendar_schema_valid_json
  - [ ] test_create_event_schema_valid_json
  - [ ] test_create_reminder_schema_valid_json
  - [ ] test_all_tools_list_length

## PHASE 10: Integration Tests
- [ ] tests/integration/test_cli.py (Click test runner)
  - [ ] test_cli_read_events_json_output
  - [ ] test_cli_create_event_json_output
  - [ ] test_cli_create_reminder_json_output
  - [ ] test_cli_list_tools_output
  - [ ] test_cli_permission_denied_error_output

## PHASE 11: README
- [ ] Write README.md with machine-readable requirement mapping section

## PHASE 12: PROMPTS_AND_COSTS.md + Circular Validation
- [ ] Write docs/PROMPTS_AND_COSTS.md
- [ ] Write docs/CIRCULAR_VALIDATION.md
