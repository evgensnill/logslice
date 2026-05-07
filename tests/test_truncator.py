"""Tests for logslice.truncator."""

import pytest

from logslice.truncator import (
    DEFAULT_ELLIPSIS,
    DEFAULT_MAX_LENGTH,
    truncate_line,
    truncate_lines,
)


class TestTruncateLine:
    def test_short_line_unchanged(self):
        line = "short line"
        assert truncate_line(line, max_length=80) == line

    def test_exact_length_unchanged(self):
        line = "a" * 80
        assert truncate_line(line, max_length=80) == line

    def test_long_line_is_truncated(self):
        line = "a" * 100
        result = truncate_line(line, max_length=80)
        assert len(result) == 80
        assert result.endswith(DEFAULT_ELLIPSIS)

    def test_preserves_trailing_newline(self):
        line = "a" * 100 + "\n"
        result = truncate_line(line, max_length=80)
        assert result.endswith("\n")
        assert len(result) == 81  # 80 chars + newline

    def test_no_trailing_newline_not_added(self):
        line = "a" * 100
        result = truncate_line(line, max_length=80)
        assert not result.endswith("\n")

    def test_custom_ellipsis(self):
        line = "a" * 50
        result = truncate_line(line, max_length=20, ellipsis=">>")
        assert result == "a" * 18 + ">>"

    def test_zero_max_length_raises(self):
        with pytest.raises(ValueError, match="max_length must be a positive integer"):
            truncate_line("hello", max_length=0)

    def test_negative_max_length_raises(self):
        with pytest.raises(ValueError):
            truncate_line("hello", max_length=-5)

    def test_ellipsis_longer_than_max_length(self):
        # ellipsis itself is longer than max_length — content portion becomes empty
        line = "hello world"
        result = truncate_line(line, max_length=2, ellipsis="...")
        assert result == "..."

    def test_empty_line_unchanged(self):
        assert truncate_line("", max_length=10) == ""


class TestTruncateLines:
    def test_all_short_lines_unchanged(self):
        lines = ["foo\n", "bar\n", "baz\n"]
        assert truncate_lines(lines, max_length=80) == lines

    def test_long_lines_are_truncated(self):
        lines = ["a" * 200 + "\n", "b" * 200 + "\n"]
        result = truncate_lines(lines, max_length=50)
        for r in result:
            # 50 chars + newline
            assert len(r) == 51

    def test_empty_list_returns_empty(self):
        assert truncate_lines([]) == []

    def test_returns_new_list(self):
        lines = ["short\n"]
        result = truncate_lines(lines, max_length=80)
        assert result is not lines
