"""Unit tests for CalendarReader in mock mode."""

import pytest

from apple_sync.integration.calendar_reader import CalendarReader
from apple_sync.shared.validators import ValidationError


@pytest.fixture()
def reader():
    return CalendarReader(mock_mode=True)


class TestReadEvents:
    def test_returns_list(self, reader):
        result = reader.read_events("2026-04-17", "2026-04-17")
        assert isinstance(result, list)

    def test_today_returns_list(self, reader):
        result = reader.read_events("today", "today")
        assert isinstance(result, list)

    def test_date_range_returns_events(self, reader):
        result = reader.read_events("2026-04-16", "2026-04-18")
        assert len(result) >= 1

    def test_filter_by_calendar_name(self, reader):
        result = reader.read_events("2026-04-16", "2026-04-18", calendar_name="Work")
        for event in result:
            assert event["calendar"] == "Work"

    def test_filter_by_nonexistent_calendar_returns_empty(self, reader):
        result = reader.read_events("2026-04-17", "2026-04-17", calendar_name="NoSuchCal")
        assert result == []

    def test_result_has_required_keys(self, reader):
        result = reader.read_events("2026-04-17", "2026-04-17")
        if result:
            assert "id" in result[0]
            assert "title" in result[0]
            assert "start" in result[0]
            assert "end" in result[0]

    def test_empty_range_returns_empty(self, reader):
        result = reader.read_events("2020-01-01", "2020-01-02")
        assert result == []

    def test_invalid_date_raises_validation_error(self, reader):
        with pytest.raises(ValidationError):
            reader.read_events("bad-date", "2026-04-17")
