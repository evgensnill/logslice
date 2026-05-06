"""Tests for logslice.highlighter module."""

import unittest
from logslice.highlighter import colorize, highlight_pattern, highlight_lines, ANSI_RESET


class TestColorize(unittest.TestCase):
    def test_wraps_text_with_known_color(self):
        result = colorize("hello", "red")
        self.assertIn("hello", result)
        self.assertIn(ANSI_RESET, result)
        self.assertTrue(result.startswith("\033["))

    def test_unknown_color_returns_plain_text(self):
        result = colorize("hello", "ultraviolet")
        self.assertEqual(result, "hello")

    def test_bold_color(self):
        result = colorize("important", "bold")
        self.assertIn("important", result)
        self.assertIn("\033[1m", result)


class TestHighlightPattern(unittest.TestCase):
    def test_highlights_matching_text(self):
        result = highlight_pattern("ERROR: disk full", "ERROR", "red")
        self.assertIn(ANSI_RESET, result)
        self.assertIn("ERROR", result)

    def test_no_match_returns_original(self):
        result = highlight_pattern("INFO: all good", "ERROR", "red")
        self.assertEqual(result, "INFO: all good")

    def test_empty_pattern_returns_original(self):
        result = highlight_pattern("some line", "", "yellow")
        self.assertEqual(result, "some line")

    def test_invalid_regex_returns_original(self):
        result = highlight_pattern("some line", "[invalid", "yellow")
        self.assertEqual(result, "some line")

    def test_multiple_occurrences_all_highlighted(self):
        result = highlight_pattern("foo bar foo", "foo", "cyan")
        self.assertEqual(result.count(ANSI_RESET), 2)

    def test_case_sensitive_by_default(self):
        result = highlight_pattern("error ERROR", "error", "red")
        # Only lowercase 'error' should be highlighted
        self.assertEqual(result.count(ANSI_RESET), 1)


class TestHighlightLines(unittest.TestCase):
    def setUp(self):
        self.lines = [(1, "ERROR found"), (2, "INFO ok"), (3, "ERROR again")]

    def test_highlights_matching_lines(self):
        result = highlight_lines(self.lines, pattern="ERROR", color="red")
        self.assertIn(ANSI_RESET, result[0][1])
        self.assertNotIn(ANSI_RESET, result[1][1])
        self.assertIn(ANSI_RESET, result[2][1])

    def test_disabled_returns_original(self):
        result = highlight_lines(self.lines, pattern="ERROR", enabled=False)
        self.assertEqual(result, self.lines)

    def test_no_pattern_returns_original(self):
        result = highlight_lines(self.lines, pattern=None)
        self.assertEqual(result, self.lines)

    def test_preserves_line_numbers(self):
        result = highlight_lines(self.lines, pattern="ERROR", color="yellow")
        numbers = [num for num, _ in result]
        self.assertEqual(numbers, [1, 2, 3])

    def test_empty_list(self):
        result = highlight_lines([], pattern="ERROR")
        self.assertEqual(result, [])
