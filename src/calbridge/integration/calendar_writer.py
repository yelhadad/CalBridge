"""Calendar event creation via Apple iCloud CalDAV."""

import logging
import uuid
from datetime import datetime
from typing import Any

from ..shared.constants import DEFAULT_CALENDAR
from ..shared.ical_builder import build_rrule, build_valarm, validate_recurrence
from ..shared.utils import event_to_dict
from ..shared.validators import InputValidator
from .base import BaseIntegration
from .mock_store import MockCalDAVStore

logger = logging.getLogger("calbridge.calendar_writer")


class CalendarWriter(BaseIntegration):
    """Creates VEVENT objects in Apple iCloud CalDAV."""

    def create_event(
        self,
        title: str,
        start_datetime: str,
        end_datetime: str,
        calendar_name: str | None = None,
        location: str = "",
        notes: str = "",
        recurrence: str | None = None,
        recurrence_count: int | None = None,
        recurrence_until: str | None = None,
        alert_minutes: int | None = None,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new calendar event and return its serialized dict."""
        InputValidator.validate_non_empty_string(title, "title")
        InputValidator.validate_datetime_string(start_datetime, "start_datetime")
        InputValidator.validate_datetime_string(end_datetime, "end_datetime")
        if recurrence is not None:
            validate_recurrence(recurrence)

        self._check_calendar_permission()
        store = self._get_store()
        target = self._get_target_calendar(store, calendar_name)
        ical = self._build_ical(
            title,
            start_datetime,
            end_datetime,
            location,
            notes,
            recurrence,
            recurrence_count,
            recurrence_until,
            alert_minutes,
        )

        result = target.save_event(ical)
        logger.info(
            "create_event: created '%s' in '%s' (recurrence=%s, alert=%s)",
            title,
            getattr(target, "name", calendar_name or DEFAULT_CALENDAR),
            recurrence,
            alert_minutes,
        )
        return event_to_dict(result)

    def _get_target_calendar(self, store: Any, name: str | None) -> Any:
        """Return the named VEVENT calendar or the default."""
        if isinstance(store, MockCalDAVStore):
            if name is None:
                return store.default_event_calendar()
            cals = [c for c in store.calendars(supports_todos=False) if c.name == name]
            if cals:
                return cals[0]
            logger.warning("Calendar '%s' not found; using default.", name)
            return store.default_event_calendar()

        all_cals = store.calendars()
        if name:
            for cal in all_cals:
                if getattr(cal, "name", str(cal.url)) == name:
                    return cal
            logger.warning("Calendar '%s' not found; using first available.", name)
        return all_cals[0] if all_cals else store.calendars()[0]

    @staticmethod
    def _build_ical(
        title: str,
        start: str,
        end: str,
        location: str,
        notes: str,
        recurrence: str | None,
        recurrence_count: int | None,
        recurrence_until: str | None,
        alert_minutes: int | None,
    ) -> str:
        """Render an iCalendar VEVENT string with optional RRULE and VALARM."""
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//calbridge//CalendarWriter//EN",
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}",
            f"SUMMARY:{title}",
            f"DTSTART:{_to_ical_dt(start)}",
            f"DTEND:{_to_ical_dt(end)}",
        ]
        if location:
            lines.append(f"LOCATION:{location}")
        if notes:
            lines.append(f"DESCRIPTION:{notes}")
        if recurrence:
            lines.append(build_rrule(recurrence, recurrence_count, recurrence_until))
        if alert_minutes is not None:
            lines.append(build_valarm(alert_minutes))
        lines += ["END:VEVENT", "END:VCALENDAR"]
        return "\r\n".join(lines)


def _to_ical_dt(dt_str: str) -> str:
    """Convert YYYY-MM-DDTHH:MM:SS to iCal YYYYMMDDTHHMMSS format."""
    dt = datetime.fromisoformat(dt_str)
    return dt.strftime("%Y%m%dT%H%M%S")
