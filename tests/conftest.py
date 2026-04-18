"""Shared pytest fixtures for unit and integration tests."""

import logging
import pytest

from apple_sync.integration.mock_store import MockCalDAVStore, MockVEvent, MockVTodo


@pytest.fixture(autouse=True)
def suppress_logging():
    """Silence apple_sync loggers during tests to keep CLI output clean."""
    logging.getLogger("apple_sync").setLevel(logging.CRITICAL)


@pytest.fixture(autouse=True)
def mock_mode_env(monkeypatch):
    """Ensure all tests run in mock mode, bypassing Apple CalDAV network calls."""
    monkeypatch.setenv("APPLE_SYNC_MOCK", "true")
    monkeypatch.setenv("MOCK_AUTH_FAIL", "false")
    monkeypatch.setenv("APPLE_SYNC_DISABLE_LOGGING", "true")


@pytest.fixture()
def mock_store():
    """Return a fresh MockCalDAVStore loaded with fixture data."""
    return MockCalDAVStore()


@pytest.fixture()
def sample_event():
    """Return a single MockVEvent for assertion tests."""
    return MockVEvent({
        "id": "test-001",
        "title": "Test Event",
        "start": "2026-04-17T10:00:00",
        "end": "2026-04-17T11:00:00",
        "calendar": "Work",
        "location": "Office",
        "notes": "Test notes",
    })


@pytest.fixture()
def sample_reminder():
    """Return a single MockVTodo for assertion tests."""
    return MockVTodo({
        "id": "test-rem-001",
        "title": "Test Reminder",
        "notes": "Test notes",
        "due_date": "2026-04-17T18:00:00",
        "priority": 5,
        "list": "Work",
    })
