"""Credential validation for iCloud CalDAV authentication.

This module replaces the macOS TCC permission model with CalDAV credential
validation, since the app runs on Linux and connects via HTTPS to Apple's
iCloud CalDAV server.
"""

import logging
import os

from ..shared.constants import AUTH_REMEDIATION

logger = logging.getLogger("apple_sync.permission_manager")


class PermissionDeniedError(PermissionError):
    """Raised when CalDAV credentials are missing or rejected."""

    def __init__(self, message: str = "") -> None:
        """Include remediation steps in the error message."""
        self.code = "AUTH_FAILED"
        super().__init__(f"AUTH_FAILED: {message}\n{AUTH_REMEDIATION}")


class PermissionRestrictedError(PermissionError):
    """Raised when the account is restricted from CalDAV access."""

    def __init__(self, message: str = "") -> None:
        """Store restriction details."""
        self.code = "PERMISSION_RESTRICTED"
        super().__init__(f"PERMISSION_RESTRICTED: {message}")


class PermissionManager:
    """Validates that required credentials are present before CalDAV calls."""

    _MOCK_ENV = "APPLE_SYNC_MOCK"
    _MOCK_AUTH_FAIL_ENV = "MOCK_AUTH_FAIL"

    def check_calendar_permission(self) -> None:
        """Verify credentials for calendar access."""
        self._check("Calendar")

    def check_reminder_permission(self) -> None:
        """Verify credentials for reminder access."""
        self._check("Reminders")

    def _check(self, label: str) -> None:
        """Core credential check; mock or live."""
        if os.environ.get(self._MOCK_ENV, "false").lower() == "true":
            self._check_mock(label)
            return
        self._check_live(label)

    def _check_mock(self, label: str) -> None:
        """Simulate auth check using MOCK_AUTH_FAIL env var."""
        if os.environ.get(self._MOCK_AUTH_FAIL_ENV, "false").lower() == "true":
            self._log_remediation(label)
            raise PermissionDeniedError(f"Simulated auth failure for {label}")
        logger.debug("Mock credential check passed for %s", label)

    def _check_live(self, label: str) -> None:
        """Verify APPLE_ID and APPLE_APP_PASSWORD are present in environment."""
        apple_id = os.environ.get("APPLE_ID", "")
        app_password = os.environ.get("APPLE_APP_PASSWORD", "")
        if not apple_id or not app_password:
            self._log_remediation(label)
            raise PermissionDeniedError(
                "APPLE_ID and APPLE_APP_PASSWORD environment variables are required."
            )
        logger.debug("Credentials present for %s (%s)", label, apple_id)

    def _log_remediation(self, label: str) -> None:
        """Log actionable remediation steps when credentials are missing."""
        logger.error(
            "AUTH_FAILED for %s. %s", label, AUTH_REMEDIATION
        )
