"""Unit tests for ReminderSDK facade."""

from unittest.mock import patch

import pytest

from apple_sync.sdk.reminder_sdk import ReminderSDK


@pytest.fixture()
def sdk():
    return ReminderSDK(mock_mode=True)


class TestReminderSDK:
    def test_create_reminder_delegates_to_writer(self, sdk):
        expected = {
            "id": "r1",
            "title": "T",
            "notes": "",
            "due_date": None,
            "priority": 0,
            "list": "Reminders",
        }
        with patch.object(sdk._writer, "create_reminder", return_value=expected) as mock_write:
            result = sdk.create_reminder("T")
            mock_write.assert_called_once_with("T", alert_minutes=None)
            assert result == expected

    def test_create_reminder_returns_dict(self, sdk):
        result = sdk.create_reminder("Buy milk")
        assert isinstance(result, dict)
        assert result["title"] == "Buy milk"

    def test_create_reminder_with_kwargs_passed_through(self, sdk):
        with patch.object(sdk._writer, "create_reminder", return_value={}) as mock_write:
            sdk.create_reminder("Task", priority=5, notes="Details")
            mock_write.assert_called_once_with(
                "Task", alert_minutes=None, priority=5, notes="Details"
            )
