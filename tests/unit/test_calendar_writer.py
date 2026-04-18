"""Unit tests for CalendarWriter in mock mode."""

import pytest

from calbridge.integration.calendar_writer import CalendarWriter
from calbridge.shared.validators import ValidationError


@pytest.fixture()
def writer():
    return CalendarWriter(mock_mode=True)


class TestCreateEvent:
    def test_success_returns_dict(self, writer):
        result = writer.create_event("Meeting", "2026-04-17T10:00:00", "2026-04-17T11:00:00")
        assert isinstance(result, dict)

    def test_result_has_required_keys(self, writer):
        result = writer.create_event("Meeting", "2026-04-17T10:00:00", "2026-04-17T11:00:00")
        assert "id" in result
        assert "title" in result
        assert result["title"] == "Meeting"

    def test_custom_calendar(self, writer):
        result = writer.create_event(
            "Meeting", "2026-04-17T10:00:00", "2026-04-17T11:00:00", calendar_name="Work"
        )
        assert result["calendar"] == "Work"

    def test_with_location_and_notes(self, writer):
        result = writer.create_event(
            "Meeting",
            "2026-04-17T10:00:00",
            "2026-04-17T11:00:00",
            location="Office",
            notes="Bring laptop",
        )
        assert result["location"] == "Office"
        assert result["notes"] == "Bring laptop"

    def test_empty_title_raises(self, writer):
        with pytest.raises(ValidationError) as exc:
            writer.create_event("", "2026-04-17T10:00:00", "2026-04-17T11:00:00")
        assert exc.value.field == "title"

    def test_invalid_start_raises(self, writer):
        with pytest.raises(ValidationError):
            writer.create_event("Meeting", "bad-start", "2026-04-17T11:00:00")

    def test_invalid_end_raises(self, writer):
        with pytest.raises(ValidationError):
            writer.create_event("Meeting", "2026-04-17T10:00:00", "bad-end")

    def test_unknown_calendar_falls_back_to_default(self, writer):
        result = writer.create_event(
            "Meeting", "2026-04-17T10:00:00", "2026-04-17T11:00:00", calendar_name="NonExistent"
        )
        assert result["title"] == "Meeting"
