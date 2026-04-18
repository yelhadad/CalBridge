"""Mock CalDAV store for CI/CD and unit testing without Apple credentials."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

_FIXTURES = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures"


class MockVEvent:
    """Simulates a CalDAV VEVENT calendar object."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Populate from fixture dict."""
        self.id = data.get("id", str(uuid.uuid4()))
        self.title = data.get("title", "")
        self.location = data.get("location", "")
        self.notes = data.get("notes", "")
        self.calendar_name = data.get("calendar", DEFAULT_CALENDAR)

        start_str = data.get("start", "")
        end_str = data.get("end", "")
        self.start_dt: datetime | None = datetime.fromisoformat(start_str) if start_str else None
        self.end_dt: datetime | None = datetime.fromisoformat(end_str) if end_str else None


class MockVTodo:
    """Simulates a CalDAV VTODO (reminder) calendar object."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Populate from fixture dict."""
        self.id = data.get("id", str(uuid.uuid4()))
        self.title = data.get("title", "")
        self.notes = data.get("notes", "")
        self.priority = data.get("priority", 0)
        self.list_name = data.get("list", DEFAULT_REMINDER_LIST)

        due = data.get("due_date")
        self.due_date: datetime | None = datetime.fromisoformat(due) if due else None


class MockCalendar:
    """Simulates a CalDAV calendar collection."""

    def __init__(self, name: str, supports_todos: bool = False) -> None:
        """Initialize with calendar name and component type."""
        self.name = name
        self._supports_todos = supports_todos
        self._events: list[MockVEvent] = []
        self._todos: list[MockVTodo] = []

    def date_search(
        self, start: datetime, end: datetime, expand: bool = True
    ) -> list[MockVEvent]:
        """Return events within the date range."""
        return [
            e for e in self._events
            if e.start_dt and start <= e.start_dt <= end
        ]

    def save_event(self, ical_string: str) -> MockVEvent:
        """Parse ical string and append a new MockVEvent."""
        evt = self._parse_vevent(ical_string)
        self._events.append(evt)
        return evt

    def save_todo(self, ical_string: str) -> MockVTodo:
        """Parse ical string and append a new MockVTodo."""
        todo = self._parse_vtodo(ical_string)
        self._todos.append(todo)
        return todo

    def _parse_vevent(self, ical: str) -> MockVEvent:
        """Extract key fields from an iCal VEVENT string."""
        lines = {
            k.strip(): v.strip()
            for line in ical.splitlines()
            if ":" in line
            for k, v in [line.split(":", 1)]
        }
        return MockVEvent({
            "id": lines.get("UID", str(uuid.uuid4())),
            "title": lines.get("SUMMARY", ""),
            "start": lines.get("DTSTART", ""),
            "end": lines.get("DTEND", ""),
            "location": lines.get("LOCATION", ""),
            "notes": lines.get("DESCRIPTION", ""),
            "calendar": self.name,
        })

    def _parse_vtodo(self, ical: str) -> MockVTodo:
        """Extract key fields from an iCal VTODO string."""
        lines = {
            k.strip(): v.strip()
            for line in ical.splitlines()
            if ":" in line
            for k, v in [line.split(":", 1)]
        }
        priority_str = lines.get("PRIORITY", "0")
        try:
            priority = int(priority_str)
        except ValueError:
            priority = 0
        return MockVTodo({
            "id": lines.get("UID", str(uuid.uuid4())),
            "title": lines.get("SUMMARY", ""),
            "notes": lines.get("DESCRIPTION", ""),
            "due_date": lines.get("DUE", None),
            "priority": priority,
            "list": self.name,
        })


# Import constants after class definitions to avoid circular issues
from ..shared.constants import DEFAULT_CALENDAR, DEFAULT_REMINDER_LIST  # noqa: E402


class MockCalDAVStore:
    """Drop-in replacement for the live CalDAV client in mock/CI mode."""

    def __init__(self) -> None:
        """Load fixture data and initialize mock calendars."""
        self._calendars = self._build_calendars()

    def _build_calendars(self) -> list[MockCalendar]:
        """Build mock calendar objects seeded from fixture files."""
        events = self._load_json(_FIXTURES / "mock_events.json")
        reminders = self._load_json(_FIXTURES / "mock_reminders.json")

        cal_map: dict[str, MockCalendar] = {}

        for evt_data in events:
            name = evt_data.get("calendar", DEFAULT_CALENDAR)
            if name not in cal_map:
                cal_map[name] = MockCalendar(name, supports_todos=False)
            cal_map[name]._events.append(MockVEvent(evt_data))

        for rem_data in reminders:
            name = rem_data.get("list", DEFAULT_REMINDER_LIST)
            key = f"todo:{name}"
            if key not in cal_map:
                cal_map[key] = MockCalendar(name, supports_todos=True)
            cal_map[key]._todos.append(MockVTodo(rem_data))

        return list(cal_map.values())

    @staticmethod
    def _load_json(path: Path) -> list[dict]:
        """Load a JSON fixture file; return empty list if missing."""
        if not path.exists():
            return []
        with path.open() as f:
            return json.load(f)

    def calendars(self, supports_todos: bool = False) -> list[MockCalendar]:
        """Return calendars filtered by component type."""
        return [c for c in self._calendars if c._supports_todos == supports_todos]

    def default_event_calendar(self) -> MockCalendar:
        """Return the first VEVENT calendar or create one."""
        event_cals = self.calendars(supports_todos=False)
        if event_cals:
            return event_cals[0]
        cal = MockCalendar(DEFAULT_CALENDAR)
        self._calendars.append(cal)
        return cal

    def default_reminder_list(self) -> MockCalendar:
        """Return the first VTODO calendar or create one."""
        todo_cals = self.calendars(supports_todos=True)
        if todo_cals:
            return todo_cals[0]
        cal = MockCalendar(DEFAULT_REMINDER_LIST, supports_todos=True)
        self._calendars.append(cal)
        return cal
