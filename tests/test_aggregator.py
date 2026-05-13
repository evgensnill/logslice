"""Tests for logslice.aggregator and logslice.aggregator_config."""

import pytest

from logslice.aggregator import aggregate_by_field, aggregate_by_pattern, top_n
from logslice.aggregator_config import AggregatorConfig, from_dict, validate


# ---------------------------------------------------------------------------
# aggregate_by_pattern
# ---------------------------------------------------------------------------

class TestAggregateByPattern:
    LINES = [
        "ERROR something went wrong\n",
        "INFO  all good\n",
        "ERROR disk full\n",
        "WARN  low memory\n",
        "ERROR timeout\n",
    ]

    def test_counts_matches(self):
        result = aggregate_by_pattern(self.LINES, r"ERROR")
        assert result["ERROR"] == 3

    def test_no_match_returns_empty(self):
        result = aggregate_by_pattern(self.LINES, r"CRITICAL")
        assert result == {}

    def test_capture_group(self):
        result = aggregate_by_pattern(self.LINES, r"(ERROR|INFO|WARN)", group=1)
        assert result["ERROR"] == 3
        assert result["INFO"] == 1
        assert result["WARN"] == 1

    def test_empty_input(self):
        assert aggregate_by_pattern([], r"ERROR") == {}


# ---------------------------------------------------------------------------
# aggregate_by_field
# ---------------------------------------------------------------------------

class TestAggregateByField:
    LINES = [
        "ERROR something\n",
        "INFO  all good\n",
        "ERROR disk full\n",
        "WARN  low memory\n",
    ]

    def test_counts_by_first_field(self):
        result = aggregate_by_field(self.LINES, separator=" ", field_index=0)
        assert result["ERROR"] == 2
        assert result["INFO"] == 1

    def test_field_index_out_of_range_skipped(self):
        result = aggregate_by_field(["only_one_field\n"], separator=" ", field_index=5)
        assert result == {}

    def test_empty_input(self):
        assert aggregate_by_field([], field_index=0) == {}


# ---------------------------------------------------------------------------
# top_n
# ---------------------------------------------------------------------------

class TestTopN:
    DATA = {"ERROR": 10, "WARN": 3, "INFO": 7, "DEBUG": 1}

    def test_returns_top_entries(self):
        result = top_n(self.DATA, n=2)
        assert result[0] == ("ERROR", 10)
        assert result[1] == ("INFO", 7)

    def test_ascending_order(self):
        result = top_n(self.DATA, n=2, ascending=True)
        assert result[0] == ("DEBUG", 1)

    def test_n_larger_than_data(self):
        assert len(top_n(self.DATA, n=100)) == len(self.DATA)


# ---------------------------------------------------------------------------
# AggregatorConfig / validate / from_dict
# ---------------------------------------------------------------------------

class TestAggregatorConfig:
    def test_defaults(self):
        cfg = AggregatorConfig()
        assert cfg.enabled is False
        assert cfg.mode == "pattern"
        assert cfg.top_n == 10

    def test_validate_invalid_mode(self):
        cfg = AggregatorConfig(mode="unknown", pattern="x")
        with pytest.raises(ValueError, match="mode"):
            validate(cfg)

    def test_validate_pattern_required_in_pattern_mode(self):
        cfg = AggregatorConfig(mode="pattern", pattern=None)
        with pytest.raises(ValueError, match="pattern"):
            validate(cfg)

    def test_validate_negative_top_n(self):
        cfg = AggregatorConfig(mode="field", top_n=0)
        with pytest.raises(ValueError, match="top_n"):
            validate(cfg)

    def test_from_dict(self):
        cfg = from_dict({"enabled": True, "mode": "field", "field_index": 2, "top_n": 5})
        assert cfg.enabled is True
        assert cfg.mode == "field"
        assert cfg.field_index == 2
        assert cfg.top_n == 5
