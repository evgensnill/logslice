"""Tests for logslice.sorter and logslice.sorter_config."""

import re
import pytest

from logslice.sorter import sort_lines, DEFAULT_TIMESTAMP_RE, _sort_key_timestamp
from logslice.sorter_config import SorterConfig, validate, from_dict


# ---------------------------------------------------------------------------
# sort_lines — text key
# ---------------------------------------------------------------------------

class TestSortLinesText:
    def test_sorts_ascending(self):
        lines = ["banana\n", "apple\n", "cherry\n"]
        result = list(sort_lines(lines, key="text"))
        assert result == ["apple\n", "banana\n", "cherry\n"]

    def test_sorts_descending(self):
        lines = ["banana\n", "apple\n", "cherry\n"]
        result = list(sort_lines(lines, key="text", reverse=True))
        assert result == ["cherry\n", "banana\n", "apple\n"]

    def test_empty_input(self):
        assert list(sort_lines([], key="text")) == []

    def test_single_line(self):
        assert list(sort_lines(["only\n"])) == ["only\n"]

    def test_invalid_key_raises(self):
        with pytest.raises(ValueError, match="Unknown sort key"):
            list(sort_lines(["a"], key="invalid"))


# ---------------------------------------------------------------------------
# sort_lines — timestamp key
# ---------------------------------------------------------------------------

class TestSortLinesTimestamp:
    LINES = [
        "2024-03-15 10:05:00 INFO  third\n",
        "2024-03-15 08:00:00 DEBUG first\n",
        "2024-03-15 09:30:00 WARN  second\n",
    ]

    def test_sorts_by_timestamp_ascending(self):
        result = list(sort_lines(self.LINES, key="timestamp"))
        assert result[0].startswith("2024-03-15 08:00:00")
        assert result[-1].startswith("2024-03-15 10:05:00")

    def test_sorts_by_timestamp_descending(self):
        result = list(sort_lines(self.LINES, key="timestamp", reverse=True))
        assert result[0].startswith("2024-03-15 10:05:00")

    def test_fallback_for_no_timestamp(self):
        lines = ["no-ts-line\n", "2024-01-01 00:00:00 with-ts\n"]
        result = list(sort_lines(lines, key="timestamp"))
        # Should not raise; lines without timestamps sort by raw text
        assert len(result) == 2

    def test_custom_timestamp_pattern(self):
        pattern = re.compile(r"ts=(\d+)")
        lines = ["ts=300 c\n", "ts=100 a\n", "ts=200 b\n"]
        result = list(sort_lines(lines, key="timestamp", timestamp_pattern=pattern))
        assert result[0] == "ts=100 a\n"


# ---------------------------------------------------------------------------
# SorterConfig defaults
# ---------------------------------------------------------------------------

class TestSorterConfigDefaults:
    def setup_method(self):
        self.cfg = SorterConfig()

    def test_default_enabled_is_false(self):
        assert self.cfg.enabled is False

    def test_default_key_is_text(self):
        assert self.cfg.key == "text"

    def test_default_reverse_is_false(self):
        assert self.cfg.reverse is False

    def test_default_timestamp_pattern_is_none(self):
        assert self.cfg.timestamp_pattern is None


# ---------------------------------------------------------------------------
# validate / from_dict
# ---------------------------------------------------------------------------

class TestSorterConfigValidation:
    def test_invalid_key_raises(self):
        cfg = SorterConfig(key="bad")
        with pytest.raises(ValueError, match="key"):
            validate(cfg)

    def test_invalid_regex_raises(self):
        cfg = SorterConfig(timestamp_pattern="[invalid")
        with pytest.raises(ValueError, match="regex"):
            validate(cfg)

    def test_from_dict_defaults(self):
        cfg = from_dict({})
        assert cfg.enabled is False
        assert cfg.key == "text"

    def test_from_dict_custom_values(self):
        cfg = from_dict({"enabled": True, "key": "timestamp", "reverse": True})
        assert cfg.enabled is True
        assert cfg.key == "timestamp"
        assert cfg.reverse is True

    def test_from_dict_invalid_key_raises(self):
        with pytest.raises(ValueError):
            from_dict({"key": "unknown"})
