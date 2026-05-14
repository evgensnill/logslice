"""Configuration dataclass for the log splitter."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SplitterConfig:
    enabled: bool = False
    chunk_size: Optional[int] = None  # number of lines per chunk
    max_bytes: Optional[int] = None   # max bytes per chunk


def validate(config: SplitterConfig) -> None:
    """Raise ValueError if the config is invalid."""
    if not config.enabled:
        return
    if config.chunk_size is not None and config.max_bytes is not None:
        raise ValueError("SplitterConfig: set chunk_size or max_bytes, not both.")
    if config.chunk_size is None and config.max_bytes is None:
        raise ValueError(
            "SplitterConfig: one of chunk_size or max_bytes must be set when enabled."
        )
    if config.chunk_size is not None and config.chunk_size <= 0:
        raise ValueError("SplitterConfig: chunk_size must be a positive integer.")
    if config.max_bytes is not None and config.max_bytes <= 0:
        raise ValueError("SplitterConfig: max_bytes must be a positive integer.")


def from_dict(data: dict) -> SplitterConfig:
    """Build a SplitterConfig from a plain dictionary."""
    cfg = SplitterConfig(
        enabled=bool(data.get("enabled", False)),
        chunk_size=data.get("chunk_size"),
        max_bytes=data.get("max_bytes"),
    )
    validate(cfg)
    return cfg
