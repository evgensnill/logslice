"""Tests for logslice.redactor."""

import re
import pytest

from logslice.redactor import (
    DEFAULT_MASK,
    BUILTIN_PATTERNS,
    compile_patterns,
    redact_line,
    redact_lines,
    resolve_patterns,
)


class TestCompilePatterns:
    def test_returns_list_of_patterns(self):
        result = compile_patterns([r"\d+", r"[a-z]+"])
        assert all(isinstance(p, re.Pattern) for p in result)

    def test_empty_list_returns_empty(self):
        assert compile_patterns([]) == []

    def test_invalid_regex_raises(self):
        with pytest.raises(re.error):
            compile_patterns([r"[invalid"])


class TestRedactLine:
    def test_replaces_single_match(self):
        pattern = re.compile(r"\d+")
        result = redact_line("error on line 42", [pattern])
        assert "42" not in result
        assert DEFAULT_MASK in result

    def test_replaces_multiple_patterns(self):
        p1 = re.compile(r"\d+")
        p2 = re.compile(r"error")
        result = redact_line("error on line 42", [p1, p2])
        assert "42" not in result
        assert "error" not in result

    def test_custom_mask(self):
        pattern = re.compile(r"secret")
        result = redact_line("my secret value", [pattern], mask="[HIDDEN]")
        assert result == "my [HIDDEN] value"

    def test_no_match_returns_original(self):
        pattern = re.compile(r"xyz")
        original = "nothing to redact"
        assert redact_line(original, [pattern]) == original


class TestRedactLines:
    def test_yields_redacted_lines(self):
        patterns = compile_patterns([r"\d+"])
        lines = ["line 1", "line 2", "no digits here"]
        result = list(redact_lines(lines, patterns))
        assert DEFAULT_MASK in result[0]
        assert DEFAULT_MASK in result[1]
        assert result[2] == "no digits here"

    def test_empty_input_yields_nothing(self):
        patterns = compile_patterns([r"\d+"])
        assert list(redact_lines([], patterns)) == []


class TestResolvePatterns:
    def test_builtin_ipv4(self):
        patterns = resolve_patterns(builtin_names=["ipv4"])
        result = redact_line("connect from 192.168.1.1", patterns)
        assert "192.168.1.1" not in result

    def test_builtin_email(self):
        patterns = resolve_patterns(builtin_names=["email"])
        result = redact_line("user: foo@example.com logged in", patterns)
        assert "foo@example.com" not in result

    def test_custom_pattern(self):
        patterns = resolve_patterns(pattern_strings=[r"password=\S+"])
        result = redact_line("password=hunter2 ok", patterns)
        assert "hunter2" not in result

    def test_unknown_builtin_raises(self):
        with pytest.raises(ValueError, match="Unknown built-in"):
            resolve_patterns(builtin_names=["nonexistent"])

    def test_combines_builtin_and_custom(self):
        patterns = resolve_patterns(
            builtin_names=["ipv4"], pattern_strings=[r"token=\S+"]
        )
        line = "ip=10.0.0.1 token=abc123"
        result = redact_line(line, patterns)
        assert "10.0.0.1" not in result
        assert "abc123" not in result
