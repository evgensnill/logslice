"""Configuration dataclass for the log-line aggregator."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AggregatorConfig:
    """Settings that control how lines are aggregated."""

    enabled: bool = False
    mode: str = "pattern"          # 'pattern' | 'field'
    pattern: Optional[str] = None  # regex used in 'pattern' mode
    group: int = 0                 # capture group for pattern mode
    separator: str = " "           # delimiter for 'field' mode
    field_index: int = 0           # field position for 'field' mode
    top_n: int = 10                # how many top results to surface
    ascending: bool = False        # sort order for top_n


def validate(cfg: AggregatorConfig) -> None:
    """Raise ValueError if the config is inconsistent."""
    if cfg.mode not in ("pattern", "field"):
        raise ValueError(f"AggregatorConfig.mode must be 'pattern' or 'field', got {cfg.mode!r}")
    if cfg.mode == "pattern" and not cfg.pattern:
        raise ValueError("AggregatorConfig.pattern must be set when mode is 'pattern'")
    if cfg.group < 0:
        raise ValueError("AggregatorConfig.group must be >= 0")
    if cfg.field_index < 0:
        raise ValueError("AggregatorConfig.field_index must be >= 0")
    if cfg.top_n < 1:
        raise ValueError("AggregatorConfig.top_n must be >= 1")


def from_dict(data: dict) -> AggregatorConfig:
    """Build an AggregatorConfig from a plain dictionary (e.g. parsed TOML/JSON)."""
    cfg = AggregatorConfig(
        enabled=bool(data.get("enabled", False)),
        mode=str(data.get("mode", "pattern")),
        pattern=data.get("pattern") or None,
        group=int(data.get("group", 0)),
        separator=str(data.get("separator", " ")),
        field_index=int(data.get("field_index", 0)),
        top_n=int(data.get("top_n", 10)),
        ascending=bool(data.get("ascending", False)),
    )
    return cfg
