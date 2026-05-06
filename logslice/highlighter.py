"""Terminal color highlighting for matched patterns in log lines."""

import re
from typing import Optional

ANSI_COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bold": "\033[1m",
}
ANSI_RESET = "\033[0m"


def colorize(text: str, color: str) -> str:
    """Wrap text with ANSI color codes."""
    code = ANSI_COLORS.get(color)
    if not code:
        return text
    return f"{code}{text}{ANSI_RESET}"


def highlight_pattern(line: str, pattern: str, color: str = "yellow") -> str:
    """Highlight all occurrences of pattern in line using the given color."""
    if not pattern:
        return line
    try:
        compiled = re.compile(pattern)
    except re.error:
        return line

    def replace_match(m: re.Match) -> str:
        return colorize(m.group(0), color)

    return compiled.sub(replace_match, line)


def highlight_lines(
    lines: list,
    pattern: Optional[str] = None,
    color: str = "yellow",
    enabled: bool = True,
) -> list:
    """Apply pattern highlighting to a list of (line_number, text) tuples."""
    if not enabled or not pattern:
        return lines
    return [(num, highlight_pattern(text, pattern, color)) for num, text in lines]
