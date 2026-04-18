"""CalendarSDK — facade over CalendarReader and CalendarWriter."""

from typing import Any

from ..integration.calendar_reader import CalendarReader
from ..integration.calendar_writer import CalendarWriter


class CalendarSDK:
    """Single entry point for all calendar operations."""

    def __init__(self, mock_mode: bool = False) -> None:
        """Instantiate reader and writer with the given mock mode."""
        self._reader = CalendarReader(mock_mode=mock_mode)
        self._writer = CalendarWriter(mock_mode=mock_mode)

    def read_events(
        self,
        start: str,
        end: str,
        calendar_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve events in the given date range."""
        return self._reader.read_events(start, end, calendar_name)

    def create_event(
        self,
        title: str,
        start_datetime: str,
        end_datetime: str,
        recurrence: str | None = None,
        recurrence_count: int | None = None,
        recurrence_until: str | None = None,
        alert_minutes: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new calendar event; supports recurrence and alerts."""
        return self._writer.create_event(
            title, start_datetime, end_datetime,
            recurrence=recurrence,
            recurrence_count=recurrence_count,
            recurrence_until=recurrence_until,
            alert_minutes=alert_minutes,
            **kwargs,
        )
