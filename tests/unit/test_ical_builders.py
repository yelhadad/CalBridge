"""Unit tests for iCal string builders in CalendarWriter and ReminderWriter."""

from apple_sync.integration.calendar_writer import CalendarWriter, _to_ical_dt
from apple_sync.integration.reminder_writer import ReminderWriter
from apple_sync.shared.ical_builder import build_rrule, build_valarm


def _vevent(
    title="T",
    start="2026-04-17T10:00:00",
    end="2026-04-17T11:00:00",
    location="",
    notes="",
    recurrence=None,
    count=None,
    until=None,
    alert=None,
):
    return CalendarWriter._build_ical(
        title, start, end, location, notes, recurrence, count, until, alert
    )


def _vtodo(title="T", notes="", due=None, priority=0, alert=None):
    return ReminderWriter._build_ical(title, notes, due, priority, alert)


class TestToIcalDt:
    def test_converts_iso_to_ical(self):
        assert _to_ical_dt("2026-04-17T10:30:00") == "20260417T103000"

    def test_midnight(self):
        assert _to_ical_dt("2026-01-01T00:00:00") == "20260101T000000"


class TestBuildVEvent:
    def test_contains_summary(self):
        assert "SUMMARY:My Meeting" in _vevent("My Meeting", notes="Notes here")

    def test_contains_dtstart(self):
        assert "DTSTART:20260417T100000" in _vevent()

    def test_contains_dtend(self):
        assert "DTEND:20260417T110000" in _vevent()

    def test_contains_uid(self):
        assert "UID:" in _vevent()

    def test_contains_location(self):
        assert "LOCATION:Room A" in _vevent(location="Room A")

    def test_no_location_when_empty(self):
        assert "LOCATION:" not in _vevent(location="")

    def test_contains_rrule_weekly(self):
        ical = _vevent(recurrence="weekly")
        assert "RRULE:FREQ=WEEKLY" in ical

    def test_rrule_with_count(self):
        ical = _vevent(recurrence="daily", count=5)
        assert "RRULE:FREQ=DAILY;COUNT=5" in ical

    def test_rrule_with_until(self):
        ical = _vevent(recurrence="monthly", until="2026-12-31")
        assert "RRULE:FREQ=MONTHLY;UNTIL=20261231" in ical

    def test_no_rrule_when_none(self):
        assert "RRULE:" not in _vevent()

    def test_contains_valarm_when_alert_set(self):
        ical = _vevent(alert=15)
        assert "BEGIN:VALARM" in ical
        assert "TRIGGER:-PT15M" in ical

    def test_no_valarm_when_alert_none(self):
        assert "BEGIN:VALARM" not in _vevent()


class TestBuildVTodo:
    def test_contains_summary(self):
        assert "SUMMARY:Buy milk" in _vtodo("Buy milk")

    def test_contains_priority(self):
        assert "PRIORITY:7" in _vtodo(priority=7)

    def test_contains_due_when_set(self):
        assert "DUE:20260420T090000" in _vtodo(due="2026-04-20T09:00:00")

    def test_no_due_line_when_none(self):
        assert "DUE:" not in _vtodo()

    def test_contains_description(self):
        assert "DESCRIPTION:Important!" in _vtodo(notes="Important!")

    def test_no_description_when_empty(self):
        assert "DESCRIPTION:" not in _vtodo(notes="")

    def test_contains_valarm_when_alert_set(self):
        ical = _vtodo(alert=30)
        assert "BEGIN:VALARM" in ical
        assert "TRIGGER:-PT30M" in ical

    def test_no_valarm_when_alert_none(self):
        assert "BEGIN:VALARM" not in _vtodo()


class TestBuildRrule:
    def test_daily(self):
        assert build_rrule("daily") == "RRULE:FREQ=DAILY"

    def test_yearly_with_count(self):
        assert build_rrule("yearly", recurrence_count=3) == "RRULE:FREQ=YEARLY;COUNT=3"

    def test_until_ignored_when_count_given(self):
        rule = build_rrule("weekly", recurrence_count=2, recurrence_until="2026-12-31")
        assert "COUNT=2" in rule
        assert "UNTIL" not in rule

    def test_malformed_until_ignored(self):
        rule = build_rrule("daily", recurrence_until="not-a-date")
        assert "UNTIL" not in rule


class TestBuildValarm:
    def test_15_minutes(self):
        alarm = build_valarm(15)
        assert "TRIGGER:-PT15M" in alarm
        assert "ACTION:DISPLAY" in alarm

    def test_zero_minutes(self):
        assert "TRIGGER:-PT0M" in build_valarm(0)

    def test_negative_offset(self):
        assert "TRIGGER:PT10M" in build_valarm(-10)
