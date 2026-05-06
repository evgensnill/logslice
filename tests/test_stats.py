"""Tests for logslice.stats module."""

import pytest
from logslice.stats import ParseStats


class TestParseStatsDefaults:
    def test_initial_totals_are_zero(self):
        stats = ParseStats()
        assert stats.total_lines == 0
        assert stats.matched_lines == 0
        assert stats.skipped_lines == 0
        assert stats.error_lines == 0

    def test_initial_pattern_hits_empty(self):
        stats = ParseStats()
        assert stats.pattern_hits == {}

    def test_match_rate_zero_when_no_lines(self):
        stats = ParseStats()
        assert stats.match_rate == 0.0


class TestParseStatsRecording:
    def test_record_line_increments_total(self):
        stats = ParseStats()
        stats.record_line()
        stats.record_line()
        assert stats.total_lines == 2

    def test_record_match_increments_matched(self):
        stats = ParseStats()
        stats.record_match()
        assert stats.matched_lines == 1

    def test_record_match_with_pattern_tracks_hits(self):
        stats = ParseStats()
        stats.record_match(pattern="ERROR")
        stats.record_match(pattern="ERROR")
        stats.record_match(pattern="WARN")
        assert stats.pattern_hits["ERROR"] == 2
        assert stats.pattern_hits["WARN"] == 1

    def test_record_skip_increments_skipped(self):
        stats = ParseStats()
        stats.record_skip()
        assert stats.skipped_lines == 1

    def test_record_error_increments_errors(self):
        stats = ParseStats()
        stats.record_error()
        assert stats.error_lines == 1


class TestParseStatsMatchRate:
    def test_match_rate_calculation(self):
        stats = ParseStats(total_lines=10, matched_lines=4)
        assert stats.match_rate == pytest.approx(0.4)

    def test_match_rate_full(self):
        stats = ParseStats(total_lines=5, matched_lines=5)
        assert stats.match_rate == pytest.approx(1.0)


class TestParseStatsSummary:
    def test_summary_contains_totals(self):
        stats = ParseStats(total_lines=100, matched_lines=42, skipped_lines=10)
        summary = stats.summary()
        assert "100" in summary
        assert "42" in summary
        assert "10" in summary

    def test_to_dict_keys(self):
        stats = ParseStats(total_lines=5, matched_lines=3)
        d = stats.to_dict()
        assert "total_lines" in d
        assert "matched_lines" in d
        assert "match_rate" in d
        assert "pattern_hits" in d

    def test_to_dict_match_rate_rounded(self):
        stats = ParseStats(total_lines=3, matched_lines=1)
        d = stats.to_dict()
        assert d["match_rate"] == round(1 / 3, 4)
