"""Tests for logslice.splitter and logslice.splitter_config."""

import pytest

from logslice.splitter import split_by_count, split_by_size, split_lines
from logslice.splitter_config import SplitterConfig, validate, from_dict


# ---------------------------------------------------------------------------
# split_by_count
# ---------------------------------------------------------------------------

class TestSplitByCount:
    def test_even_split(self):
        lines = ["a\n", "b\n", "c\n", "d\n"]
        result = list(split_by_count(lines, 2))
        assert result == [["a\n", "b\n"], ["c\n", "d\n"]]

    def test_uneven_split(self):
        lines = ["a\n", "b\n", "c\n"]
        result = list(split_by_count(lines, 2))
        assert result == [["a\n", "b\n"], ["c\n"]]

    def test_chunk_larger_than_input(self):
        lines = ["a\n", "b\n"]
        result = list(split_by_count(lines, 10))
        assert result == [["a\n", "b\n"]]

    def test_empty_input(self):
        assert list(split_by_count([], 5)) == []

    def test_invalid_chunk_size_raises(self):
        with pytest.raises(ValueError):
            list(split_by_count(["a\n"], 0))


# ---------------------------------------------------------------------------
# split_by_size
# ---------------------------------------------------------------------------

class TestSplitBySize:
    def test_splits_on_byte_boundary(self):
        # each line is 2 bytes ("a\n"), max_bytes=4 => 2 lines per chunk
        lines = ["a\n", "b\n", "c\n", "d\n"]
        result = list(split_by_size(lines, 4))
        assert result == [["a\n", "b\n"], ["c\n", "d\n"]]

    def test_single_line_exceeds_limit_still_emitted(self):
        lines = ["hello world\n"]  # 12 bytes
        result = list(split_by_size(lines, 4))
        assert result == [["hello world\n"]]

    def test_empty_input(self):
        assert list(split_by_size([], 100)) == []

    def test_invalid_max_bytes_raises(self):
        with pytest.raises(ValueError):
            list(split_by_size(["a\n"], -1))


# ---------------------------------------------------------------------------
# split_lines (dispatcher)
# ---------------------------------------------------------------------------

class TestSplitLines:
    def test_delegates_to_count(self):
        lines = ["a\n", "b\n", "c\n"]
        result = list(split_lines(lines, chunk_size=2))
        assert len(result) == 2

    def test_delegates_to_size(self):
        lines = ["a\n", "b\n"]
        result = list(split_lines(lines, max_bytes=100))
        assert result == [["a\n", "b\n"]]

    def test_both_raises(self):
        with pytest.raises(ValueError, match="not both"):
            list(split_lines(["a\n"], chunk_size=2, max_bytes=10))

    def test_neither_raises(self):
        with pytest.raises(ValueError):
            list(split_lines(["a\n"]))


# ---------------------------------------------------------------------------
# SplitterConfig
# ---------------------------------------------------------------------------

class TestSplitterConfigDefaults:
    def test_default_enabled_is_false(self):
        assert SplitterConfig().enabled is False

    def test_default_chunk_size_is_none(self):
        assert SplitterConfig().chunk_size is None

    def test_default_max_bytes_is_none(self):
        assert SplitterConfig().max_bytes is None


class TestSplitterConfigValidation:
    def test_disabled_config_is_always_valid(self):
        validate(SplitterConfig(enabled=False))  # no exception

    def test_enabled_with_chunk_size_is_valid(self):
        validate(SplitterConfig(enabled=True, chunk_size=100))

    def test_enabled_with_max_bytes_is_valid(self):
        validate(SplitterConfig(enabled=True, max_bytes=1024))

    def test_both_set_raises(self):
        with pytest.raises(ValueError):
            validate(SplitterConfig(enabled=True, chunk_size=10, max_bytes=100))

    def test_neither_set_raises(self):
        with pytest.raises(ValueError):
            validate(SplitterConfig(enabled=True))

    def test_zero_chunk_size_raises(self):
        with pytest.raises(ValueError):
            validate(SplitterConfig(enabled=True, chunk_size=0))

    def test_from_dict_builds_config(self):
        cfg = from_dict({"enabled": True, "chunk_size": 50})
        assert cfg.enabled is True
        assert cfg.chunk_size == 50
