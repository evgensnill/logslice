"""Tests for logslice.sampler_config."""

import pytest

from logslice.sampler_config import SamplerConfig, validate, from_dict


class TestSamplerConfigDefaults:
    def setup_method(self):
        self.cfg = SamplerConfig()

    def test_default_enabled_is_false(self):
        assert self.cfg.enabled is False

    def test_default_rate_is_one(self):
        assert self.cfg.rate == 1.0

    def test_default_every_nth_is_none(self):
        assert self.cfg.every_nth is None

    def test_default_deterministic_is_false(self):
        assert self.cfg.deterministic is False


class TestSamplerConfigValidate:
    def test_valid_config_does_not_raise(self):
        validate(SamplerConfig(enabled=True, rate=0.5))

    def test_rate_zero_raises(self):
        with pytest.raises(ValueError, match="rate"):
            validate(SamplerConfig(rate=0.0))

    def test_rate_above_one_raises(self):
        with pytest.raises(ValueError, match="rate"):
            validate(SamplerConfig(rate=1.5))

    def test_every_nth_zero_raises(self):
        with pytest.raises(ValueError, match="every_nth"):
            validate(SamplerConfig(every_nth=0))

    def test_every_nth_negative_raises(self):
        with pytest.raises(ValueError):
            validate(SamplerConfig(every_nth=-1))

    def test_every_nth_one_is_valid(self):
        validate(SamplerConfig(every_nth=1))


class TestSamplerConfigFromDict:
    def test_builds_from_full_dict(self):
        cfg = from_dict({"enabled": True, "rate": 0.25, "every_nth": 4, "deterministic": True})
        assert cfg.enabled is True
        assert cfg.rate == 0.25
        assert cfg.every_nth == 4
        assert cfg.deterministic is True

    def test_builds_from_empty_dict_uses_defaults(self):
        cfg = from_dict({})
        assert cfg.enabled is False
        assert cfg.rate == 1.0
        assert cfg.every_nth is None

    def test_invalid_rate_in_dict_raises(self):
        with pytest.raises(ValueError):
            from_dict({"rate": 0.0})
