# Product Requirements Document (PRD)
## Apple Calendar & Reminders Headless Integration (OpenClaw Agent)
**Version:** 1.00 | **Date:** 2026-04-17 | **Author:** Senior AI Coding Agent

---

## 1. Project Overview

A headless, backend-only macOS application that provides programmatic read/write access to Apple Calendar (EventKit) and Reminders, exposed as a structured tool suite consumable by the OpenClaw AI agent.

---

## 2. ISO/IEC 25010 Quality Model Compliance

| Quality Characteristic | Sub-Characteristic | Implementation |
|---|---|---|
| Functional Suitability | Functional Completeness | All 3 tools: ReadCalendar, CreateEvent, CreateReminder |
| Functional Suitability | Functional Correctness | TDD Red-Green-Refactor, 85%+ branch coverage |
| Performance Efficiency | Time Behaviour | Async EventKit calls, response SLA <2s |
| Compatibility | Interoperability | JSON-RPC style responses, strict JSON schemas |
| Usability | Learnability | README with agent-parseable tool schemas |
| Reliability | Fault Tolerance | Graceful degradation on permission denial, offline state |
| Security | Confidentiality | No credentials in code; .env-example for secrets |
| Maintainability | Modularity | Max 150 LOC per file; DRY mixins; relative imports |
| Maintainability | Testability | 85%+ branch coverage, XML/JSON coverage reports |
| Portability | Adaptability | macOS 12+, Python 3.11+, uv environment |

---

## 3. Stakeholders

- **Primary Consumer:** OpenClaw AI Agent (machine-to-machine)
- **Developer:** Senior Software Engineer (Yo'ave)
- **Platform:** macOS (EventKit via PyObjC bridge)

---

## 4. Functional Requirements

### FR-01: Read Calendar Events
- Query events by date range (today, tomorrow, yesterday, custom range)
- Return structured JSON: `[{id, title, start, end, calendar, location, notes}]`
- Support filtering by calendar name

### FR-02: Create Calendar Event
- Required: title, start_datetime, end_datetime
- Optional: calendar_name, location, notes, url
- Return: `{id, title, start, end, calendar}` on success

### FR-03: Create Reminder
- Required: title
- Optional: notes, due_date (ISO 8601), priority (0-9), list_name
- Return: `{id, title, due_date, priority, list}` on success

### FR-04: Permission Management
- Detect missing TCC permissions at startup
- Log actionable error with remediation steps (not GUI popup)
- Support mock mode for CI/CD (env var: `APPLE_SYNC_MOCK=true`)

---

## 5. Non-Functional Requirements

### NFR-01: Headless Operation
- ZERO GUI interaction. All flows must be fully automatable.
- Initial permission grant documented in README as one-time manual step.

### NFR-02: Stateless Execution
- Each OpenClaw invocation is independent. No persistent in-memory state.

### NFR-03: Structured Logging
- JSON-format logs via `logging_config.json`.
- Log every agent request and permission denial.

### NFR-04: Code Quality
- Ruff linting: ZERO violations.
- Max 150 LOC per file.
- Relative imports within `src/apple_sync/`.
- All functions/classes have docstrings.

### NFR-05: Test Coverage
- pytest-cov enforcing 85% branch coverage.
- Machine-readable: `coverage.xml` + `coverage.json`.

---

## 6. System Boundaries

**In Scope:**
- macOS EventKit via PyObjC (EventKit framework)
- OpenClaw tool schema definitions
- CLI entry point for direct invocation

**Out of Scope:**
- iCloud sync (relies on system-level sync, not addressed)
- GUI / front-end
- Cross-platform support (macOS only)

---

## 7. Constraints

- Python 3.11+ only
- `uv` environment manager exclusively
- PyObjC for EventKit bridge
- macOS 12+ (Monterey) minimum
