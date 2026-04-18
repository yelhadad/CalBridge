"""Unit tests for ReminderWriter in mock mode."""

import pytest

from calbridge.integration.reminder_writer import ReminderWriter
from calbridge.shared.validators import ValidationError


@pytest.fixture()
def writer():
    return ReminderWriter(mock_mode=True)


class TestCreateReminder:
    def test_success_returns_dict(self, writer):
        result = writer.create_reminder("Buy milk")
        assert isinstance(result, dict)

    def test_result_has_required_keys(self, writer):
        result = writer.create_reminder("Buy milk")
        assert "id" in result
        assert "title" in result
        assert result["title"] == "Buy milk"

    def test_with_due_date(self, writer):
        result = writer.create_reminder("Submit report", due_date="2026-04-20T09:00:00")
        assert result["due_date"] is not None

    def test_with_priority(self, writer):
        result = writer.create_reminder("Urgent task", priority=7)
        assert result["priority"] == 7

    def test_with_notes(self, writer):
        result = writer.create_reminder("Task", notes="Do it carefully")
        assert result["notes"] == "Do it carefully"

    def test_empty_title_raises(self, writer):
        with pytest.raises(ValidationError) as exc:
            writer.create_reminder("")
        assert exc.value.field == "title"

    def test_invalid_priority_raises(self, writer):
        with pytest.raises(ValidationError) as exc:
            writer.create_reminder("Task", priority=10)
        assert exc.value.field == "priority"

    def test_invalid_due_date_raises(self, writer):
        with pytest.raises(ValidationError):
            writer.create_reminder("Task", due_date="not-a-date")

    def test_unknown_list_falls_back_to_default(self, writer):
        result = writer.create_reminder("Task", list_name="NonExistent")
        assert result["title"] == "Task"
