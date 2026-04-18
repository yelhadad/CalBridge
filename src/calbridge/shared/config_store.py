"""Persistent config store for calbridge credentials (~/.config/calbridge/config.json).

Stores credentials locally so OpenClaw can invoke the CLI without
injecting env vars on every call. File is chmod 600 (owner-read only).
"""

import json
import logging
import os
import stat
from pathlib import Path
from typing import Any

logger = logging.getLogger("calbridge.config_store")

CONFIG_DIR = Path.home() / ".config" / "calbridge"
CONFIG_FILE = CONFIG_DIR / "config.json"

_APPLE_ID_KEY = "apple_id"
_APP_PASSWORD_KEY = "apple_app_password"  # noqa: S105


def load_config() -> dict[str, Any]:
    """Read config file and return its contents, or empty dict if missing."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with CONFIG_FILE.open() as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read config file %s: %s", CONFIG_FILE, exc)
        return {}


def save_config(apple_id: str, app_password: str) -> None:
    """Write credentials to config file with owner-only permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {_APPLE_ID_KEY: apple_id, _APP_PASSWORD_KEY: app_password}
    with CONFIG_FILE.open("w") as f:
        json.dump(data, f, indent=2)
    # Restrict to owner read/write only — credentials must not be world-readable
    os.chmod(CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)
    logger.info("Config saved to %s", CONFIG_FILE)


def get_apple_id() -> str:
    """Return apple_id from config file, or empty string if not set."""
    return str(load_config().get(_APPLE_ID_KEY, ""))


def get_app_password() -> str:
    """Return apple_app_password from config file, or empty string if not set."""
    return str(load_config().get(_APP_PASSWORD_KEY, ""))
