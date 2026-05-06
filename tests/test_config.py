"""Tests for logslice.config module."""

import unittest
from logslice.config import LogSliceConfig


class TestLogSliceConfigDefaults(unittest.TestCase):
    def test_default_encoding(self):
        cfg = LogSliceConfig(file="app.log")
        self.assertEqual(cfg.encoding, "utf-8")

    def test_default_output_format(self):
        cfg = LogSliceConfig(file="app.log")
        self.assertEqual(cfg.output_format, "plain")

    def test_default_highlight_false(self):
        cfg = LogSliceConfig(file="app.log")
        self.assertFalse(cfg.highlight)

    def test_default_extra_patterns_empty_list(self):
        cfg = LogSliceConfig(file="app.log")
        self.assertEqual(cfg.extra_patterns, [])

    def test_extra_patterns_not_shared(self):
        cfg1 = LogSliceConfig(file="a.log")
        cfg2 = LogSliceConfig(file="b.log")
        cfg1.extra_patterns.append("foo")
        self.assertEqual(cfg2.extra_patterns, [])


class TestLogSliceConfigValidation(unittest.TestCase):
    def test_valid_config_no_errors(self):
        cfg = LogSliceConfig(file="app.log")
        self.assertEqual(cfg.validate(), [])

    def test_missing_file_error(self):
        cfg = LogSliceConfig()
        errors = cfg.validate()
        self.assertTrue(any("file" in e for e in errors))

    def test_invalid_output_format_error(self):
        cfg = LogSliceConfig(file="app.log", output_format="xml")
        errors = cfg.validate()
        self.assertTrue(any("output_format" in e for e in errors))

    def test_max_lines_zero_error(self):
        cfg = LogSliceConfig(file="app.log", max_lines=0)
        errors = cfg.validate()
        self.assertTrue(any("max_lines" in e for e in errors))

    def test_max_lines_negative_error(self):
        cfg = LogSliceConfig(file="app.log", max_lines=-5)
        errors = cfg.validate()
        self.assertTrue(any("max_lines" in e for e in errors))

    def test_max_lines_positive_valid(self):
        cfg = LogSliceConfig(file="app.log", max_lines=100)
        self.assertEqual(cfg.validate(), [])

    def test_all_valid_output_formats(self):
        for fmt in ("plain", "json", "csv"):
            cfg = LogSliceConfig(file="app.log", output_format=fmt)
            self.assertEqual(cfg.validate(), [], msg=f"Format {fmt!r} should be valid")
