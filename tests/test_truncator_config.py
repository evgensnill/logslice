"""Tests for logslice.truncator_config."""

import pytest

from logslice.truncator import DEFAULT_ELLIPSIS, DEFAULT_MAX_LENGTH
from logslice.truncator_config import TruncatorConfig


class TestTruncatorConfigDefaults:
    def setup_method(self):
        self.cfg = TruncatorConfig()

    def test_default_enabled_is_false(self):
        assert self.cfg.enabled is False

    def test_default_max_length(self):
        assert self.cfg.max_length == DEFAULT_MAX_LENGTH

    def test_default_ellipsis(self):
        assert self.cfg.ellipsis == DEFAULT_ELLIPSIS


class TestTruncatorConfigValidate:
    def test_valid_config_does_not_raise(self):
        cfg = TruncatorConfig(enabled=True, max_length=256, ellipsis="...")
        cfg.validate()  # should not raise

    def test_invalid_max_length_zero_raises(self):
        cfg = TruncatorConfig(max_length=0)
        with pytest.raises(ValueError, match="max_length"):
            cfg.validate()

    def test_invalid_max_length_negative_raises(self):
        cfg = TruncatorConfig(max_length=-1)
        with pytest.raises(ValueError):
            cfg.validate()

    def test_invalid_enabled_type_raises(self):
        cfg = TruncatorConfig(enabled="yes")  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="enabled"):
            cfg.validate()

    def test_invalid_ellipsis_type_raises(self):
        cfg = TruncatorConfig(ellipsis=123)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="ellipsis"):
            cfg.validate()


class TestTruncatorConfigFromDict:
    def test_from_empty_dict_uses_defaults(self):
        cfg = TruncatorConfig.from_dict({})
        assert cfg.enabled is False
        assert cfg.max_length == DEFAULT_MAX_LENGTH
        assert cfg.ellipsis == DEFAULT_ELLIPSIS

    def test_from_dict_sets_values(self):
        cfg = TruncatorConfig.from_dict({"enabled": True, "max_length": 128, "ellipsis": "~~"})
        assert cfg.enabled is True
        assert cfg.max_length == 128
        assert cfg.ellipsis == "~~"

    def test_from_dict_invalid_max_length_raises(self):
        with pytest.raises(ValueError):
            TruncatorConfig.from_dict({"max_length": -10})
