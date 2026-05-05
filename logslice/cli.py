"""Command-line interface for logslice."""

import argparse
import sys
from typing import List, Optional

from logslice.formatter import SUPPORTED_FORMATS, format_lines
from logslice.parser import filter_lines, parse_file, parse_timestamp


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Fast log file parser and filter utility with regex and time-range support.",
    )
    p.add_argument("file", nargs="?", default="-", help="Log file path (default: stdin)")
    p.add_argument("-p", "--pattern", help="Regex pattern to filter lines")
    p.add_argument("--since", help="Include lines at or after this timestamp")
    p.add_argument("--until", help="Include lines at or before this timestamp")
    p.add_argument(
        "--ts-format",
        default=None,
        help="strptime format string for parsing timestamps in log lines",
    )
    p.add_argument(
        "-f",
        "--format",
        choices=SUPPORTED_FORMATS,
        default="plain",
        help="Output format (default: plain)",
    )
    p.add_argument(
        "-n",
        "--line-numbers",
        action="store_true",
        help="Prefix output lines with their original line number",
    )
    return p


def run(argv: Optional[List[str]] = None) -> int:
    """Entry point for the CLI. Returns exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    since = parse_timestamp(args.since, fmt=args.ts_format) if args.since else None
    until = parse_timestamp(args.until, fmt=args.ts_format) if args.until else None

    try:
        if args.file == "-":
            raw_lines = sys.stdin.readlines()
        else:
            with open(args.file, "r", encoding="utf-8", errors="replace") as fh:
                raw_lines = fh.readlines()
    except OSError as exc:
        print(f"logslice: error reading file: {exc}", file=sys.stderr)
        return 1

    filtered = filter_lines(
        raw_lines,
        pattern=args.pattern,
        since=since,
        until=until,
        ts_format=args.ts_format,
    )

    formatted = format_lines(
        filtered,
        fmt=args.format,
        include_line_numbers=args.line_numbers,
    )

    for line in formatted:
        print(line)

    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
