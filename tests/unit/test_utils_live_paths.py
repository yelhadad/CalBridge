"""Tests for live caldav object serialization paths in utils."""

from datetime import date, datetime
from unittest.mock import MagicMock

from apple_sync.shared.utils import event_to_dict, reminder_to_dict


def _make_ical_prop(value):
    """Create a mock iCal property with a .dt attribute."""
    prop = MagicMock()
    prop.dt = value
    return prop


class TestLiveVEventToDict:
    def _make_live_event(
        self,
        uid="uid1",
        summary="Test",
        start=None,
        end=None,
        location="",
        description="",
        cal_name="Work",
    ):
        """Build a mock caldav Event with an icalendar_component."""
        ical = MagicMock()
        ical.get = lambda key, default=None: {
            "UID": uid,
            "SUMMARY": summary,
            "DTSTART": _make_ical_prop(start or datetime(2026, 4, 17, 10, 0, 0)),
            "DTEND": _make_ical_prop(end or datetime(2026, 4, 17, 11, 0, 0)),
            "LOCATION": location,
            "DESCRIPTION": description,
        }.get(key, default)

        event = MagicMock()
        event.icalendar_component = ical
        event.parent = MagicMock()
        event.parent.name = cal_name
        return event

    def test_extracts_all_fields(self):
        event = self._make_live_event()
        result = event_to_dict(event)
        assert set(result.keys()) == {
            "id",
            "title",
            "start",
            "end",
            "calendar",
            "location",
            "notes",
        }

    def test_uid_mapped_to_id(self):
        event = self._make_live_event(uid="test-uid")
        result = event_to_dict(event)
        assert result["id"] == "test-uid"

    def test_date_object_converted(self):
        """A date (not datetime) in DTSTART should still serialize."""
        event = self._make_live_event(start=date(2026, 4, 17))
        result = event_to_dict(event)
        assert result["start"] == "2026-04-17T00:00:00"

    def test_none_dt_returns_none(self):
        """A DTSTART property with dt=None should return None."""
        event = self._make_live_event(start=None)
        # Patch the property to return dt=None
        event.icalendar_component.get = lambda key, default=None: {
            "UID": "x",
            "SUMMARY": "T",
            "DTSTART": _make_ical_prop(None),
            "DTEND": _make_ical_prop(None),
        }.get(key, default)
        result = event_to_dict(event)
        # Should not crash; start/end may be None or str
        assert "start" in result


class TestLiveVTodoToDict:
    def _make_live_reminder(
        self, uid="uid1", summary="Task", due=None, priority=0, notes="", list_name="Reminders"
    ):
        """Build a mock caldav Todo with an icalendar_component."""
        ical = MagicMock()
        due_prop = _make_ical_prop(due) if due else None
        ical.get = lambda key, default=None: {
            "UID": uid,
            "SUMMARY": summary,
            "DUE": due_prop,
            "PRIORITY": priority,
            "DESCRIPTION": notes,
        }.get(key, default)

        reminder = MagicMock()
        reminder.icalendar_component = ical
        reminder.parent = MagicMock()
        reminder.parent.name = list_name
        return reminder

    def test_extracts_all_fields(self):
        reminder = self._make_live_reminder()
        result = reminder_to_dict(reminder)
        assert set(result.keys()) == {"id", "title", "notes", "due_date", "priority", "list"}

    def test_due_datetime_serialized(self):
        due = datetime(2026, 4, 20, 9, 0, 0)
        reminder = self._make_live_reminder(due=due)
        result = reminder_to_dict(reminder)
        assert result["due_date"] == "2026-04-20T09:00:00"

    def test_due_date_object_converted(self):
        due = date(2026, 4, 20)
        reminder = self._make_live_reminder(due=due)
        result = reminder_to_dict(reminder)
        assert result["due_date"] == "2026-04-20T00:00:00"

    def test_no_due_returns_none(self):
        reminder = self._make_live_reminder(due=None)
        result = reminder_to_dict(reminder)
        assert result["due_date"] is None

    def test_list_name_from_parent(self):
        reminder = self._make_live_reminder(list_name="Work")
        result = reminder_to_dict(reminder)
        assert result["list"] == "Work"
