"""Cache configuration dataclass for logslice."""

from dataclasses import dataclass, field
from typing import Optional

from logslice.cache import DEFAULT_CACHE_DIR, DEFAULT_TTL


@dataclass
class CacheConfig:
    """Configuration for the result cache."""

    enabled: bool = False
    cache_dir: str = DEFAULT_CACHE_DIR
    ttl: int = DEFAULT_TTL
    max_entries: Optional[int] = None

    def validate(self) -> None:
        """Raise ValueError for invalid configuration."""
        if self.ttl <= 0:
            raise ValueError(f"ttl must be positive, got {self.ttl}")
        if self.max_entries is not None and self.max_entries <= 0:
            raise ValueError(f"max_entries must be positive or None, got {self.max_entries}")
        if not self.cache_dir:
            raise ValueError("cache_dir must not be empty")


def from_dict(data: dict) -> CacheConfig:
    """Build a CacheConfig from a plain dictionary (e.g. loaded from TOML/JSON config)."""
    return CacheConfig(
        enabled=bool(data.get("enabled", False)),
        cache_dir=data.get("cache_dir", DEFAULT_CACHE_DIR),
        ttl=int(data.get("ttl", DEFAULT_TTL)),
        max_entries=data.get("max_entries"),
    )
