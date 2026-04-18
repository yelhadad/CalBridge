"""Unit tests for shared utility functions."""

from datetime import datetime

import pytest

from apple_sync.shared.utils import (
    event_to_dict,
    parse_date_range,
    reminder_to_dict,
    serialize_datetime,
)
from apple_sync.shared.validators import ValidationError
from apple_sync.integration.mock_store import MockVEvent, MockVTodo


class TestParseDateRange:
    def test_explicit_dates(self):
        start, end = parse_date_range("2026-04-17", "2026-04-17")
        assert start.year == 2026
        assert end.hour == 23

    def test_today_shorthand(self):
        start, end = parse_date_range("today", "today")
        assert start.hour == 0
        assert end.hour == 23

    def test_tomorrow_shorthand(self):
        start, end = parse_date_range("tomorrow", "tomorrow")
        assert start < end

    def test_yesterday_shorthand(self):
        start, end = parse_date_range("yesterday", "yesterday")
        assert start < end

    def test_mixed_shorthand_and_date(self):
        start, end = parse_date_range("today", "2026-12-31")
        assert start < end

    def test_end_before_start_raises(self):
        with pytest.raises(ValidationError):
            parse_date_range("2026-04-18", "2026-04-17")

    def test_invalid_start_raises(self):
        with pytest.raises(ValidationError):
            parse_date_range("bad-date", "2026-04-17")


class TestSerializeDatetime:
    def test_returns_iso_string(self):
        dt = datetime(2026, 4, 17, 10, 0, 0)
        assert serialize_datetime(dt) == "2026-04-17T10:00:00"

    def test_none_returns_none(self):
        assert serialize_datetime(None) is None


class TestEventToDict:
    def test_structure(self, sample_event):
        result = event_to_dict(sample_event)
        assert set(result.keys()) == {"id", "title", "start", "end", "calendar", "location", "notes"}

    def test_values(self, sample_event):
        result = event_to_dict(sample_event)
        assert result["title"] == "Test Event"
        assert result["calendar"] == "Work"
        assert result["start"] == "2026-04-17T10:00:00"

    def test_missing_calendar_returns_empty(self):
        evt = MockVEvent({"id": "x", "title": "T", "start": "2026-04-17T10:00:00",
                          "end": "2026-04-17T11:00:00"})
        result = event_to_dict(evt)
        assert isinstance(result["calendar"], str)


class TestReminderToDict:
    def test_structure(self, sample_reminder):
        result = reminder_to_dict(sample_reminder)
        assert set(result.keys()) == {"id", "title", "notes", "due_date", "priority", "list"}

    def test_values(self, sample_reminder):
        result = reminder_to_dict(sample_reminder)
        assert result["title"] == "Test Reminder"
        assert result["priority"] == 5
        assert result["list"] == "Work"

    def test_no_due_date(self):
        rem = MockVTodo({"id": "r1", "title": "T", "notes": "", "priority": 0, "list": "R"})
        result = reminder_to_dict(rem)
        assert result["due_date"] is None
