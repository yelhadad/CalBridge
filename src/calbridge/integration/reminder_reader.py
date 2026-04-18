"""Reminder reading via Apple iCloud CalDAV (VTODO)."""

import logging
from typing import Any

from ..shared.utils import reminder_to_dict
from .base import BaseIntegration
from .mock_store import MockCalDAVStore

logger = logging.getLogger("calbridge.reminder_reader")


class ReminderReader(BaseIntegration):
    """Reads VTODO objects from Apple iCloud CalDAV (Reminders)."""

    def read_reminders(
        self,
        list_name: str | None = None,
        include_completed: bool = False,
    ) -> list[dict[str, Any]]:
        """Return all reminders, optionally filtered by list name."""
        self._check_reminder_permission()
        store = self._get_store()

        lists = self._get_reminder_lists(store, list_name)
        reminders: list[Any] = []
        for lst in lists:
            reminders.extend(self._fetch_todos(lst, include_completed))

        logger.info(
            "read_reminders: found %d reminders (list=%s, include_completed=%s)",
            len(reminders),
            list_name or "all",
            include_completed,
        )
        return [reminder_to_dict(r) for r in reminders]

    def _get_reminder_lists(self, store: Any, list_name: str | None) -> list[Any]:
        """Return VTODO calendar collections, optionally filtered by name."""
        if isinstance(store, MockCalDAVStore):
            lists = store.calendars(supports_todos=True)
        else:
            lists = [c for c in store.calendars() if self._is_reminder_list(c)]

        if list_name:
            lists = [lst for lst in lists if _list_name(lst) == list_name]

        return lists

    @staticmethod
    def _is_reminder_list(cal: Any) -> bool:
        """Identify iCloud reminder lists by name heuristics.

        iCloud exposes reminder lists as CalDAV calendars. Their names often
        contain '⚠️' appended by the caldav library, or match known list names.
        """
        name = _list_name(cal).lower()
        reminder_hints = ("reminder", "⚠️", "tasks")
        return any(hint in name for hint in reminder_hints)

    def _fetch_todos(self, lst: Any, include_completed: bool) -> list[Any]:
        """Fetch all VTODO items from a reminder list."""
        if isinstance(lst, type(None)):
            return []
        try:
            if isinstance(lst, MockCalDAVStore.__class__):
                return lst._todos
            # Live CalDAV: use search for VTODO components
            todos = lst.search(comp_class="VTODO", todo=True, include_completed=include_completed)
            return list(todos)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to fetch todos from list %s: %s", _list_name(lst), exc)
            return []


def _list_name(lst: Any) -> str:
    """Extract list name from a CalDAV calendar or mock object."""
    return getattr(lst, "name", None) or str(getattr(lst, "url", "unknown"))
