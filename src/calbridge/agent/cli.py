"""Click CLI entry point — routes OpenClaw commands to the SDK layer."""

import json
import logging
import logging.config
import os
from pathlib import Path

import click
from dotenv import load_dotenv

from ..integration.caldav_client import AuthenticationError, NetworkError
from ..integration.permission_manager import PermissionDeniedError, PermissionRestrictedError
from ..sdk.calendar_sdk import CalendarSDK
from ..sdk.reminder_sdk import ReminderSDK
from ..shared.config_store import CONFIG_FILE, save_config
from ..shared.constants import ERROR_CODES
from ..shared.validators import ValidationError
from .responses import error_response, success_response
from .tools import ALL_TOOLS

_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "logging_config.json"


def _setup_logging() -> None:
    """Load JSON logging config if available; skipped in test environments."""
    if os.environ.get("APPLE_SYNC_DISABLE_LOGGING", "false").lower() == "true":
        return
    if _CONFIG_PATH.exists():
        with _CONFIG_PATH.open() as f:
            cfg = json.load(f)
            cfg["version"] = 1
            logging.config.dictConfig(cfg)


def _out(data: dict) -> None:
    """Print a dict as readable JSON with Unicode preserved."""
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))


@click.group()
def cli() -> None:
    """Apple Calendar & Reminders headless CLI for OpenClaw Agent."""
    load_dotenv()
    _setup_logging()


def _mock_mode() -> bool:
    """Detect mock mode from environment."""
    return os.environ.get("APPLE_SYNC_MOCK", "false").lower() == "true"


def _handle_error(exc: Exception) -> dict:
    """Convert known exceptions to standardized error responses."""
    if isinstance(exc, (AuthenticationError, PermissionDeniedError)):
        return error_response(
            ERROR_CODES["AUTH_FAILED"],
            str(exc),
            "Set APPLE_ID and APPLE_APP_PASSWORD environment variables.",
        )
    if isinstance(exc, NetworkError):
        return error_response(ERROR_CODES["NETWORK_ERROR"], str(exc))
    if isinstance(exc, PermissionRestrictedError):
        return error_response(ERROR_CODES["AUTH_FAILED"], str(exc))
    if isinstance(exc, ValidationError):
        return error_response(ERROR_CODES["VALIDATION_ERROR"], str(exc))
    return error_response(ERROR_CODES["UNKNOWN_ERROR"], str(exc))


@cli.command("read-events")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD or today/tomorrow/yesterday)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD or today/tomorrow/yesterday)")
@click.option("--calendar", default=None, help="Filter by calendar name")
def read_events(start: str, end: str, calendar: str | None) -> None:
    """Read calendar events and print JSON to stdout."""
    try:
        _out(
            success_response(CalendarSDK(mock_mode=_mock_mode()).read_events(start, end, calendar))
        )
    except Exception as exc:  # noqa: BLE001
        _out(_handle_error(exc))
        raise SystemExit(1) from exc


@cli.command("create-event")
@click.option("--title", required=True, help="Event title")
@click.option("--start", required=True, help="Start datetime (YYYY-MM-DDTHH:MM:SS)")
@click.option("--end", required=True, help="End datetime (YYYY-MM-DDTHH:MM:SS)")
@click.option("--calendar", default=None, help="Target calendar name")
@click.option("--location", default="", help="Event location")
@click.option("--notes", default="", help="Event notes")
@click.option(
    "--recurrence",
    default=None,
    type=click.Choice(["daily", "weekly", "monthly", "yearly"]),
    help="Recurrence frequency",
)
@click.option("--recurrence-count", default=None, type=int, help="Stop after N occurrences")
@click.option("--recurrence-until", default=None, help="Stop recurrence on date (YYYY-MM-DD)")
@click.option(
    "--alert",
    "alert_minutes",
    default=None,
    type=int,
    help="Alert N minutes before event (e.g. 15)",
)
def create_event(
    title: str,
    start: str,
    end: str,
    calendar: str | None,
    location: str,
    notes: str,
    recurrence: str | None,
    recurrence_count: int | None,
    recurrence_until: str | None,
    alert_minutes: int | None,
) -> None:
    """Create a calendar event and print JSON to stdout."""
    try:
        data = CalendarSDK(mock_mode=_mock_mode()).create_event(
            title,
            start,
            end,
            calendar_name=calendar,
            location=location,
            notes=notes,
            recurrence=recurrence,
            recurrence_count=recurrence_count,
            recurrence_until=recurrence_until,
            alert_minutes=alert_minutes,
        )
        _out(success_response(data))
    except Exception as exc:  # noqa: BLE001
        _out(_handle_error(exc))
        raise SystemExit(1) from exc


@cli.command("create-reminder")
@click.option("--title", required=True, help="Reminder title")
@click.option("--notes", default="", help="Reminder notes")
@click.option("--due-date", default=None, help="Due datetime (YYYY-MM-DDTHH:MM:SS)")
@click.option("--priority", default=0, type=int, help="Priority 0-9")
@click.option("--list", "list_name", default=None, help="Target reminder list")
@click.option(
    "--alert",
    "alert_minutes",
    default=None,
    type=int,
    help="Alert N minutes before due date (e.g. 30)",
)
def create_reminder(
    title: str,
    notes: str,
    due_date: str | None,
    priority: int,
    list_name: str | None,
    alert_minutes: int | None,
) -> None:
    """Create a reminder and print JSON to stdout."""
    try:
        data = ReminderSDK(mock_mode=_mock_mode()).create_reminder(
            title,
            notes=notes,
            due_date=due_date,
            priority=priority,
            list_name=list_name,
            alert_minutes=alert_minutes,
        )
        _out(success_response(data))
    except Exception as exc:  # noqa: BLE001
        _out(_handle_error(exc))
        raise SystemExit(1) from exc


@cli.command("configure")
def configure() -> None:
    """Interactively save Apple credentials to ~/.config/calbridge/config.json."""
    click.echo("CalBridge — one-time credential setup")
    click.echo(f"Credentials will be stored in: {CONFIG_FILE}\n")
    apple_id = click.prompt("Apple ID (iCloud email)")
    app_password = click.prompt(
        "App-Specific Password (generate at appleid.apple.com → App-Specific Passwords)",
        hide_input=True,
    )
    save_config(apple_id, app_password)
    click.echo(
        "\nCredentials saved. Run `calbridge read-events --start today --end today` to test."
    )


@cli.command("list-tools")
def list_tools() -> None:
    """Print all available OpenClaw tool schemas as JSON."""
    _out(ALL_TOOLS)
