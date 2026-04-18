"""OpenClaw tool schema definitions for all calbridge capabilities."""

READ_CALENDAR_TOOL_SCHEMA: dict = {
    "name": "read_calendar_events",
    "description": "Read Apple Calendar events within a date range.",
    "parameters": {
        "type": "object",
        "required": ["start", "end"],
        "properties": {
            "start": {
                "type": "string",
                "description": "Start date: 'today', 'tomorrow', 'yesterday', or YYYY-MM-DD",
            },
            "end": {
                "type": "string",
                "description": "End date: 'today', 'tomorrow', 'yesterday', or YYYY-MM-DD",
            },
            "calendar_name": {
                "type": "string",
                "description": "Optional calendar name to filter results",
            },
        },
    },
    "returns": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "start": {"type": "string", "format": "date-time"},
                "end": {"type": "string", "format": "date-time"},
                "calendar": {"type": "string"},
                "location": {"type": "string"},
                "notes": {"type": "string"},
            },
        },
    },
}

CREATE_EVENT_TOOL_SCHEMA: dict = {
    "name": "create_calendar_event",
    "description": "Create a new Apple Calendar event.",
    "parameters": {
        "type": "object",
        "required": ["title", "start_datetime", "end_datetime"],
        "properties": {
            "title": {"type": "string", "description": "Event title (required)"},
            "start_datetime": {
                "type": "string",
                "format": "date-time",
                "description": "Start datetime in YYYY-MM-DDTHH:MM:SS",
            },
            "end_datetime": {
                "type": "string",
                "format": "date-time",
                "description": "End datetime in YYYY-MM-DDTHH:MM:SS",
            },
            "calendar_name": {"type": "string", "description": "Target calendar name"},
            "location": {"type": "string", "description": "Event location"},
            "notes": {"type": "string", "description": "Event notes"},
        },
    },
    "returns": {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "title": {"type": "string"},
            "start": {"type": "string"},
            "end": {"type": "string"},
            "calendar": {"type": "string"},
        },
    },
}

CREATE_REMINDER_TOOL_SCHEMA: dict = {
    "name": "create_reminder",
    "description": "Create a new Apple Reminder.",
    "parameters": {
        "type": "object",
        "required": ["title"],
        "properties": {
            "title": {"type": "string", "description": "Reminder title (required)"},
            "notes": {"type": "string", "description": "Reminder notes"},
            "due_date": {
                "type": "string",
                "format": "date-time",
                "description": "Due date in YYYY-MM-DDTHH:MM:SS",
            },
            "priority": {
                "type": "integer",
                "minimum": 0,
                "maximum": 9,
                "description": "Priority 0 (none) to 9 (high)",
            },
            "list_name": {"type": "string", "description": "Target reminder list name"},
        },
    },
    "returns": {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "title": {"type": "string"},
            "due_date": {"type": "string"},
            "priority": {"type": "integer"},
            "list": {"type": "string"},
        },
    },
}

ALL_TOOLS: list[dict] = [
    READ_CALENDAR_TOOL_SCHEMA,
    CREATE_EVENT_TOOL_SCHEMA,
    CREATE_REMINDER_TOOL_SCHEMA,
]
