"""Calendar event reading via Apple iCloud CalDAV."""

import logging
from datetime import datetime
from typing import Any

from ..shared.utils import event_to_dict, parse_date_range
from ..shared.validators import InputValidator
from .base import BaseIntegration
from .mock_store import MockCalDAVStore

logger = logging.getLogger("apple_sync.calendar_reader")


class CalendarReader(BaseIntegration):
    """Reads VEVENT objects from Apple iCloud CalDAV over a given date range."""

    def read_events(
        self,
        start: str,
        end: str,
        calendar_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return events between start and end, optionally filtered by calendar name."""
        self._check_calendar_permission()
        start_dt, end_dt = parse_date_range(start, end)
        store = self._get_store()

        calendars = self._get_event_calendars(store, calendar_name)
        events: list[Any] = []
        for cal in calendars:
            events.extend(self._search_calendar(cal, start_dt, end_dt))

        logger.info(
            "read_events: found %d events (%s → %s, calendar=%s)",
            len(events), start, end, calendar_name or "all",
        )
        return [event_to_dict(e) for e in events]

    def _get_event_calendars(self, store: Any, calendar_name: str | None) -> list[Any]:
        """Return VEVENT calendars, filtered by name if provided."""
        if isinstance(store, MockCalDAVStore):
            cals = store.calendars(supports_todos=False)
        else:
            # iCloud's get_properties() returns empty dicts, so we include all
            # calendars and skip only known reminder-only collections.
            cals = [
                c for c in store.calendars()
                if not self._is_reminder_only_calendar(c)
            ]

        if calendar_name:
            InputValidator.validate_non_empty_string(calendar_name, "calendar_name")
            cals = [c for c in cals if _calendar_name(c) == calendar_name]

        return cals

    @staticmethod
    def _is_reminder_only_calendar(cal: Any) -> bool:
        """Return True for collections that only hold reminders (VTODO), not events."""
        name = _calendar_name(cal).lower()
        # iCloud reminder lists often end with a warning emoji or match known patterns
        reminder_hints = ("reminder", "⚠️")
        return any(hint in name for hint in reminder_hints)

    def _search_calendar(
        self, cal: Any, start_dt: datetime, end_dt: datetime
    ) -> list[Any]:
        """Search a single calendar for events in the date range."""
        try:
            return list(cal.date_search(start=start_dt, end=end_dt, expand=True))
        except Exception as exc:  # noqa: BLE001
            logger.warning("date_search failed for calendar %s: %s", _calendar_name(cal), exc)
            return []


def _calendar_name(cal: Any) -> str:
    """Extract calendar name from either a mock or live CalDAV calendar."""
    return getattr(cal, "name", None) or str(getattr(cal, "url", "unknown"))
