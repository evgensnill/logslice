"""Tests for logslice.transformer and logslice.transformer_config."""

import pytest

from logslice.transformer import (
    apply_transformers,
    make_prefix_transformer,
    make_replace_transformer,
    make_strip_transformer,
    make_uppercase_transformer,
    transform_lines,
)
from logslice.transformer_config import TransformerConfig


class TestMakeStripTransformer:
    def test_strips_leading_trailing_whitespace(self):
        fn = make_strip_transformer()
        assert fn("  hello  \n") == "hello\n"

    def test_plain_line_unchanged(self):
        fn = make_strip_transformer()
        assert fn("hello\n") == "hello\n"

    def test_empty_line(self):
        fn = make_strip_transformer()
        assert fn("   \n") == "\n"


class TestMakeReplaceTransformer:
    def test_replaces_match(self):
        fn = make_replace_transformer(r"\d+", "NUM")
        assert fn("error 404 occurred\n") == "error NUM occurred\n"

    def test_no_match_unchanged(self):
        fn = make_replace_transformer(r"\d+", "NUM")
        assert fn("no digits here\n") == "no digits here\n"

    def test_replaces_all_occurrences(self):
        fn = make_replace_transformer(r"x", "y")
        assert fn("x and x\n") == "y and y\n"


class TestMakePrefixTransformer:
    def test_prepends_prefix(self):
        fn = make_prefix_transformer("[INFO] ")
        assert fn("hello\n") == "[INFO] hello\n"

    def test_empty_prefix(self):
        fn = make_prefix_transformer("")
        assert fn("hello\n") == "hello\n"


class TestMakeUppercaseTransformer:
    def test_uppercases_line(self):
        fn = make_uppercase_transformer()
        assert fn("hello world\n") == "HELLO WORLD\n"

    def test_already_uppercase_unchanged(self):
        fn = make_uppercase_transformer()
        assert fn("HELLO\n") == "HELLO\n"


class TestApplyTransformers:
    def test_applies_in_order(self):
        fns = [make_strip_transformer(), make_uppercase_transformer()]
        assert apply_transformers("  hello  \n", fns) == "HELLO\n"

    def test_empty_pipeline_returns_line(self):
        assert apply_transformers("hello\n", []) == "hello\n"

    def test_none_result_short_circuits(self):
        def drop(_line):
            return None
        called = []
        def track(line):
            called.append(line)
            return line
        apply_transformers("hello\n", [drop, track])
        assert called == []


class TestTransformLines:
    def test_transforms_all_lines(self):
        lines = ["hello\n", "world\n"]
        result = list(transform_lines(lines, [make_uppercase_transformer()]))
        assert result == ["HELLO\n", "WORLD\n"]

    def test_empty_input(self):
        assert list(transform_lines([], [make_uppercase_transformer()])) == []

    def test_no_transformers(self):
        lines = ["a\n", "b\n"]
        assert list(transform_lines(lines, [])) == lines


class TestTransformerConfig:
    def setup_method(self):
        self.cfg = TransformerConfig()

    def test_default_enabled_is_false(self):
        assert self.cfg.enabled is False

    def test_default_strip_whitespace_false(self):
        assert self.cfg.strip_whitespace is False

    def test_default_uppercase_false(self):
        assert self.cfg.uppercase is False

    def test_default_prefix_none(self):
        assert self.cfg.prefix is None

    def test_default_replacements_empty(self):
        assert self.cfg.replacements == []

    def test_validate_passes_on_defaults(self):
        self.cfg.validate()

    def test_validate_raises_on_bad_replacement(self):
        self.cfg.replacements = [{"pattern": "x"}]
        with pytest.raises(ValueError):
            self.cfg.validate()

    def test_from_dict_roundtrip(self):
        data = {
            "enabled": True,
            "strip_whitespace": True,
            "prefix": ">> ",
            "replacements": [{"pattern": r"\d+", "replacement": "NUM"}],
        }
        cfg = TransformerConfig.from_dict(data)
        assert cfg.enabled is True
        assert cfg.strip_whitespace is True
        assert cfg.prefix == ">> "
        assert len(cfg.replacements) == 1
