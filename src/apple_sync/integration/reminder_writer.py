"""Reminder creation via Apple iCloud CalDAV (VTODO)."""

import logging
import uuid
from datetime import datetime
from typing import Any

from ..shared.constants import DEFAULT_REMINDER_LIST
from ..shared.ical_builder import build_valarm
from ..shared.utils import reminder_to_dict
from ..shared.validators import InputValidator
from .base import BaseIntegration
from .mock_store import MockCalDAVStore

logger = logging.getLogger("apple_sync.reminder_writer")


class ReminderWriter(BaseIntegration):
    """Creates VTODO objects in Apple iCloud CalDAV (Reminders)."""

    def create_reminder(
        self,
        title: str,
        notes: str = "",
        due_date: str | None = None,
        priority: int = 0,
        list_name: str | None = None,
        alert_minutes: int | None = None,
    ) -> dict[str, Any]:
        """Create a new reminder and return its serialized dict."""
        InputValidator.validate_non_empty_string(title, "title")
        InputValidator.validate_priority(priority, "priority")
        if due_date is not None:
            InputValidator.validate_datetime_string(due_date, "due_date")

        self._check_reminder_permission()
        store = self._get_store()
        target = self._get_target_list(store, list_name)
        ical = self._build_ical(title, notes, due_date, priority, alert_minutes)

        result = target.save_todo(ical)
        logger.info(
            "create_reminder: created '%s' in list '%s' (alert=%s)",
            title,
            getattr(target, "name", list_name or DEFAULT_REMINDER_LIST),
            alert_minutes,
        )
        return reminder_to_dict(result)

    def _get_target_list(self, store: Any, name: str | None) -> Any:
        """Return the named VTODO calendar or the default reminder list."""
        if isinstance(store, MockCalDAVStore):
            if name is None:
                return store.default_reminder_list()
            todos = [c for c in store.calendars(supports_todos=True) if c.name == name]
            if todos:
                return todos[0]
            logger.warning("Reminder list '%s' not found; using default.", name)
            return store.default_reminder_list()

        all_cals = store.calendars()
        todo_cals = [c for c in all_cals if self._is_todo_calendar(c)]
        if name:
            for cal in todo_cals:
                if getattr(cal, "name", str(cal.url)) == name:
                    return cal
            logger.warning("Reminder list '%s' not found; using first available.", name)
        return todo_cals[0] if todo_cals else all_cals[0]

    @staticmethod
    def _is_todo_calendar(cal: Any) -> bool:
        """Check that a CalDAV calendar supports VTODO components."""
        try:
            props = cal.get_properties()
            supported = props.get(
                "{urn:ietf:params:xml:ns:caldav}supported-calendar-component-set", ""
            )
            return "VTODO" in str(supported)
        except Exception:  # noqa: BLE001
            return False

    @staticmethod
    def _build_ical(
        title: str,
        notes: str,
        due_date: str | None,
        priority: int,
        alert_minutes: int | None,
    ) -> str:
        """Render an iCalendar VTODO string with optional DUE and VALARM."""
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//apple-sync//ReminderWriter//EN",
            "BEGIN:VTODO",
            f"UID:{uuid.uuid4()}",
            f"SUMMARY:{title}",
            f"PRIORITY:{priority}",
        ]
        if notes:
            lines.append(f"DESCRIPTION:{notes}")
        if due_date:
            dt = datetime.fromisoformat(due_date)
            lines.append(f"DUE:{dt.strftime('%Y%m%dT%H%M%S')}")
        if alert_minutes is not None:
            lines.append(build_valarm(alert_minutes))
        lines += ["END:VTODO", "END:VCALENDAR"]
        return "\r\n".join(lines)
