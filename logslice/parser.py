"""Core log file parser with regex and time-range filtering support."""

import re
from datetime import datetime
from typing import Iterator, Optional, Pattern


DEFAULT_TIMESTAMP_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d/%b/%Y:%H:%M:%S",
    "%b %d %H:%M:%S",
]


def parse_timestamp(line: str, formats: list[str] = DEFAULT_TIMESTAMP_FORMATS) -> Optional[datetime]:
    """Attempt to extract a timestamp from the beginning of a log line."""
    for fmt in formats:
        # Try to match a timestamp-like prefix
        try:
            # Extract a reasonable prefix length to attempt parsing
            prefix_len = len(datetime.now().strftime(fmt)) + 5
            candidate = line[:prefix_len].strip()
            return datetime.strptime(candidate[:len(datetime.now().strftime(fmt))], fmt)
        except (ValueError, IndexError):
            continue
    return None


def filter_lines(
    lines: Iterator[str],
    pattern: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    timestamp_formats: list[str] = DEFAULT_TIMESTAMP_FORMATS,
    invert: bool = False,
) -> Iterator[str]:
    """Filter log lines by regex pattern and/or time range.

    Args:
        lines: Iterable of raw log lines.
        pattern: Optional regex pattern to match against each line.
        start_time: Optional start of the time range (inclusive).
        end_time: Optional end of the time range (inclusive).
        timestamp_formats: List of strptime format strings to try.
        invert: If True, return lines that do NOT match the pattern.

    Yields:
        Lines that satisfy all active filters.
    """
    compiled: Optional[Pattern] = re.compile(pattern) if pattern else None

    for line in lines:
        stripped = line.rstrip("\n")

        # Time-range filter
        if start_time or end_time:
            ts = parse_timestamp(stripped, timestamp_formats)
            if ts is not None:
                if start_time and ts < start_time:
                    continue
                if end_time and ts > end_time:
                    continue

        # Regex filter
        if compiled is not None:
            matched = compiled.search(stripped) is not None
            if invert and matched:
                continue
            if not invert and not matched:
                continue

        yield stripped


def parse_file(
    filepath: str,
    pattern: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    timestamp_formats: list[str] = DEFAULT_TIMESTAMP_FORMATS,
    invert: bool = False,
    encoding: str = "utf-8",
) -> Iterator[str]:
    """Open a log file and yield filtered lines."""
    with open(filepath, "r", encoding=encoding, errors="replace") as fh:
        yield from filter_lines(
            fh,
            pattern=pattern,
            start_time=start_time,
            end_time=end_time,
            timestamp_formats=timestamp_formats,
            invert=invert,
        )
