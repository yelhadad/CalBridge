"""Utility helpers for date parsing and CalDAV data serialization."""

from datetime import date, datetime, timedelta
from typing import Any

from .constants import DATE_FORMAT, DATETIME_FORMAT
from .validators import InputValidator, ValidationError


def parse_date_range(start: str, end: str) -> tuple[datetime, datetime]:
    """Convert shorthand strings or ISO dates to datetime bounds.

    Accepts 'today', 'tomorrow', 'yesterday', or 'YYYY-MM-DD'.
    Returns (start_of_day, end_of_day) datetimes.
    """
    today = date.today()
    shortcuts = {
        "today": today,
        "tomorrow": today + timedelta(days=1),
        "yesterday": today - timedelta(days=1),
    }

    def _resolve(value: str) -> date:
        lower = value.lower()
        if lower in shortcuts:
            return shortcuts[lower]
        InputValidator.validate_date_string(value, "date")
        return datetime.strptime(value, DATE_FORMAT).date()

    start_date = _resolve(start)
    end_date = _resolve(end)

    if end_date < start_date:
        raise ValidationError("end", "End date must not be before start date")

    return (
        datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0),
        datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59),
    )


def serialize_datetime(dt: datetime | None) -> str | None:
    """Serialize datetime to ISO 8601 string, or None if not set."""
    if dt is None:
        return None
    return dt.strftime(DATETIME_FORMAT)


def event_to_dict(event: Any) -> dict[str, Any]:
    """Convert a CalDAV VEVENT (mock or live) to a serializable dict.

    Supports both MockVEvent objects and live caldav.Event objects
    (which expose iCal data via .vobject_instance or .icalendar_component).
    """
    # Try live caldav Event first (has icalendar_component)
    ical = getattr(event, "icalendar_component", None)
    if ical is not None:
        return _live_vevent_to_dict(ical, event)

    # MockVEvent path
    cal_obj = getattr(event, "calendar", None)
    cal_name = getattr(cal_obj, "name", None) or getattr(event, "calendar_name", "")
    return {
        "id": str(getattr(event, "id", getattr(event, "eventIdentifier", ""))),
        "title": str(getattr(event, "title", "") or ""),
        "start": serialize_datetime(getattr(event, "start_dt", None)),
        "end": serialize_datetime(getattr(event, "end_dt", None)),
        "calendar": str(cal_name),
        "location": str(getattr(event, "location", "") or ""),
        "notes": str(getattr(event, "notes", "") or ""),
    }


def _live_vevent_to_dict(ical: Any, event: Any) -> dict[str, Any]:
    """Extract fields from a live caldav icalendar_component."""

    def _dt(key: str) -> str | None:
        val = ical.get(key)
        if val is None:
            return None
        dt_val = val.dt
        if isinstance(dt_val, datetime):
            return serialize_datetime(dt_val)
        if isinstance(dt_val, date):
            return serialize_datetime(datetime(dt_val.year, dt_val.month, dt_val.day))
        return str(dt_val)

    cal_name = getattr(getattr(event, "parent", None), "name", "")
    return {
        "id": str(ical.get("UID", "")),
        "title": str(ical.get("SUMMARY", "")),
        "start": _dt("DTSTART"),
        "end": _dt("DTEND"),
        "calendar": str(cal_name),
        "location": str(ical.get("LOCATION", "") or ""),
        "notes": str(ical.get("DESCRIPTION", "") or ""),
    }


def reminder_to_dict(reminder: Any) -> dict[str, Any]:
    """Convert a CalDAV VTODO (mock or live) to a serializable dict."""
    ical = getattr(reminder, "icalendar_component", None)
    if ical is not None:
        return _live_vtodo_to_dict(ical, reminder)

    # MockVTodo path
    cal_obj = getattr(reminder, "calendar", None)
    list_name = getattr(cal_obj, "name", None) or getattr(reminder, "list_name", "")
    return {
        "id": str(getattr(reminder, "id", getattr(reminder, "calendarItemIdentifier", ""))),
        "title": str(getattr(reminder, "title", "") or ""),
        "notes": str(getattr(reminder, "notes", "") or ""),
        "due_date": serialize_datetime(getattr(reminder, "due_date", None)),
        "priority": int(getattr(reminder, "priority", 0) or 0),
        "list": str(list_name),
    }


def _live_vtodo_to_dict(ical: Any, reminder: Any) -> dict[str, Any]:
    """Extract fields from a live caldav icalendar_component for VTODO."""
    due = ical.get("DUE")
    due_str = None
    if due is not None:
        dt_val = due.dt
        if isinstance(dt_val, datetime):
            due_str = serialize_datetime(dt_val)
        elif isinstance(dt_val, date):
            due_str = serialize_datetime(datetime(dt_val.year, dt_val.month, dt_val.day))

    list_name = getattr(getattr(reminder, "parent", None), "name", "")
    return {
        "id": str(ical.get("UID", "")),
        "title": str(ical.get("SUMMARY", "")),
        "notes": str(ical.get("DESCRIPTION", "") or ""),
        "due_date": due_str,
        "priority": int(ical.get("PRIORITY", 0) or 0),
        "list": str(list_name),
    }
