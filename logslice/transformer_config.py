"""Configuration for the line transformer pipeline."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TransformerConfig:
    enabled: bool = False
    strip_whitespace: bool = False
    uppercase: bool = False
    prefix: Optional[str] = None
    replacements: List[Dict[str, str]] = field(default_factory=list)

    def validate(self) -> None:
        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be a bool")
        if not isinstance(self.strip_whitespace, bool):
            raise TypeError("strip_whitespace must be a bool")
        if not isinstance(self.uppercase, bool):
            raise TypeError("uppercase must be a bool")
        if self.prefix is not None and not isinstance(self.prefix, str):
            raise TypeError("prefix must be a string or None")
        if not isinstance(self.replacements, list):
            raise TypeError("replacements must be a list")
        for item in self.replacements:
            if "pattern" not in item or "replacement" not in item:
                raise ValueError(
                    "each replacement must have 'pattern' and 'replacement' keys"
                )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransformerConfig":
        return cls(
            enabled=data.get("enabled", False),
            strip_whitespace=data.get("strip_whitespace", False),
            uppercase=data.get("uppercase", False),
            prefix=data.get("prefix", None),
            replacements=data.get("replacements", []),
        )
