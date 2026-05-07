"""Line truncation utilities for logslice."""

from typing import List, Optional

DEFAULT_MAX_LENGTH = 512
DEFAULT_ELLIPSIS = "..."


def truncate_line(line: str, max_length: int = DEFAULT_MAX_LENGTH, ellipsis: str = DEFAULT_ELLIPSIS) -> str:
    """Truncate a single line to max_length characters.

    If the line (stripped of trailing newline) exceeds max_length,
    it is cut and the ellipsis is appended.  The trailing newline,
    if present, is preserved after truncation.
    """
    if max_length <= 0:
        raise ValueError("max_length must be a positive integer")

    trailing_newline = line.endswith("\n")
    content = line.rstrip("\n")

    if len(content) <= max_length:
        return line

    cut = max_length - len(ellipsis)
    if cut < 0:
        cut = 0
    truncated = content[:cut] + ellipsis

    return truncated + ("\n" if trailing_newline else "")


def truncate_lines(
    lines: List[str],
    max_length: int = DEFAULT_MAX_LENGTH,
    ellipsis: str = DEFAULT_ELLIPSIS,
) -> List[str]:
    """Apply truncate_line to every line in *lines* and return a new list."""
    return [truncate_line(line, max_length=max_length, ellipsis=ellipsis) for line in lines]
