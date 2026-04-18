"""iCal string builders for recurrence (RRULE) and alerts (VALARM)."""

from datetime import datetime

RECURRENCE_FREQS = {"daily", "weekly", "monthly", "yearly"}


def build_rrule(
    recurrence: str,
    recurrence_count: int | None = None,
    recurrence_until: str | None = None,
) -> str:
    """Return an RRULE line for the given recurrence pattern.

    recurrence: one of 'daily', 'weekly', 'monthly', 'yearly'
    recurrence_count: stop after N occurrences
    recurrence_until: stop on or before this date (YYYY-MM-DD)
    """
    freq = recurrence.upper()
    rule = f"RRULE:FREQ={freq}"
    if recurrence_count is not None and recurrence_count > 0:
        rule += f";COUNT={recurrence_count}"
    elif recurrence_until is not None:
        try:
            until_dt = datetime.strptime(recurrence_until, "%Y-%m-%d")
            rule += f";UNTIL={until_dt.strftime('%Y%m%dT000000Z')}"
        except ValueError:
            pass  # silently skip malformed until date
    return rule


def build_valarm(alert_minutes: int) -> str:
    """Return a VALARM component string for an alert N minutes before.

    Negative alert_minutes = before start; positive = after start.
    Standard usage: alert_minutes=15 → alert 15 minutes before.
    """
    if alert_minutes >= 0:
        trigger = f"-PT{alert_minutes}M"
    else:
        # Positive offset after start (unusual but valid)
        trigger = f"PT{abs(alert_minutes)}M"

    return (
        "BEGIN:VALARM\r\n"
        "ACTION:DISPLAY\r\n"
        "DESCRIPTION:Reminder\r\n"
        f"TRIGGER:{trigger}\r\n"
        "END:VALARM"
    )


def validate_recurrence(value: str) -> None:
    """Raise ValueError if recurrence value is not a supported frequency."""
    if value.lower() not in RECURRENCE_FREQS:
        raise ValueError(
            f"recurrence must be one of {sorted(RECURRENCE_FREQS)}, got {value!r}"
        )
