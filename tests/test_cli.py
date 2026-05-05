"""Tests for the logslice CLI module."""

import argparse
import io
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from logslice.cli import build_parser, run, main


SAMPLE_LOG = """2024-01-15 08:00:01 INFO  Server started
2024-01-15 08:01:22 DEBUG Loaded config from /etc/app/config.yaml
2024-01-15 08:05:45 INFO  Listening on port 8080
2024-01-15 09:12:33 WARN  High memory usage detected
2024-01-15 10:30:00 ERROR Failed to connect to database
2024-01-15 10:30:05 INFO  Retrying database connection
2024-01-15 11:00:00 INFO  Database connection restored
"""


class TestBuildParser(unittest.TestCase):
    """Tests for the argument parser builder."""

    def setUp(self):
        self.parser = build_parser()

    def test_returns_argument_parser(self):
        self.assertIsInstance(self.parser, argparse.ArgumentParser)

    def test_requires_file_argument(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])

    def test_parses_file_argument(self):
        args = self.parser.parse_args(["app.log"])
        self.assertEqual(args.file, "app.log")

    def test_default_format_is_plain(self):
        args = self.parser.parse_args(["app.log"])
        self.assertEqual(args.format, "plain")

    def test_format_option_json(self):
        args = self.parser.parse_args(["app.log", "--format", "json"])
        self.assertEqual(args.format, "json")

    def test_format_option_csv(self):
        args = self.parser.parse_args(["app.log", "--format", "csv"])
        self.assertEqual(args.format, "csv")

    def test_pattern_option(self):
        args = self.parser.parse_args(["app.log", "--pattern", "ERROR"])
        self.assertEqual(args.pattern, "ERROR")

    def test_pattern_defaults_to_none(self):
        args = self.parser.parse_args(["app.log"])
        self.assertIsNone(args.pattern)

    def test_start_time_option(self):
        args = self.parser.parse_args(["app.log", "--start", "2024-01-15 09:00:00"])
        self.assertEqual(args.start, "2024-01-15 09:00:00")

    def test_end_time_option(self):
        args = self.parser.parse_args(["app.log", "--end", "2024-01-15 11:00:00"])
        self.assertEqual(args.end, "2024-01-15 11:00:00")

    def test_line_numbers_flag(self):
        args = self.parser.parse_args(["app.log", "--line-numbers"])
        self.assertTrue(args.line_numbers)

    def test_line_numbers_off_by_default(self):
        args = self.parser.parse_args(["app.log"])
        self.assertFalse(args.line_numbers)


class TestRun(unittest.TestCase):
    """Integration tests for the run() function."""

    def _make_temp_log(self, content=SAMPLE_LOG):
        """Create a temporary log file and return its path."""
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False)
        tmp.write(content)
        tmp.close()
        return tmp.name

    def tearDown(self):
        # Clean up any temp files created during tests
        pass

    def test_run_plain_output(self):
        path = self._make_temp_log()
        try:
            args = argparse.Namespace(
                file=path,
                pattern=None,
                start=None,
                end=None,
                format="plain",
                line_numbers=False,
            )
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                run(args)
                output = mock_stdout.getvalue()
            self.assertIn("Server started", output)
            self.assertIn("ERROR", output)
        finally:
            os.unlink(path)

    def test_run_with_pattern_filter(self):
        path = self._make_temp_log()
        try:
            args = argparse.Namespace(
                file=path,
                pattern="ERROR",
                start=None,
                end=None,
                format="plain",
                line_numbers=False,
            )
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                run(args)
                output = mock_stdout.getvalue()
            self.assertIn("ERROR", output)
            self.assertNotIn("Server started", output)
        finally:
            os.unlink(path)

    def test_run_with_time_range(self):
        path = self._make_temp_log()
        try:
            args = argparse.Namespace(
                file=path,
                pattern=None,
                start="2024-01-15 10:00:00",
                end="2024-01-15 10:59:59",
                format="plain",
                line_numbers=False,
            )
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                run(args)
                output = mock_stdout.getvalue()
            self.assertIn("ERROR", output)
            self.assertNotIn("Server started", output)
        finally:
            os.unlink(path)

    def test_run_json_format(self):
        path = self._make_temp_log()
        try:
            args = argparse.Namespace(
                file=path,
                pattern="ERROR",
                start=None,
                end=None,
                format="json",
                line_numbers=False,
            )
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                run(args)
                output = mock_stdout.getvalue()
            self.assertIn('"text"', output)
        finally:
            os.unlink(path)

    def test_run_missing_file_exits(self):
        args = argparse.Namespace(
            file="/nonexistent/path/to/file.log",
            pattern=None,
            start=None,
            end=None,
            format="plain",
            line_numbers=False,
        )
        with self.assertRaises(SystemExit):
            run(args)


class TestMain(unittest.TestCase):
    """Tests for the main() entry point."""

    def test_main_calls_run(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write(SAMPLE_LOG)
            path = f.name
        try:
            with patch("sys.argv", ["logslice", path]):
                with patch("logslice.cli.run") as mock_run:
                    main()
                    mock_run.assert_called_once()
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
