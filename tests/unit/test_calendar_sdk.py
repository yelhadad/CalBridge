"""Unit tests for CalendarSDK facade."""

from unittest.mock import patch

import pytest

from calbridge.sdk.calendar_sdk import CalendarSDK


@pytest.fixture()
def sdk():
    return CalendarSDK(mock_mode=True)


class TestCalendarSDK:
    def test_read_events_delegates_to_reader(self, sdk):
        with patch.object(sdk._reader, "read_events", return_value=[]) as mock_read:
            sdk.read_events("today", "today")
            mock_read.assert_called_once_with("today", "today", None)

    def test_read_events_with_calendar_filter(self, sdk):
        with patch.object(sdk._reader, "read_events", return_value=[]) as mock_read:
            sdk.read_events("today", "today", calendar_name="Work")
            mock_read.assert_called_once_with("today", "today", "Work")

    def test_create_event_delegates_to_writer(self, sdk):
        expected = {
            "id": "x",
            "title": "T",
            "start": "s",
            "end": "e",
            "calendar": "C",
            "location": "",
            "notes": "",
        }
        with patch.object(sdk._writer, "create_event", return_value=expected) as mock_write:
            result = sdk.create_event("T", "2026-04-17T10:00:00", "2026-04-17T11:00:00")
            mock_write.assert_called_once()
            assert result == expected

    def test_read_events_returns_list(self, sdk):
        result = sdk.read_events("2026-04-17", "2026-04-17")
        assert isinstance(result, list)

    def test_create_event_returns_dict(self, sdk):
        result = sdk.create_event("Test", "2026-04-17T10:00:00", "2026-04-17T11:00:00")
        assert isinstance(result, dict)
        assert result["title"] == "Test"
