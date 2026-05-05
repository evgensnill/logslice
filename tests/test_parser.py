"""Tests for logslice.parser module."""

import pytest
from datetime import datetime
from logslice.parser import filter_lines, parse_timestamp, DEFAULT_TIMESTAMP_FORMATS


SAMPLE_LINES = [
    "2024-01-15 08:00:01 INFO  Application started",
    "2024-01-15 08:05:10 DEBUG Connecting to database",
    "2024-01-15 08:10:22 ERROR Failed to connect: timeout",
    "2024-01-15 09:00:00 INFO  Retry successful",
    "2024-01-15 09:30:45 WARN  High memory usage detected",
    "No timestamp line — plain text entry",
]


class TestParseTimestamp:
    def test_parses_iso_like_format(self):
        line = "2024-01-15 08:00:01 INFO Application started"
        ts = parse_timestamp(line)
        assert ts == datetime(2024, 1, 15, 8, 0, 1)

    def test_returns_none_for_no_timestamp(self):
        assert parse_timestamp("No timestamp here") is None

    def test_custom_format(self):
        line = "2024-01-15T12:30:00 some event"
        ts = parse_timestamp(line, ["%Y-%m-%dT%H:%M:%S"])
        assert ts == datetime(2024, 1, 15, 12, 30, 0)


class TestFilterLines:
    def test_no_filters_returns_all(self):
        result = list(filter_lines(iter(SAMPLE_LINES)))
        assert len(result) == len(SAMPLE_LINES)

    def test_regex_filter_matches(self):
        result = list(filter_lines(iter(SAMPLE_LINES), pattern=r"ERROR"))
        assert len(result) == 1
        assert "Failed to connect" in result[0]

    def test_regex_filter_invert(self):
        result = list(filter_lines(iter(SAMPLE_LINES), pattern=r"INFO", invert=True))
        assert all("INFO" not in line for line in result)

    def test_start_time_filter(self):
        start = datetime(2024, 1, 15, 9, 0, 0)
        result = list(filter_lines(iter(SAMPLE_LINES), start_time=start))
        # Lines without a timestamp pass through; timestamped lines must be >= start
        timestamped_results = [r for r in result if parse_timestamp(r) is not None]
        for line in timestamped_results:
            assert parse_timestamp(line) >= start

    def test_end_time_filter(self):
        end = datetime(2024, 1, 15, 8, 10, 0)
        result = list(filter_lines(iter(SAMPLE_LINES), end_time=end))
        timestamped_results = [r for r in result if parse_timestamp(r) is not None]
        for line in timestamped_results:
            assert parse_timestamp(line) <= end

    def test_combined_time_and_pattern(self):
        start = datetime(2024, 1, 15, 8, 0, 0)
        end = datetime(2024, 1, 15, 8, 59, 59)
        result = list(
            filter_lines(iter(SAMPLE_LINES), pattern=r"INFO|ERROR", start_time=start, end_time=end)
        )
        assert len(result) == 2
        assert any("Application started" in r for r in result)
        assert any("Failed to connect" in r for r in result)

    def test_no_timestamp_lines_pass_time_filter(self):
        lines = ["No timestamp line — plain text entry"]
        result = list(filter_lines(iter(lines), start_time=datetime(2099, 1, 1)))
        # Lines with no parseable timestamp are not excluded by time filters
        assert result == ["No timestamp line — plain text entry"]
