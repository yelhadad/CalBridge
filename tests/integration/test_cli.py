"""Integration tests for the Click CLI using CliRunner."""

import json

import pytest
from click.testing import CliRunner

from apple_sync.agent.cli import cli


@pytest.fixture()
def runner():
    return CliRunner()


class TestReadEventsCommand:
    def test_json_output_structure(self, runner):
        result = runner.invoke(cli, ["read-events", "--start", "2026-04-17", "--end", "2026-04-17"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "success"
        assert isinstance(data["data"], list)

    def test_with_calendar_filter(self, runner):
        result = runner.invoke(
            cli,
            ["read-events", "--start", "2026-04-17", "--end", "2026-04-17", "--calendar", "Work"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "success"

    def test_invalid_date_returns_error_json(self, runner):
        result = runner.invoke(cli, ["read-events", "--start", "bad-date", "--end", "2026-04-17"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "error"


class TestCreateEventCommand:
    def test_json_output_structure(self, runner):
        result = runner.invoke(
            cli,
            [
                "create-event",
                "--title", "Test Meeting",
                "--start", "2026-04-17T10:00:00",
                "--end", "2026-04-17T11:00:00",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "success"
        assert data["data"]["title"] == "Test Meeting"

    def test_with_optional_fields(self, runner):
        result = runner.invoke(
            cli,
            [
                "create-event",
                "--title", "Meeting",
                "--start", "2026-04-17T14:00:00",
                "--end", "2026-04-17T15:00:00",
                "--location", "Office",
                "--notes", "Bring docs",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"]["location"] == "Office"

    def test_invalid_title_returns_error(self, runner):
        result = runner.invoke(
            cli,
            ["create-event", "--title", "", "--start", "2026-04-17T10:00:00",
             "--end", "2026-04-17T11:00:00"],
        )
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "error"


class TestCreateReminderCommand:
    def test_json_output_structure(self, runner):
        result = runner.invoke(cli, ["create-reminder", "--title", "Buy milk"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "success"
        assert data["data"]["title"] == "Buy milk"

    def test_with_due_date_and_priority(self, runner):
        result = runner.invoke(
            cli,
            [
                "create-reminder",
                "--title", "Submit report",
                "--due-date", "2026-04-20T09:00:00",
                "--priority", "7",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"]["priority"] == 7

    def test_auth_failure_returns_error_json(self, runner, monkeypatch):
        monkeypatch.setenv("MOCK_AUTH_FAIL", "true")
        result = runner.invoke(cli, ["create-reminder", "--title", "Task"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "error"
        assert data["error"]["code"] == "AUTH_FAILED"


class TestListToolsCommand:
    def test_outputs_json_array(self, runner):
        result = runner.invoke(cli, ["list-tools"])
        assert result.exit_code == 0
        tools = json.loads(result.output)
        assert isinstance(tools, list)
        assert len(tools) == 3

    def test_tool_names_present(self, runner):
        result = runner.invoke(cli, ["list-tools"])
        tools = json.loads(result.output)
        names = [t["name"] for t in tools]
        assert "read_calendar_events" in names
        assert "create_calendar_event" in names
        assert "create_reminder" in names
