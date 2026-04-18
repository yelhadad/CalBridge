"""Input validation — all boundary checks for agent-provided data."""

from datetime import datetime

from .constants import (
    DATETIME_FORMAT,
    DATE_FORMAT,
    MAX_NOTES_LENGTH,
    MAX_TITLE_LENGTH,
    PRIORITY_MAX,
    PRIORITY_MIN,
)


class ValidationError(ValueError):
    """Raised when agent input fails validation."""

    def __init__(self, field: str, message: str) -> None:
        """Store field name and message for structured error reporting."""
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class InputValidator:
    """Validates all inputs at the agent boundary before processing."""

    @staticmethod
    def validate_date_string(value: str, field: str = "date") -> None:
        """Ensure value is a valid YYYY-MM-DD date string."""
        try:
            datetime.strptime(value, DATE_FORMAT)
        except (ValueError, TypeError) as exc:
            raise ValidationError(field, f"Must be YYYY-MM-DD, got: {value!r}") from exc

    @staticmethod
    def validate_datetime_string(value: str, field: str = "datetime") -> None:
        """Ensure value is a valid ISO 8601 datetime string (YYYY-MM-DDTHH:MM:SS)."""
        try:
            datetime.strptime(value, DATETIME_FORMAT)
        except (ValueError, TypeError) as exc:
            raise ValidationError(
                field, f"Must be YYYY-MM-DDTHH:MM:SS, got: {value!r}"
            ) from exc

    @staticmethod
    def validate_priority(value: int, field: str = "priority") -> None:
        """Ensure priority is an integer in [0, 9]."""
        if not isinstance(value, int) or not (PRIORITY_MIN <= value <= PRIORITY_MAX):
            raise ValidationError(
                field,
                f"Must be integer {PRIORITY_MIN}–{PRIORITY_MAX}, got: {value!r}",
            )

    @staticmethod
    def validate_non_empty_string(value: str, field: str) -> None:
        """Ensure value is a non-empty string within length bounds."""
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(field, "Must be a non-empty string")
        limit = MAX_TITLE_LENGTH if "title" in field.lower() else MAX_NOTES_LENGTH
        if len(value) > limit:
            raise ValidationError(field, f"Exceeds maximum length of {limit}")
