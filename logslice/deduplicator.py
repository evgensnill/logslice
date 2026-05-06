"""Deduplication support for log lines."""

import hashlib
from typing import Iterable, Iterator, Optional


def _line_key(line: str, fields: Optional[int] = None) -> str:
    """Compute a deduplication key for a log line.

    If ``fields`` is given, only the first N whitespace-separated tokens
    are used so that timestamps (field 0) can be ignored.
    """
    text = line.rstrip("\n")
    if fields is not None:
        parts = text.split(None, fields)
        # drop the leading *fields* tokens; remainder is the message body
        text = parts[fields] if len(parts) > fields else text
    return hashlib.md5(text.encode("utf-8", errors="replace")).hexdigest()


def deduplicate_lines(
    lines: Iterable[str],
    skip_fields: Optional[int] = None,
    max_seen: int = 100_000,
) -> Iterator[str]:
    """Yield unique log lines, dropping exact duplicates.

    Args:
        lines: Iterable of raw log line strings.
        skip_fields: If set, ignore the first N whitespace-separated fields
            (e.g. skip_fields=2 ignores date + time columns) when comparing.
        max_seen: Maximum number of keys to keep in memory.  When the set
            exceeds this limit it is cleared to avoid unbounded growth.

    Yields:
        Lines that have not been seen before.
    """
    seen: set[str] = set()
    for line in lines:
        key = _line_key(line, fields=skip_fields)
        if key in seen:
            continue
        seen.add(key)
        if len(seen) > max_seen:
            seen.clear()
            seen.add(key)
        yield line
