"""Configuration dataclass for the redactor feature."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from logslice.redactor import DEFAULT_MASK


@dataclass
class RedactorConfig:
    enabled: bool = False
    mask: str = DEFAULT_MASK
    # Names of built-in patterns (e.g. 'ipv4', 'email')
    builtin_patterns: List[str] = field(default_factory=list)
    # Custom regex strings supplied by the user
    custom_patterns: List[str] = field(default_factory=list)


def validate(cfg: RedactorConfig) -> None:
    """Raise ValueError if the config is invalid."""
    if not isinstance(cfg.mask, str) or not cfg.mask:
        raise ValueError("RedactorConfig.mask must be a non-empty string")
    if not isinstance(cfg.builtin_patterns, list):
        raise ValueError("RedactorConfig.builtin_patterns must be a list")
    if not isinstance(cfg.custom_patterns, list):
        raise ValueError("RedactorConfig.custom_patterns must be a list")


def from_dict(data: Dict[str, Any]) -> RedactorConfig:
    """Build a RedactorConfig from a plain dictionary (e.g. parsed TOML/JSON)."""
    return RedactorConfig(
        enabled=bool(data.get("enabled", False)),
        mask=str(data.get("mask", DEFAULT_MASK)),
        builtin_patterns=list(data.get("builtin_patterns", [])),
        custom_patterns=list(data.get("custom_patterns", [])),
    )
