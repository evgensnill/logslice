"""Line sorting support for logslice."""

from typing import Iterable, Iterator, Optional
import re


DEFAULT_TIMESTAMP_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})"
)


def _sort_key_text(line: str) -> str:
    """Return the line itself as a sort key (lexicographic)."""
    return line.rstrip("\n")


def _sort_key_timestamp(line: str, pattern: re.Pattern) -> str:
    """Extract a timestamp string from a line for use as a sort key.

    Falls back to the full line when no timestamp is found so that
    lines without timestamps sort consistently rather than raising.
    """
    match = pattern.search(line)
    if match:
        return match.group(1)
    return line.rstrip("\n")


def sort_lines(
    lines: Iterable[str],
    *,
    key: str = "text",
    reverse: bool = False,
    timestamp_pattern: Optional[re.Pattern] = None,
) -> Iterator[str]:
    """Sort *lines* and yield them in order.

    Parameters
    ----------
    lines:
        Iterable of raw log lines (may include trailing newlines).
    key:
        Sorting strategy.  ``"text"`` sorts lexicographically;
        ``"timestamp"`` extracts a timestamp prefix for comparison.
    reverse:
        When *True* yield lines in descending order.
    timestamp_pattern:
        Compiled regex used when ``key="timestamp"``.  Must expose a
        capturing group at index 1.  Defaults to
        ``DEFAULT_TIMESTAMP_RE`` when *None*.
    """
    if key not in ("text", "timestamp"):
        raise ValueError(f"Unknown sort key {key!r}. Choose 'text' or 'timestamp'.")

    collected = list(lines)

    if key == "timestamp":
        pattern = timestamp_pattern or DEFAULT_TIMESTAMP_RE
        collected.sort(
            key=lambda ln: _sort_key_timestamp(ln, pattern),
            reverse=reverse,
        )
    else:
        collected.sort(key=_sort_key_text, reverse=reverse)

    yield from collected
