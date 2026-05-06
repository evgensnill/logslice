"""Redactor module: mask sensitive patterns in log lines."""

import re
from typing import Iterable, Iterator, List, Optional


DEFAULT_MASK = "***REDACTED***"

# Built-in named patterns for common sensitive data
BUILTIN_PATTERNS = {
    "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "email": r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "credit_card": r"\b(?:\d[ \-]?){13,16}\b",
    "auth_token": r"(?i)(?:token|bearer|api[_-]?key)[=:\s]+[\w\-\.]+",
}


def compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    """Compile a list of regex pattern strings into Pattern objects."""
    compiled = []
    for p in patterns:
        compiled.append(re.compile(p))
    return compiled


def redact_line(line: str, patterns: List[re.Pattern], mask: str = DEFAULT_MASK) -> str:
    """Replace all matches of each pattern in line with the mask string."""
    for pattern in patterns:
        line = pattern.sub(mask, line)
    return line


def redact_lines(
    lines: Iterable[str],
    patterns: List[re.Pattern],
    mask: str = DEFAULT_MASK,
) -> Iterator[str]:
    """Yield each line with sensitive patterns replaced by the mask."""
    for line in lines:
        yield redact_line(line, patterns, mask)


def resolve_patterns(
    pattern_strings: Optional[List[str]] = None,
    builtin_names: Optional[List[str]] = None,
) -> List[re.Pattern]:
    """Combine custom pattern strings with named built-in patterns."""
    raw: List[str] = []
    for name in (builtin_names or []):
        if name not in BUILTIN_PATTERNS:
            raise ValueError(f"Unknown built-in redaction pattern: {name!r}")
        raw.append(BUILTIN_PATTERNS[name])
    raw.extend(pattern_strings or [])
    return compile_patterns(raw)
