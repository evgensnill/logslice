"""Tests for logslice.sampler."""

import pytest

from logslice.sampler import sample_lines, _line_hash_fraction


LINES = [f"line {i}\n" for i in range(1, 21)]  # 20 lines


class TestLineHashFraction:
    def test_returns_float_in_range(self):
        frac = _line_hash_fraction("hello world")
        assert 0.0 <= frac < 1.0

    def test_same_input_same_output(self):
        assert _line_hash_fraction("abc") == _line_hash_fraction("abc")

    def test_different_inputs_differ(self):
        assert _line_hash_fraction("abc") != _line_hash_fraction("xyz")


class TestSampleLinesEveryNth:
    def test_every_second_line(self):
        result = list(sample_lines(LINES, rate=1.0, every_nth=2))
        assert result == LINES[1::2]

    def test_every_first_line_returns_all(self):
        result = list(sample_lines(LINES, rate=1.0, every_nth=1))
        assert result == LINES

    def test_every_nth_zero_raises(self):
        with pytest.raises(ValueError, match="every_nth must be >= 1"):
            list(sample_lines(LINES, rate=1.0, every_nth=0))

    def test_every_nth_negative_raises(self):
        with pytest.raises(ValueError):
            list(sample_lines(LINES, rate=1.0, every_nth=-3))

    def test_empty_input(self):
        assert list(sample_lines([], rate=1.0, every_nth=2)) == []


class TestSampleLinesRate:
    def test_rate_one_returns_all(self):
        result = list(sample_lines(LINES, rate=1.0))
        assert result == LINES

    def test_rate_half_returns_roughly_half(self):
        result = list(sample_lines(LINES, rate=0.5))
        assert len(result) == 10

    def test_rate_zero_raises(self):
        with pytest.raises(ValueError, match="rate must be in the range"):
            list(sample_lines(LINES, rate=0.0))

    def test_rate_above_one_raises(self):
        with pytest.raises(ValueError):
            list(sample_lines(LINES, rate=1.1))

    def test_deterministic_same_result_twice(self):
        r1 = list(sample_lines(LINES, rate=0.5, deterministic=True))
        r2 = list(sample_lines(LINES, rate=0.5, deterministic=True))
        assert r1 == r2

    def test_deterministic_subset_of_input(self):
        result = list(sample_lines(LINES, rate=0.3, deterministic=True))
        assert all(line in LINES for line in result)

    def test_empty_input_rate(self):
        assert list(sample_lines([], rate=0.5)) == []
