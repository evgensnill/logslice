"""Line aggregation: group and count log lines by pattern or field."""

import re
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional, Tuple


def aggregate_by_pattern(
    lines: Iterable[str],
    pattern: str,
    group: int = 0,
) -> Dict[str, int]:
    """Count occurrences of lines matching a regex pattern.

    Args:
        lines: Iterable of log lines.
        pattern: Regular expression to match against each line.
        group: Capture group index to use as the aggregation key.
                0 means use the entire match.

    Returns:
        A dict mapping matched text (or group) to occurrence count.
    """
    compiled = re.compile(pattern)
    counts: Counter = Counter()
    for line in lines:
        m = compiled.search(line)
        if m:
            key = m.group(group)
            counts[key] += 1
    return dict(counts)


def aggregate_by_field(
    lines: Iterable[str],
    separator: str = " ",
    field_index: int = 0,
) -> Dict[str, int]:
    """Count occurrences grouped by a whitespace/separator-delimited field.

    Args:
        lines: Iterable of log lines.
        separator: Field delimiter (default: single space).
        field_index: Zero-based index of the field to group by.

    Returns:
        A dict mapping field value to occurrence count.
    """
    counts: Counter = Counter()
    for line in lines:
        stripped = line.rstrip("\n")
        parts = stripped.split(separator)
        if field_index < len(parts):
            counts[parts[field_index]] += 1
    return dict(counts)


def top_n(
    aggregated: Dict[str, int],
    n: int = 10,
    ascending: bool = False,
) -> List[Tuple[str, int]]:
    """Return the top-N entries from an aggregated dict.

    Args:
        aggregated: Dict of key -> count as returned by aggregate_* functions.
        n: Maximum number of entries to return.
        ascending: If True, return least-frequent entries first.

    Returns:
        List of (key, count) tuples sorted by count.
    """
    sorted_items = sorted(aggregated.items(), key=lambda kv: kv[1], reverse=not ascending)
    return sorted_items[:n]
