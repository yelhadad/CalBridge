"""Unit tests for PermissionManager (CalDAV credential validation)."""

import pytest

from apple_sync.integration.permission_manager import (
    PermissionDeniedError,
    PermissionManager,
)


class TestCalendarPermission:
    def test_authorized_passes(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "true")
        monkeypatch.setenv("MOCK_AUTH_FAIL", "false")
        PermissionManager().check_calendar_permission()  # no exception

    def test_auth_fail_raises(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "true")
        monkeypatch.setenv("MOCK_AUTH_FAIL", "true")
        with pytest.raises(PermissionDeniedError) as exc:
            PermissionManager().check_calendar_permission()
        assert exc.value.code == "AUTH_FAILED"

    def test_live_missing_env_raises(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "false")
        monkeypatch.delenv("APPLE_ID", raising=False)
        monkeypatch.delenv("APPLE_APP_PASSWORD", raising=False)
        with pytest.raises(PermissionDeniedError):
            PermissionManager().check_calendar_permission()

    def test_live_with_credentials_passes_check(self, monkeypatch):
        """Only checks env vars are present, not that they're valid."""
        monkeypatch.setenv("APPLE_SYNC_MOCK", "false")
        monkeypatch.setenv("APPLE_ID", "user@icloud.com")
        monkeypatch.setenv("APPLE_APP_PASSWORD", "xxxx-xxxx-xxxx-xxxx")
        # Should not raise (credential presence check only)
        PermissionManager().check_calendar_permission()


class TestReminderPermission:
    def test_authorized_passes(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "true")
        monkeypatch.setenv("MOCK_AUTH_FAIL", "false")
        PermissionManager().check_reminder_permission()

    def test_auth_fail_raises(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "true")
        monkeypatch.setenv("MOCK_AUTH_FAIL", "true")
        with pytest.raises(PermissionDeniedError) as exc:
            PermissionManager().check_reminder_permission()
        assert exc.value.code == "AUTH_FAILED"


class TestRemediationLogging:
    def test_remediation_logged_on_failure(self, monkeypatch, caplog):
        import logging

        monkeypatch.setenv("APPLE_SYNC_MOCK", "true")
        monkeypatch.setenv("MOCK_AUTH_FAIL", "true")
        with caplog.at_level(logging.ERROR, logger="apple_sync.permission_manager"):  # noqa: SIM117
            with pytest.raises(PermissionDeniedError):
                PermissionManager().check_calendar_permission()
        assert any("AUTH_FAILED" in r.message for r in caplog.records)
