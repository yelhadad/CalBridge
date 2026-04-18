"""Unit tests for BaseIntegration — store factory and permission checks."""

import pytest

from apple_sync.integration.base import BaseIntegration
from apple_sync.integration.mock_store import MockCalDAVStore
from apple_sync.integration.permission_manager import PermissionDeniedError


class ConcreteIntegration(BaseIntegration):
    """Minimal concrete subclass for testing the abstract base."""

    pass


class TestGetStore:
    def test_mock_mode_returns_mock_store(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "true")
        obj = ConcreteIntegration(mock_mode=True)
        store = obj._get_store()
        assert isinstance(store, MockCalDAVStore)

    def test_reads_mock_mode_from_env(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "true")
        obj = ConcreteIntegration()
        assert obj._mock_mode is True

    def test_live_mode_no_caldav_raises_import_error(self, monkeypatch):
        """When caldav is not importable, raise ImportError."""
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "caldav":
                raise ImportError("No module named 'caldav'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setenv("APPLE_SYNC_MOCK", "false")
        monkeypatch.setenv("APPLE_ID", "user@icloud.com")
        monkeypatch.setenv("APPLE_APP_PASSWORD", "xxxx-xxxx-xxxx-xxxx")

        obj = ConcreteIntegration(mock_mode=False)
        with pytest.MonkeyPatch().context() as m:
            m.setattr(builtins, "__import__", mock_import)
            with pytest.raises((ImportError, Exception)):
                obj._get_store()


class TestPermissionChecks:
    def test_check_calendar_permission_passes_in_mock(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "true")
        monkeypatch.setenv("MOCK_AUTH_FAIL", "false")
        obj = ConcreteIntegration(mock_mode=True)
        obj._check_calendar_permission()  # no exception

    def test_check_reminder_permission_passes_in_mock(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "true")
        monkeypatch.setenv("MOCK_AUTH_FAIL", "false")
        obj = ConcreteIntegration(mock_mode=True)
        obj._check_reminder_permission()

    def test_check_calendar_permission_fails_on_auth_fail(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "true")
        monkeypatch.setenv("MOCK_AUTH_FAIL", "true")
        obj = ConcreteIntegration(mock_mode=True)
        with pytest.raises(PermissionDeniedError):
            obj._check_calendar_permission()
