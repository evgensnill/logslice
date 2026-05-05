"""Tests for logslice.formatter module."""

import json
from datetime import datetime

import pytest

from logslice.formatter import (
    format_line_csv,
    format_line_json,
    format_line_plain,
    format_lines,
)


SAMPLE_TS = datetime(2024, 3, 15, 12, 0, 0)
SAMPLE_LINE = "2024-03-15 12:00:00 ERROR Something went wrong"


class TestFormatLinePlain:
    def test_strips_trailing_newline(self):
        assert format_line_plain("hello\n") == "hello"

    def test_with_line_number(self):
        assert format_line_plain("hello", line_number=5) == "5: hello"

    def test_without_line_number(self):
        assert format_line_plain("hello") == "hello"


class TestFormatLineJson:
    def test_basic_output(self):
        result = json.loads(format_line_json(SAMPLE_LINE))
        assert result["message"] == SAMPLE_LINE
        assert "line_number" not in result
        assert "timestamp" not in result

    def test_with_line_number(self):
        result = json.loads(format_line_json(SAMPLE_LINE, line_number=42))
        assert result["line_number"] == 42

    def test_with_timestamp(self):
        result = json.loads(format_line_json(SAMPLE_LINE, timestamp=SAMPLE_TS))
        assert result["timestamp"] == SAMPLE_TS.isoformat()

    def test_strips_newline_from_message(self):
        result = json.loads(format_line_json("msg\n"))
        assert result["message"] == "msg"


class TestFormatLineCsv:
    def test_basic_output(self):
        result = format_line_csv(SAMPLE_LINE)
        assert SAMPLE_LINE in result

    def test_with_line_number(self):
        result = format_line_csv("error", line_number=3)
        parts = result.split(",")
        assert parts[0] == "3"

    def test_with_timestamp(self):
        result = format_line_csv("error", timestamp=SAMPLE_TS)
        assert SAMPLE_TS.isoformat() in result


class TestFormatLines:
    def test_plain_format(self):
        lines = ["line one\n", "line two\n"]
        result = format_lines(lines, fmt="plain")
        assert result == ["line one", "line two"]

    def test_json_format_returns_valid_json(self):
        lines = ["error occurred\n"]
        result = format_lines(lines, fmt="json")
        parsed = json.loads(result[0])
        assert parsed["message"] == "error occurred"

    def test_csv_format(self):
        lines = ["warn: disk full\n"]
        result = format_lines(lines, fmt="csv")
        assert "warn: disk full" in result[0]

    def test_include_line_numbers(self):
        lines = ["a\n", "b\n"]
        result = format_lines(lines, fmt="plain", include_line_numbers=True, start_number=10)
        assert result[0] == "10: a"
        assert result[1] == "11: b"

    def test_unsupported_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported format"):
            format_lines(["line\n"], fmt="xml")

    def test_timestamps_passed_to_json(self):
        lines = ["msg\n"]
        result = format_lines(lines, fmt="json", timestamps=[SAMPLE_TS])
        parsed = json.loads(result[0])
        assert parsed["timestamp"] == SAMPLE_TS.isoformat()
