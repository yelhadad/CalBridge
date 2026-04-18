"""Unit tests for CalDAVClient authentication error handling."""

import pytest

from calbridge.integration.caldav_client import AuthenticationError, NetworkError


class TestAuthenticationError:
    def test_has_code(self):
        exc = AuthenticationError("bad creds")
        assert exc.code == "AUTH_FAILED"

    def test_message_includes_remediation(self):
        exc = AuthenticationError("bad creds")
        assert "AUTH_FAILED" in str(exc)
        assert "APPLE_APP_PASSWORD" in str(exc)


class TestNetworkError:
    def test_has_code(self):
        exc = NetworkError("timeout")
        assert exc.code == "NETWORK_ERROR"

    def test_message_content(self):
        exc = NetworkError("connection refused")
        assert "NETWORK_ERROR" in str(exc)


class TestCalDAVClientMissingCredentials:
    def test_get_principal_raises_on_empty_creds(self, monkeypatch):
        """Missing env vars should raise AuthenticationError immediately."""
        monkeypatch.setenv("APPLE_SYNC_MOCK", "false")
        monkeypatch.delenv("APPLE_ID", raising=False)
        monkeypatch.delenv("APPLE_APP_PASSWORD", raising=False)

        from calbridge.integration.caldav_client import CalDAVClient

        client = CalDAVClient()
        with pytest.raises(AuthenticationError) as exc:
            client.get_principal()
        assert exc.value.code == "AUTH_FAILED"

    def test_get_principal_raises_on_missing_apple_id(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "false")
        monkeypatch.delenv("APPLE_ID", raising=False)
        monkeypatch.setenv("APPLE_APP_PASSWORD", "xxxx")

        from calbridge.integration.caldav_client import CalDAVClient

        client = CalDAVClient()
        with pytest.raises(AuthenticationError):
            client.get_principal()

    def test_explicit_empty_creds_raise(self, monkeypatch):
        monkeypatch.setenv("APPLE_SYNC_MOCK", "false")
        monkeypatch.delenv("APPLE_ID", raising=False)
        monkeypatch.delenv("APPLE_APP_PASSWORD", raising=False)
        from calbridge.integration.caldav_client import CalDAVClient

        client = CalDAVClient(apple_id="", app_password="")
        with pytest.raises(AuthenticationError):
            client.get_principal()

    def test_network_error_on_connection_failure(self, monkeypatch):
        """Simulate a non-auth network failure."""
        monkeypatch.setenv("APPLE_SYNC_MOCK", "false")
        monkeypatch.setenv("APPLE_ID", "user@icloud.com")
        monkeypatch.setenv("APPLE_APP_PASSWORD", "xxxx-xxxx-xxxx-xxxx")

        from unittest.mock import MagicMock, patch

        from calbridge.integration.caldav_client import CalDAVClient

        mock_client = MagicMock()
        mock_client.principal.side_effect = Exception("connection refused")

        with patch("caldav.DAVClient", return_value=mock_client):
            client = CalDAVClient()
            with pytest.raises(NetworkError):
                client.get_principal()

    def test_auth_error_on_401(self, monkeypatch):
        """Simulate a 401 Unauthorized response."""
        monkeypatch.setenv("APPLE_SYNC_MOCK", "false")
        monkeypatch.setenv("APPLE_ID", "user@icloud.com")
        monkeypatch.setenv("APPLE_APP_PASSWORD", "xxxx-xxxx-xxxx-xxxx")

        from unittest.mock import MagicMock, patch

        from calbridge.integration.caldav_client import CalDAVClient

        mock_client = MagicMock()
        mock_client.principal.side_effect = Exception("401 Unauthorized")

        with patch("caldav.DAVClient", return_value=mock_client):
            client = CalDAVClient()
            with pytest.raises(AuthenticationError):
                client.get_principal()
