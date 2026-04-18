"""Unit tests for config_store — credential persistence to ~/.config/calbridge/config.json."""

import json
import stat

import pytest

from calbridge.shared import config_store


@pytest.fixture()
def tmp_config(tmp_path, monkeypatch):
    """Redirect CONFIG_DIR and CONFIG_FILE to a temp directory for isolation."""
    config_dir = tmp_path / ".config" / "calbridge"
    config_file = config_dir / "config.json"
    monkeypatch.setattr(config_store, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(config_store, "CONFIG_FILE", config_file)
    return config_file


class TestSaveConfig:
    def test_creates_file_with_correct_keys(self, tmp_config):
        config_store.save_config("user@icloud.com", "xxxx-xxxx-xxxx-xxxx")
        data = json.loads(tmp_config.read_text())
        assert data["apple_id"] == "user@icloud.com"
        assert data["apple_app_password"] == "xxxx-xxxx-xxxx-xxxx"

    def test_file_is_owner_read_write_only(self, tmp_config):
        config_store.save_config("user@icloud.com", "xxxx-xxxx-xxxx-xxxx")
        mode = tmp_config.stat().st_mode & 0o777
        assert mode == stat.S_IRUSR | stat.S_IWUSR

    def test_creates_parent_directories(self, tmp_config):
        config_store.save_config("user@icloud.com", "xxxx-xxxx-xxxx-xxxx")
        assert tmp_config.parent.exists()

    def test_overwrites_existing_config(self, tmp_config):
        config_store.save_config("old@icloud.com", "old-pass")
        config_store.save_config("new@icloud.com", "new-pass")
        data = json.loads(tmp_config.read_text())
        assert data["apple_id"] == "new@icloud.com"


class TestLoadConfig:
    def test_returns_empty_dict_when_file_missing(self, tmp_config):
        assert config_store.load_config() == {}

    def test_returns_data_when_file_exists(self, tmp_config):
        config_store.save_config("user@icloud.com", "xxxx-xxxx-xxxx-xxxx")
        data = config_store.load_config()
        assert data["apple_id"] == "user@icloud.com"

    def test_returns_empty_dict_on_corrupt_json(self, tmp_config):
        tmp_config.parent.mkdir(parents=True, exist_ok=True)
        tmp_config.write_text("not valid json")
        assert config_store.load_config() == {}


class TestGetters:
    def test_get_apple_id_from_config(self, tmp_config):
        config_store.save_config("user@icloud.com", "xxxx-xxxx-xxxx-xxxx")
        assert config_store.get_apple_id() == "user@icloud.com"

    def test_get_app_password_from_config(self, tmp_config):
        config_store.save_config("user@icloud.com", "xxxx-xxxx-xxxx-xxxx")
        assert config_store.get_app_password() == "xxxx-xxxx-xxxx-xxxx"

    def test_get_apple_id_returns_empty_when_missing(self, tmp_config):
        assert config_store.get_apple_id() == ""

    def test_get_app_password_returns_empty_when_missing(self, tmp_config):
        assert config_store.get_app_password() == ""


class TestCalDAVClientReadsFromConfig:
    """Verify CalDAVClient picks up credentials from the config file."""

    def test_reads_apple_id_from_config_file(self, tmp_config, monkeypatch):
        monkeypatch.delenv("APPLE_ID", raising=False)
        monkeypatch.delenv("APPLE_APP_PASSWORD", raising=False)
        config_store.save_config("config@icloud.com", "xxxx-xxxx-xxxx-xxxx")

        from calbridge.integration.caldav_client import CalDAVClient

        client = CalDAVClient()
        assert client._apple_id == "config@icloud.com"

    def test_reads_password_from_config_file(self, tmp_config, monkeypatch):
        monkeypatch.delenv("APPLE_ID", raising=False)
        monkeypatch.delenv("APPLE_APP_PASSWORD", raising=False)
        config_store.save_config("config@icloud.com", "xxxx-xxxx-xxxx-xxxx")

        from calbridge.integration.caldav_client import CalDAVClient

        client = CalDAVClient()
        assert client._app_password == "xxxx-xxxx-xxxx-xxxx"

    def test_env_var_takes_priority_over_config(self, tmp_config, monkeypatch):
        config_store.save_config("config@icloud.com", "config-pass")
        monkeypatch.setenv("APPLE_ID", "env@icloud.com")
        monkeypatch.setenv("APPLE_APP_PASSWORD", "env-pass")

        from calbridge.integration.caldav_client import CalDAVClient

        client = CalDAVClient()
        assert client._apple_id == "env@icloud.com"
        assert client._app_password == "env-pass"

    def test_constructor_args_take_priority_over_config(self, tmp_config, monkeypatch):
        config_store.save_config("config@icloud.com", "config-pass")
        monkeypatch.delenv("APPLE_ID", raising=False)
        monkeypatch.delenv("APPLE_APP_PASSWORD", raising=False)

        from calbridge.integration.caldav_client import CalDAVClient

        client = CalDAVClient(apple_id="arg@icloud.com", app_password="arg-pass")
        assert client._apple_id == "arg@icloud.com"
        assert client._app_password == "arg-pass"
