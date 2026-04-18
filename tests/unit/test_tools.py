"""Unit tests for OpenClaw tool schema definitions."""

import json

from apple_sync.agent.tools import (
    ALL_TOOLS,
    CREATE_EVENT_TOOL_SCHEMA,
    CREATE_REMINDER_TOOL_SCHEMA,
    READ_CALENDAR_TOOL_SCHEMA,
)


class TestReadCalendarSchema:
    def test_is_valid_json_serializable(self):
        assert json.dumps(READ_CALENDAR_TOOL_SCHEMA)

    def test_has_name(self):
        assert READ_CALENDAR_TOOL_SCHEMA["name"] == "read_calendar_events"

    def test_has_required_params(self):
        required = READ_CALENDAR_TOOL_SCHEMA["parameters"]["required"]
        assert "start" in required
        assert "end" in required

    def test_has_returns(self):
        assert "returns" in READ_CALENDAR_TOOL_SCHEMA


class TestCreateEventSchema:
    def test_is_valid_json_serializable(self):
        assert json.dumps(CREATE_EVENT_TOOL_SCHEMA)

    def test_has_name(self):
        assert CREATE_EVENT_TOOL_SCHEMA["name"] == "create_calendar_event"

    def test_required_params(self):
        required = CREATE_EVENT_TOOL_SCHEMA["parameters"]["required"]
        assert "title" in required
        assert "start_datetime" in required
        assert "end_datetime" in required


class TestCreateReminderSchema:
    def test_is_valid_json_serializable(self):
        assert json.dumps(CREATE_REMINDER_TOOL_SCHEMA)

    def test_has_name(self):
        assert CREATE_REMINDER_TOOL_SCHEMA["name"] == "create_reminder"

    def test_required_params(self):
        required = CREATE_REMINDER_TOOL_SCHEMA["parameters"]["required"]
        assert "title" in required

    def test_priority_constraints(self):
        priority = CREATE_REMINDER_TOOL_SCHEMA["parameters"]["properties"]["priority"]
        assert priority["minimum"] == 0
        assert priority["maximum"] == 9


class TestAllTools:
    def test_length(self):
        assert len(ALL_TOOLS) == 3

    def test_all_have_names(self):
        for tool in ALL_TOOLS:
            assert "name" in tool

    def test_all_serializable(self):
        assert json.dumps(ALL_TOOLS)
