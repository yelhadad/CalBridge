"""Authenticated CalDAV client factory for Apple iCloud."""

import logging
import os
from typing import Any

from ..shared.constants import AUTH_REMEDIATION, ERROR_CODES, ICAL_CALDAV_URL

logger = logging.getLogger("calbridge.caldav_client")


class AuthenticationError(Exception):
    """Raised when CalDAV authentication fails."""

    def __init__(self, message: str = "") -> None:
        """Include remediation steps in the error message."""
        self.code = ERROR_CODES["AUTH_FAILED"]
        super().__init__(f"AUTH_FAILED: {message}\n{AUTH_REMEDIATION}")


class NetworkError(Exception):
    """Raised when the CalDAV server is unreachable."""

    def __init__(self, message: str = "") -> None:
        """Store network error details."""
        self.code = ERROR_CODES["NETWORK_ERROR"]
        super().__init__(f"NETWORK_ERROR: {message}")


class CalDAVClient:
    """Creates an authenticated session to Apple iCloud CalDAV."""

    _APPLE_ID_ENV = "APPLE_ID"
    _APP_PASSWORD_ENV = "APPLE_APP_PASSWORD"  # noqa: S105

    def __init__(
        self,
        apple_id: str | None = None,
        app_password: str | None = None,
        caldav_url: str = ICAL_CALDAV_URL,
    ) -> None:
        """Read credentials from args or environment variables."""
        self._apple_id = apple_id or os.environ.get(self._APPLE_ID_ENV, "")
        self._app_password = app_password or os.environ.get(self._APP_PASSWORD_ENV, "")
        self._caldav_url = caldav_url

    def get_principal(self) -> Any:
        """Connect to iCloud CalDAV and return the authenticated principal.

        The principal is the root resource representing the user's CalDAV home,
        from which all calendar collections can be listed.
        """
        if not self._apple_id or not self._app_password:
            raise AuthenticationError(
                "APPLE_ID and APPLE_APP_PASSWORD environment variables are required."
            )

        try:
            import caldav  # type: ignore[import]
        except ImportError as exc:
            raise ImportError("caldav package is required. Install with: uv add caldav") from exc

        try:
            client = caldav.DAVClient(
                url=self._caldav_url,
                username=self._apple_id,
                password=self._app_password,
            )
            principal = client.principal()
            logger.info("CalDAV authenticated for %s", self._apple_id)
            return principal
        except Exception as exc:
            msg = str(exc).lower()
            if any(kw in msg for kw in ("401", "403", "unauthorized", "forbidden")):
                logger.error("CalDAV auth failed for %s", self._apple_id)
                raise AuthenticationError(str(exc)) from exc
            logger.error("CalDAV network error: %s", exc)
            raise NetworkError(str(exc)) from exc
