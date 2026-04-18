"""Unit tests for InputValidator — TDD Red-Green-Refactor."""

import pytest

from apple_sync.shared.validators import InputValidator, ValidationError


class TestValidateDateString:
    def test_valid_date(self):
        InputValidator.validate_date_string("2026-04-17")  # no exception

    def test_invalid_date_format(self):
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_date_string("17/04/2026")
        assert exc.value.field == "date"

    def test_invalid_date_not_a_date(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_date_string("not-a-date")

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_date_string(None)  # type: ignore[arg-type]

    def test_custom_field_name(self):
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_date_string("bad", field="start")
        assert exc.value.field == "start"


class TestValidateDatetimeString:
    def test_valid_datetime(self):
        InputValidator.validate_datetime_string("2026-04-17T10:00:00")

    def test_invalid_datetime_no_time(self):
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_datetime_string("2026-04-17")
        assert exc.value.field == "datetime"

    def test_invalid_datetime_garbage(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_datetime_string("garbage")

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_datetime_string(None)  # type: ignore[arg-type]


class TestValidatePriority:
    def test_valid_zero(self):
        InputValidator.validate_priority(0)

    def test_valid_nine(self):
        InputValidator.validate_priority(9)

    def test_valid_middle(self):
        InputValidator.validate_priority(5)

    def test_below_range(self):
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_priority(-1)
        assert exc.value.field == "priority"

    def test_above_range(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_priority(10)

    def test_float_raises(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_priority(5.0)  # type: ignore[arg-type]

    def test_string_raises(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_priority("high")  # type: ignore[arg-type]


class TestValidateNonEmptyString:
    def test_valid_string(self):
        InputValidator.validate_non_empty_string("hello", "title")

    def test_empty_string_raises(self):
        with pytest.raises(ValidationError) as exc:
            InputValidator.validate_non_empty_string("", "title")
        assert exc.value.field == "title"

    def test_whitespace_only_raises(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_non_empty_string("   ", "title")

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_non_empty_string(None, "title")  # type: ignore[arg-type]

    def test_too_long_title_raises(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_non_empty_string("x" * 256, "title")

    def test_notes_length_limit(self):
        # Notes allow 10000 chars; 10001 should fail
        with pytest.raises(ValidationError):
            InputValidator.validate_non_empty_string("x" * 10001, "notes")
