"""Tests for logslice.redactor_config."""

import pytest

from logslice.redactor import DEFAULT_MASK
from logslice.redactor_config import RedactorConfig, validate, from_dict


class TestRedactorConfigDefaults:
    def setup_method(self):
        self.cfg = RedactorConfig()

    def test_default_enabled_is_false(self):
        assert self.cfg.enabled is False

    def test_default_mask(self):
        assert self.cfg.mask == DEFAULT_MASK

    def test_default_builtin_patterns_empty(self):
        assert self.cfg.builtin_patterns == []

    def test_default_custom_patterns_empty(self):
        assert self.cfg.custom_patterns == []


class TestValidate:
    def test_valid_config_passes(self):
        cfg = RedactorConfig(enabled=True, mask="[X]", builtin_patterns=["ipv4"])
        validate(cfg)  # should not raise

    def test_empty_mask_raises(self):
        cfg = RedactorConfig(mask="")
        with pytest.raises(ValueError, match="mask"):
            validate(cfg)

    def test_non_list_builtin_patterns_raises(self):
        cfg = RedactorConfig()
        cfg.builtin_patterns = "ipv4"  # type: ignore
        with pytest.raises(ValueError, match="builtin_patterns"):
            validate(cfg)

    def test_non_list_custom_patterns_raises(self):
        cfg = RedactorConfig()
        cfg.custom_patterns = None  # type: ignore
        with pytest.raises(ValueError, match="custom_patterns"):
            validate(cfg)


class TestFromDict:
    def test_all_fields(self):
        data = {
            "enabled": True,
            "mask": "[MASKED]",
            "builtin_patterns": ["email"],
            "custom_patterns": [r"\d+"],
        }
        cfg = from_dict(data)
        assert cfg.enabled is True
        assert cfg.mask == "[MASKED]"
        assert cfg.builtin_patterns == ["email"]
        assert cfg.custom_patterns == [r"\d+"]

    def test_defaults_on_empty_dict(self):
        cfg = from_dict({})
        assert cfg.enabled is False
        assert cfg.mask == DEFAULT_MASK
        assert cfg.builtin_patterns == []
        assert cfg.custom_patterns == []

    def test_enabled_coerced_to_bool(self):
        cfg = from_dict({"enabled": 1})
        assert cfg.enabled is True
