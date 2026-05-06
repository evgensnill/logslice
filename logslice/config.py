"""Configuration dataclass for logslice."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class LogSliceConfig:
    """Top-level runtime configuration for logslice."""

    # I/O
    encoding: str = "utf-8"
    output_format: str = "plain"  # plain | json | csv

    # Filtering
    pattern: str = ""
    extra_patterns: List[str] = field(default_factory=list)
    start_time: str = ""
    end_time: str = ""
    time_format: str = "%Y-%m-%d %H:%M:%S"

    # Display
    highlight: bool = False
    highlight_color: str = "yellow"
    show_line_numbers: bool = False

    # Deduplication
    deduplicate: bool = False
    dedup_skip_fields: int = 0  # 0 means compare the full line
    dedup_max_seen: int = 100_000


def validate(config: LogSliceConfig) -> List[str]:
    """Return a list of validation error messages (empty list means valid)."""
    errors: List[str] = []

    if config.output_format not in ("plain", "json", "csv"):
        errors.append(
            f"Invalid output_format '{config.output_format}'; "
            "must be one of: plain, json, csv"
        )

    if config.dedup_skip_fields < 0:
        errors.append("dedup_skip_fields must be >= 0")

    if config.dedup_max_seen < 1:
        errors.append("dedup_max_seen must be >= 1")

    return errors
