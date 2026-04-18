"""Application-wide constants — single source of truth for magic values."""

ICAL_CALDAV_URL = "https://caldav.icloud.com"

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

PRIORITY_MIN = 0
PRIORITY_MAX = 9

DEFAULT_CALENDAR = "Calendar"
DEFAULT_REMINDER_LIST = "Reminders"

MAX_TITLE_LENGTH = 255
MAX_NOTES_LENGTH = 10_000
MAX_DATE_RANGE_DAYS = 365

# Standardized error codes returned in agent error responses
ERROR_CODES = {
    "AUTH_FAILED": "AUTH_FAILED",
    "NETWORK_ERROR": "NETWORK_ERROR",
    "VALIDATION_ERROR": "VALIDATION_ERROR",
    "CALENDAR_NOT_FOUND": "CALENDAR_NOT_FOUND",
    "REMINDER_LIST_NOT_FOUND": "REMINDER_LIST_NOT_FOUND",
    "SAVE_FAILED": "SAVE_FAILED",
    "UNKNOWN_ERROR": "UNKNOWN_ERROR",
}

AUTH_REMEDIATION = (
    "Remediation:\n"
    "  1. Verify APPLE_ID environment variable is your iCloud email\n"
    "  2. Generate an App-Specific Password at https://appleid.apple.com\n"
    "     → Sign-In and Security → App-Specific Passwords → '+'\n"
    "  3. Set APPLE_APP_PASSWORD to the generated xxxx-xxxx-xxxx-xxxx value\n"
    "  OR set APPLE_SYNC_MOCK=true for testing without real credentials."
)
