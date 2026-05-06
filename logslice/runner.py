"""High-level runner that ties together config, parsing, formatting, and highlighting."""

from typing import Optional, TextIO
import sys

from logslice.config import LogSliceConfig
from logslice.parser import parse_file, filter_lines
from logslice.formatter import format_lines
from logslice.highlighter import highlight_lines


def run_with_config(config: LogSliceConfig, output: Optional[TextIO] = None) -> int:
    """Execute logslice with the given config.

    Returns an exit code: 0 on success, 1 on validation/IO error.
    Writes results to *output* (defaults to sys.stdout).
    """
    if output is None:
        output = sys.stdout

    errors = config.validate()
    if errors:
        for err in errors:
            print(f"logslice: error: {err}", file=sys.stderr)
        return 1

    try:
        raw_lines = parse_file(
            config.file,
            encoding=config.encoding,
        )
    except (OSError, IOError) as exc:
        print(f"logslice: error: {exc}", file=sys.stderr)
        return 1

    filtered = filter_lines(
        raw_lines,
        pattern=config.pattern,
        start_time=config.start_time,
        end_time=config.end_time,
        time_format=config.time_format,
        invert=config.invert_match,
    )

    if config.max_lines is not None:
        filtered = filtered[: config.max_lines]

    if config.highlight and config.pattern:
        filtered = highlight_lines(
            filtered,
            pattern=config.pattern,
            color=config.highlight_color,
            enabled=True,
        )

    formatted = format_lines(
        filtered,
        fmt=config.output_format,
        show_line_numbers=config.show_line_numbers,
    )

    for line in formatted:
        print(line, file=output)

    return 0
