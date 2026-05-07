"""Configuration dataclass for the truncator feature."""

from dataclasses import dataclass, field
from typing import Any, Dict

from logslice.truncator import DEFAULT_ELLIPSIS, DEFAULT_MAX_LENGTH


@dataclass
class TruncatorConfig:
    enabled: bool = False
    max_length: int = DEFAULT_MAX_LENGTH
    ellipsis: str = DEFAULT_ELLIPSIS

    def validate(self) -> None:
        """Raise ValueError for invalid configuration values."""
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be a bool")
        if not isinstance(self.max_length, int) or self.max_length <= 0:
            raise ValueError("max_length must be a positive integer")
        if not isinstance(self.ellipsis, str):
            raise ValueError("ellipsis must be a string")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TruncatorConfig":
        """Construct a TruncatorConfig from a plain dictionary."""
        cfg = cls(
            enabled=data.get("enabled", False),
            max_length=data.get("max_length", DEFAULT_MAX_LENGTH),
            ellipsis=data.get("ellipsis", DEFAULT_ELLIPSIS),
        )
        cfg.validate()
        return cfg
