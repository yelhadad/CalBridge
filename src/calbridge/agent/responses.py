"""Standardized agent response builders for OpenClaw consumption."""

from typing import Any


def success_response(data: Any) -> dict[str, Any]:
    """Wrap successful operation data in the standard envelope."""
    return {"status": "success", "data": data, "error": None}


def error_response(
    code: str,
    message: str,
    remediation: str = "",
) -> dict[str, Any]:
    """Wrap error details in the standard envelope with optional remediation."""
    return {
        "status": "error",
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "remediation": remediation,
        },
    }
