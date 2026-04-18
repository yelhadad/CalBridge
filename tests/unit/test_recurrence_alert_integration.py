"""Tests for recurrence and alert parameters in CalendarWriter and ReminderWriter."""

import pytest

from apple_sync.integration.calendar_writer import CalendarWriter
from apple_sync.integration.reminder_writer import ReminderWriter


@pytest.fixture()
def writer():
    return CalendarWriter(mock_mode=True)


@pytest.fixture()
def rem_writer():
    return ReminderWriter(mock_mode=True)


class TestCreateEventRecurrence:
    def test_daily_recurrence(self, writer):
        result = writer.create_event(
            "Standup",
            "2026-04-18T09:00:00",
            "2026-04-18T09:30:00",
            recurrence="daily",
        )
        assert result["title"] == "Standup"

    def test_weekly_recurrence_with_count(self, writer):
        result = writer.create_event(
            "Weekly Review",
            "2026-04-18T10:00:00",
            "2026-04-18T11:00:00",
            recurrence="weekly",
            recurrence_count=10,
        )
        assert result["title"] == "Weekly Review"

    def test_monthly_recurrence_with_until(self, writer):
        result = writer.create_event(
            "Monthly Report",
            "2026-04-18T10:00:00",
            "2026-04-18T11:00:00",
            recurrence="monthly",
            recurrence_until="2026-12-31",
        )
        assert result["title"] == "Monthly Report"

    def test_yearly_recurrence(self, writer):
        result = writer.create_event(
            "Birthday",
            "2026-05-05T00:00:00",
            "2026-05-05T23:59:00",
            recurrence="yearly",
        )
        assert result["title"] == "Birthday"

    def test_invalid_recurrence_raises(self, writer):
        with pytest.raises((ValueError, Exception)):
            writer.create_event(
                "Bad",
                "2026-04-18T09:00:00",
                "2026-04-18T10:00:00",
                recurrence="hourly",
            )


class TestCreateEventAlert:
    def test_alert_15_minutes(self, writer):
        result = writer.create_event(
            "Meeting",
            "2026-04-18T10:00:00",
            "2026-04-18T11:00:00",
            alert_minutes=15,
        )
        assert result["title"] == "Meeting"

    def test_alert_one_day(self, writer):
        result = writer.create_event(
            "Trip",
            "2026-04-20T08:00:00",
            "2026-04-20T09:00:00",
            alert_minutes=1440,  # 24 hours
        )
        assert result["title"] == "Trip"

    def test_recurrence_and_alert_combined(self, writer):
        result = writer.create_event(
            "Weekly Standup",
            "2026-04-18T09:00:00",
            "2026-04-18T09:30:00",
            recurrence="weekly",
            alert_minutes=10,
        )
        assert result["title"] == "Weekly Standup"


class TestCreateReminderAlert:
    def test_alert_30_minutes(self, rem_writer):
        result = rem_writer.create_reminder(
            "Take medicine",
            due_date="2026-04-18T08:00:00",
            alert_minutes=30,
        )
        assert result["title"] == "Take medicine"

    def test_alert_zero(self, rem_writer):
        result = rem_writer.create_reminder(
            "Call back",
            due_date="2026-04-18T14:00:00",
            alert_minutes=0,
        )
        assert result["title"] == "Call back"

    def test_no_alert(self, rem_writer):
        result = rem_writer.create_reminder("Simple task")
        assert result["title"] == "Simple task"
