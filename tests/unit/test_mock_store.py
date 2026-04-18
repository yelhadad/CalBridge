"""Unit tests for MockCalDAVStore fixture loading and behavior."""

from apple_sync.integration.mock_store import MockCalDAVStore, MockCalendar, MockVEvent, MockVTodo


class TestMockCalDAVStore:
    def test_loads_event_calendars(self, mock_store):
        cals = mock_store.calendars(supports_todos=False)
        assert len(cals) >= 1

    def test_loads_reminder_lists(self, mock_store):
        cals = mock_store.calendars(supports_todos=True)
        assert len(cals) >= 1

    def test_default_event_calendar(self, mock_store):
        cal = mock_store.default_event_calendar()
        assert cal is not None
        assert hasattr(cal, "name")

    def test_default_reminder_list(self, mock_store):
        cal = mock_store.default_reminder_list()
        assert cal is not None

    def test_default_event_calendar_creates_if_empty(self):
        """When no event calendars exist, a new one is created."""
        store = MockCalDAVStore()
        store._calendars = []
        cal = store.default_event_calendar()
        assert cal.name == "Calendar"

    def test_default_reminder_list_creates_if_empty(self):
        """When no reminder lists exist, a new one is created."""
        store = MockCalDAVStore()
        store._calendars = []
        cal = store.default_reminder_list()
        assert cal.name == "Reminders"


class TestMockCalendar:
    def test_date_search_filters_by_range(self):
        from datetime import datetime

        cal = MockCalendar("Test")
        cal._events = [
            MockVEvent(
                {
                    "id": "1",
                    "title": "In range",
                    "start": "2026-04-17T10:00:00",
                    "end": "2026-04-17T11:00:00",
                    "calendar": "Test",
                }
            ),
            MockVEvent(
                {
                    "id": "2",
                    "title": "Out of range",
                    "start": "2026-04-20T10:00:00",
                    "end": "2026-04-20T11:00:00",
                    "calendar": "Test",
                }
            ),
        ]
        start = datetime(2026, 4, 17, 0, 0, 0)
        end = datetime(2026, 4, 17, 23, 59, 59)
        results = cal.date_search(start, end)
        assert len(results) == 1
        assert results[0].title == "In range"

    def test_save_event_appends(self):
        cal = MockCalendar("Test")
        ical = (
            "BEGIN:VCALENDAR\nVERSION:2.0\n"
            "BEGIN:VEVENT\nUID:abc\nSUMMARY:Test\n"
            "DTSTART:20260417T100000\nDTEND:20260417T110000\n"
            "END:VEVENT\nEND:VCALENDAR"
        )
        result = cal.save_event(ical)
        assert result.title == "Test"
        assert len(cal._events) == 1

    def test_save_todo_appends(self):
        cal = MockCalendar("Work", supports_todos=True)
        ical = (
            "BEGIN:VCALENDAR\nVERSION:2.0\n"
            "BEGIN:VTODO\nUID:rem1\nSUMMARY:Buy milk\nPRIORITY:5\n"
            "END:VTODO\nEND:VCALENDAR"
        )
        result = cal.save_todo(ical)
        assert result.title == "Buy milk"
        assert result.priority == 5


class TestMockVEvent:
    def test_no_start_end(self):
        evt = MockVEvent({"id": "x", "title": "T"})
        assert evt.start_dt is None
        assert evt.end_dt is None


class TestMockVTodo:
    def test_no_due_date(self):
        todo = MockVTodo({"id": "x", "title": "T", "priority": 0, "list": "R"})
        assert todo.due_date is None
