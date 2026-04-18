"""Unit tests for agent response builders."""

from apple_sync.agent.responses import error_response, success_response


class TestSuccessResponse:
    def test_structure(self):
        resp = success_response({"key": "value"})
        assert resp["status"] == "success"
        assert resp["data"] == {"key": "value"}
        assert resp["error"] is None

    def test_list_data(self):
        resp = success_response([1, 2, 3])
        assert resp["data"] == [1, 2, 3]

    def test_empty_data(self):
        resp = success_response({})
        assert resp["status"] == "success"


class TestErrorResponse:
    def test_structure(self):
        resp = error_response("PERMISSION_DENIED", "Access denied")
        assert resp["status"] == "error"
        assert resp["data"] is None
        assert resp["error"]["code"] == "PERMISSION_DENIED"
        assert resp["error"]["message"] == "Access denied"

    def test_with_remediation(self):
        resp = error_response("PERMISSION_DENIED", "Access denied", "Grant in Settings")
        assert resp["error"]["remediation"] == "Grant in Settings"

    def test_without_remediation_is_empty_string(self):
        resp = error_response("VALIDATION_ERROR", "Bad input")
        assert resp["error"]["remediation"] == ""
