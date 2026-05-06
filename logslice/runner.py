"""High-level runner that wires together parsing, formatting, and stats."""

from typing import Optional

from logslice.config import LogSliceConfig
from logslice.parser import parse_file, filter_lines
from logslice.formatter import format_lines
from logslice.highlighter import highlight_lines
from logslice.stats import ParseStats


def run_with_config(config: LogSliceConfig, output=None) -> ParseStats:
    """Execute a full log-slice run using *config*.

    Reads *config.file*, applies time-range and pattern filters, optionally
    highlights matches, formats each surviving line, writes to *output* (or
    stdout when *output* is None), and returns a populated :class:`ParseStats`.
    """
    import sys

    out = output if output is not None else sys.stdout
    stats = ParseStats()

    lines = parse_file(
        config.file,
        encoding=config.encoding,
    )

    filtered = filter_lines(
        lines,
        patterns=config.extra_patterns,
        start=config.start_time,
        end=config.end_time,
        stats=stats,
    )

    if config.highlight and config.extra_patterns:
        filtered = highlight_lines(filtered, config.extra_patterns)

    formatted = format_lines(
        filtered,
        fmt=config.output_format,
        line_numbers=getattr(config, "line_numbers", False),
    )

    for line in formatted:
        out.write(line + "\n")

    return stats
