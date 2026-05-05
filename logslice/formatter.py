"""Output formatting utilities for logslice."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


SUPPORTED_FORMATS = ("plain", "json", "csv")


def format_line_plain(line: str, line_number: Optional[int] = None) -> str:
    """Return a plain text formatted line, optionally prefixed with line number."""
    if line_number is not None:
        return f"{line_number}: {line.rstrip()}"
    return line.rstrip()


def format_line_json(
    line: str,
    line_number: Optional[int] = None,
    timestamp: Optional[datetime] = None,
) -> str:
    """Return a JSON-encoded representation of a log line."""
    record: Dict[str, Any] = {"message": line.rstrip()}
    if line_number is not None:
        record["line_number"] = line_number
    if timestamp is not None:
        record["timestamp"] = timestamp.isoformat()
    return json.dumps(record)


def format_line_csv(
    line: str,
    line_number: Optional[int] = None,
    timestamp: Optional[datetime] = None,
) -> str:
    """Return a CSV-encoded representation of a log line."""
    import csv
    import io

    buf = io.StringIO()
    writer = csv.writer(buf)
    row: List[Any] = []
    if line_number is not None:
        row.append(line_number)
    if timestamp is not None:
        row.append(timestamp.isoformat())
    row.append(line.rstrip())
    writer.writerow(row)
    return buf.getvalue().rstrip()


def format_lines(
    lines: List[str],
    fmt: str = "plain",
    start_number: int = 1,
    include_line_numbers: bool = False,
    timestamps: Optional[List[Optional[datetime]]] = None,
) -> List[str]:
    """Format a list of log lines according to the specified format.

    Args:
        lines: Raw log lines to format.
        fmt: One of 'plain', 'json', or 'csv'.
        start_number: Starting line number (used when include_line_numbers=True).
        include_line_numbers: Whether to include line numbers in output.
        timestamps: Optional list of parsed timestamps aligned with lines.

    Returns:
        List of formatted strings.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")

    result = []
    for i, line in enumerate(lines):
        line_no = (start_number + i) if include_line_numbers else None
        ts = timestamps[i] if timestamps else None

        if fmt == "plain":
            result.append(format_line_plain(line, line_no))
        elif fmt == "json":
            result.append(format_line_json(line, line_no, ts))
        elif fmt == "csv":
            result.append(format_line_csv(line, line_no, ts))

    return result
