"""Tests for logslice.deduplicator."""

import pytest
from logslice.deduplicator import _line_key, deduplicate_lines


class TestLineKey:
    def test_same_line_produces_same_key(self):
        assert _line_key("hello world") == _line_key("hello world")

    def test_different_lines_produce_different_keys(self):
        assert _line_key("hello world") != _line_key("goodbye world")

    def test_key_is_hex_string(self):
        key = _line_key("some log line")
        int(key, 16)  # should not raise

    def test_trailing_newline_ignored(self):
        assert _line_key("line\n") == _line_key("line")

    def test_skip_fields_ignores_leading_tokens(self):
        key_a = _line_key("2024-01-01 12:00:00 ERROR disk full", fields=2)
        key_b = _line_key("2024-01-02 09:15:33 ERROR disk full", fields=2)
        assert key_a == key_b

    def test_skip_fields_different_messages(self):
        key_a = _line_key("2024-01-01 12:00:00 ERROR disk full", fields=2)
        key_b = _line_key("2024-01-01 12:00:00 ERROR out of memory", fields=2)
        assert key_a != key_b

    def test_skip_fields_fewer_tokens_than_fields(self):
        # Should not raise; falls back to full line
        key = _line_key("short", fields=5)
        assert isinstance(key, str)


class TestDeduplicateLines:
    def test_unique_lines_all_returned(self):
        lines = ["alpha\n", "beta\n", "gamma\n"]
        result = list(deduplicate_lines(lines))
        assert result == lines

    def test_duplicate_lines_removed(self):
        lines = ["alpha\n", "beta\n", "alpha\n", "gamma\n", "beta\n"]
        result = list(deduplicate_lines(lines))
        assert result == ["alpha\n", "beta\n", "gamma\n"]

    def test_empty_input(self):
        assert list(deduplicate_lines([])) == []

    def test_skip_fields_deduplicates_by_message(self):
        lines = [
            "2024-01-01 00:00:01 ERROR disk full\n",
            "2024-01-01 00:00:02 ERROR disk full\n",
            "2024-01-01 00:00:03 WARN low memory\n",
        ]
        result = list(deduplicate_lines(lines, skip_fields=2))
        assert len(result) == 2
        assert result[0] == lines[0]
        assert result[1] == lines[2]

    def test_max_seen_clears_cache(self):
        # After clearing, a previously seen line should pass through again
        lines = ["line_a\n", "line_b\n", "line_a\n"]
        # max_seen=1 forces a clear after the second unique line
        result = list(deduplicate_lines(lines, max_seen=1))
        # line_a appears twice because the cache was cleared
        assert result.count("line_a\n") == 2

    def test_returns_iterator(self):
        import types
        result = deduplicate_lines(["x\n"])
        assert isinstance(result, types.GeneratorType)
