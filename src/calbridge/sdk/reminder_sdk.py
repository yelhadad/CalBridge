"""ReminderSDK — facade over ReminderWriter."""

from typing import Any

from ..integration.reminder_writer import ReminderWriter


class ReminderSDK:
    """Single entry point for all reminder operations."""

    def __init__(self, mock_mode: bool = False) -> None:
        """Instantiate the writer with the given mock mode."""
        self._writer = ReminderWriter(mock_mode=mock_mode)

    def create_reminder(
        self,
        title: str,
        alert_minutes: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new reminder; supports alert before due date."""
        return self._writer.create_reminder(title, alert_minutes=alert_minutes, **kwargs)
