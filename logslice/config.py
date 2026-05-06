"""Configuration dataclass for logslice run options."""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class LogSliceConfig:
    """Holds all runtime configuration for a logslice invocation."""

    # Input
    file: str = ""
    encoding: str = "utf-8"

    # Filtering
    pattern: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    time_format: Optional[str] = None
    invert_match: bool = False

    # Output
    output_format: str = "plain"  # plain | json | csv
    show_line_numbers: bool = False
    max_lines: Optional[int] = None

    # Highlighting
    highlight: bool = False
    highlight_color: str = "yellow"

    # Extra
    extra_patterns: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        """Return a list of validation error messages (empty if valid)."""
        errors = []
        if not self.file:
            errors.append("'file' must not be empty.")
        if self.output_format not in ("plain", "json", "csv"):
            errors.append(
                f"Invalid output_format '{self.output_format}'. "
                "Choose from: plain, json, csv."
            )
        if self.max_lines is not None and self.max_lines < 1:
            errors.append("'max_lines' must be a positive integer.")
        return errors
