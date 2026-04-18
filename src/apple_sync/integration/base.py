"""Abstract base class for all CalDAV integration components."""

import logging
import os
from abc import ABC
from typing import Any

from .caldav_client import CalDAVClient
from .mock_store import MockCalDAVStore
from .permission_manager import PermissionManager


class BaseIntegration(ABC):
    """Provides shared CalDAV client access and mock mode detection."""

    _MOCK_ENV = "APPLE_SYNC_MOCK"

    def __init__(self, mock_mode: bool | None = None) -> None:
        """Determine mock mode from argument or environment variable."""
        if mock_mode is None:
            mock_mode = os.environ.get(self._MOCK_ENV, "false").lower() == "true"
        self._mock_mode = mock_mode
        self._logger = logging.getLogger(f"apple_sync.{self.__class__.__name__}")
        self._permission_manager = PermissionManager()

    def _check_calendar_permission(self) -> None:
        """Verify credentials before any calendar operation."""
        self._permission_manager.check_calendar_permission()

    def _check_reminder_permission(self) -> None:
        """Verify credentials before any reminder operation."""
        self._permission_manager.check_reminder_permission()

    def _get_store(self) -> Any:
        """Return a MockCalDAVStore or live CalDAV principal based on mode."""
        if self._mock_mode:
            return MockCalDAVStore()
        client = CalDAVClient()
        return client.get_principal()
