"""Configuration dataclass for the log-line sampler."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SamplerConfig:
    """Settings that control how lines are sampled before output."""

    enabled: bool = False
    rate: float = 1.0
    every_nth: Optional[int] = None
    deterministic: bool = False


def validate(cfg: SamplerConfig) -> None:
    """Raise *ValueError* if *cfg* contains invalid values."""
    if not isinstance(cfg.enabled, bool):
        raise ValueError("SamplerConfig.enabled must be a bool")
    if not (0.0 < cfg.rate <= 1.0):
        raise ValueError("SamplerConfig.rate must be in the range (0.0, 1.0]")
    if cfg.every_nth is not None and cfg.every_nth < 1:
        raise ValueError("SamplerConfig.every_nth must be >= 1 when set")


def from_dict(data: dict) -> SamplerConfig:
    """Build a :class:`SamplerConfig` from a plain dictionary (e.g. from TOML/JSON)."""
    cfg = SamplerConfig(
        enabled=bool(data.get("enabled", False)),
        rate=float(data.get("rate", 1.0)),
        every_nth=data.get("every_nth"),
        deterministic=bool(data.get("deterministic", False)),
    )
    validate(cfg)
    return cfg
