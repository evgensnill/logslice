"""Line sampling utilities for logslice."""

import hashlib
from typing import Iterable, Iterator, Optional


def _line_hash_fraction(line: str) -> float:
    """Return a stable float in [0, 1) derived from the line content."""
    digest = hashlib.md5(line.encode("utf-8", errors="replace")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def sample_lines(
    lines: Iterable[str],
    rate: float,
    *,
    every_nth: Optional[int] = None,
    deterministic: bool = False,
) -> Iterator[str]:
    """Yield a subset of *lines* according to the sampling strategy.

    Args:
        lines: Source iterable of log lines.
        rate: Fraction of lines to keep in the range (0.0, 1.0].
              Ignored when *every_nth* is set.
        every_nth: If given, keep every N-th line (1-based index).
        deterministic: When True and *every_nth* is None, use a content-hash
                       so the same line is always included or excluded.
                       When False, use a simple counter-based approach.

    Raises:
        ValueError: If *rate* is outside (0, 1] or *every_nth* < 1.
    """
    if every_nth is not None:
        if every_nth < 1:
            raise ValueError("every_nth must be >= 1")
        for index, line in enumerate(lines, start=1):
            if index % every_nth == 0:
                yield line
        return

    if not (0.0 < rate <= 1.0):
        raise ValueError("rate must be in the range (0.0, 1.0]")

    if deterministic:
        for line in lines:
            if _line_hash_fraction(line) < rate:
                yield line
    else:
        step = max(1, round(1.0 / rate))
        for index, line in enumerate(lines, start=1):
            if index % step == 0:
                yield line
