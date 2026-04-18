"""Cover live CalDAV code paths using mocked principals."""

from unittest.mock import MagicMock, patch

import pytest

from apple_sync.integration.calendar_writer import CalendarWriter
from apple_sync.integration.reminder_writer import ReminderWriter


def _mock_calendar(name="Work", supports_todos=False):
    cal = MagicMock()
    cal.name = name
    cal.get_display_name.return_value = name
    cal.get_properties.return_value = {}
    saved = []
    cal.save_event.side_effect = lambda ical: _parse_mock_event(ical, name, saved)
    cal.save_todo.side_effect = lambda ical: _parse_mock_todo(ical, name, saved)
    return cal


def _parse_mock_event(ical, cal_name, saved):
    from apple_sync.integration.mock_store import MockVEvent
    evt = MockVEvent({"id": "live-1", "title": "T", "start": "2026-04-18T10:00:00",
                      "end": "2026-04-18T11:00:00", "calendar": cal_name})
    saved.append(evt)
    return evt


def _parse_mock_todo(ical, list_name, saved):
    from apple_sync.integration.mock_store import MockVTodo
    todo = MockVTodo({"id": "live-r1", "title": "T", "priority": 0, "list": list_name})
    saved.append(todo)
    return todo


class TestCalendarWriterLivePath:
    def _writer(self):
        w = CalendarWriter(mock_mode=False)
        return w

    def test_create_event_uses_named_calendar(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "false")
        monkeypatch.setenv("APPLE_ID", "u@icloud.com")
        monkeypatch.setenv("APPLE_APP_PASSWORD", "xxxx")

        work_cal = _mock_calendar("Work")
        mock_principal = MagicMock()
        mock_principal.calendars.return_value = [work_cal]

        with patch("caldav.DAVClient") as mock_cls:
            mock_cls.return_value.principal.return_value = mock_principal
            writer = self._writer()
            result = writer.create_event(
                "Meeting", "2026-04-18T10:00:00", "2026-04-18T11:00:00",
                calendar_name="Work",
            )
        assert result["title"] == "T"

    def test_create_event_falls_back_when_calendar_missing(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "false")
        monkeypatch.setenv("APPLE_ID", "u@icloud.com")
        monkeypatch.setenv("APPLE_APP_PASSWORD", "xxxx")

        default_cal = _mock_calendar("Calendar")
        mock_principal = MagicMock()
        mock_principal.calendars.return_value = [default_cal]

        with patch("caldav.DAVClient") as mock_cls:
            mock_cls.return_value.principal.return_value = mock_principal
            writer = self._writer()
            result = writer.create_event(
                "Meeting", "2026-04-18T10:00:00", "2026-04-18T11:00:00",
                calendar_name="NonExistent",
            )
        assert result["title"] == "T"


class TestReminderWriterLivePath:
    def _writer(self):
        return ReminderWriter(mock_mode=False)

    def _todo_cal(self, name="Reminders"):
        cal = _mock_calendar(name, supports_todos=True)
        # Make get_properties return VTODO support
        cal.get_properties.return_value = {
            "{urn:ietf:params:xml:ns:caldav}supported-calendar-component-set": "VTODO"
        }
        return cal

    def test_create_reminder_uses_named_list(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "false")
        monkeypatch.setenv("APPLE_ID", "u@icloud.com")
        monkeypatch.setenv("APPLE_APP_PASSWORD", "xxxx")

        work_list = self._todo_cal("Work")
        mock_principal = MagicMock()
        mock_principal.calendars.return_value = [work_list]

        with patch("caldav.DAVClient") as mock_cls:
            mock_cls.return_value.principal.return_value = mock_principal
            writer = self._writer()
            result = writer.create_reminder("Buy milk", list_name="Work")
        assert result["title"] == "T"

    def test_create_reminder_falls_back_when_list_missing(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "false")
        monkeypatch.setenv("APPLE_ID", "u@icloud.com")
        monkeypatch.setenv("APPLE_APP_PASSWORD", "xxxx")

        default_list = self._todo_cal("Reminders")
        mock_principal = MagicMock()
        mock_principal.calendars.return_value = [default_list]

        with patch("caldav.DAVClient") as mock_cls:
            mock_cls.return_value.principal.return_value = mock_principal
            writer = self._writer()
            result = writer.create_reminder("Buy milk", list_name="NonExistent")
        assert result["title"] == "T"

    def test_is_todo_calendar_true_when_vtodo_in_props(self):
        cal = MagicMock()
        cal.get_properties.return_value = {
            "{urn:ietf:params:xml:ns:caldav}supported-calendar-component-set": "VTODO"
        }
        assert ReminderWriter._is_todo_calendar(cal) is True

    def test_is_todo_calendar_false_on_exception(self):
        cal = MagicMock()
        cal.get_properties.side_effect = Exception("fail")
        assert ReminderWriter._is_todo_calendar(cal) is False

    def test_create_reminder_no_todo_cals_uses_first(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "false")
        monkeypatch.setenv("APPLE_ID", "u@icloud.com")
        monkeypatch.setenv("APPLE_APP_PASSWORD", "xxxx")

        any_cal = _mock_calendar("Calendar")
        mock_principal = MagicMock()
        mock_principal.calendars.return_value = [any_cal]

        with patch("caldav.DAVClient") as mock_cls:
            mock_cls.return_value.principal.return_value = mock_principal
            writer = self._writer()
            result = writer.create_reminder("Task")
        assert result["title"] == "T"
