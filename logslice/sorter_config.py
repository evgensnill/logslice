"""Configuration dataclass for the line sorter."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SorterConfig:
    """Holds options that control how log lines are sorted."""

    enabled: bool = False
    key: str = "text"          # "text" | "timestamp"
    reverse: bool = False
    timestamp_pattern: Optional[str] = None  # raw regex string or None


def validate(cfg: SorterConfig) -> None:
    """Raise *ValueError* if *cfg* contains invalid values."""
    if not isinstance(cfg.enabled, bool):
        raise ValueError("SorterConfig.enabled must be a bool.")
    if cfg.key not in ("text", "timestamp"):
        raise ValueError(
            f"SorterConfig.key must be 'text' or 'timestamp', got {cfg.key!r}."
        )
    if not isinstance(cfg.reverse, bool):
        raise ValueError("SorterConfig.reverse must be a bool.")
    if cfg.timestamp_pattern is not None:
        import re
        try:
            re.compile(cfg.timestamp_pattern)
        except re.error as exc:
            raise ValueError(
                f"SorterConfig.timestamp_pattern is not valid regex: {exc}"
            ) from exc


def from_dict(data: dict) -> SorterConfig:
    """Build a :class:`SorterConfig` from a plain dictionary."""
    cfg = SorterConfig(
        enabled=bool(data.get("enabled", False)),
        key=str(data.get("key", "text")),
        reverse=bool(data.get("reverse", False)),
        timestamp_pattern=data.get("timestamp_pattern"),
    )
    validate(cfg)
    return cfg
