"""Cache-aware wrapper around run_with_config."""

from typing import Any, Dict, List, Optional

from logslice import cache
from logslice.cache_config import CacheConfig
from logslice.config import LogSliceConfig
from logslice.runner import run_with_config


def _build_cache_params(config: LogSliceConfig) -> Dict[str, Any]:
    """Extract cache-key-relevant fields from LogSliceConfig."""
    return {
        "pattern": config.pattern,
        "start_time": str(config.start_time) if config.start_time else None,
        "end_time": str(config.end_time) if config.end_time else None,
        "output_format": config.output_format,
        "extra_patterns": sorted(config.extra_patterns),
    }


def run_with_cache(
    config: LogSliceConfig,
    cache_cfg: Optional[CacheConfig] = None,
) -> List[str]:
    """Run log parsing, returning cached results when available.

    If cache_cfg is None or cache is disabled, delegates directly to
    run_with_config without any caching overhead.
    """
    if cache_cfg is None or not cache_cfg.enabled:
        return run_with_config(config)

    params = _build_cache_params(config)
    cached = cache.get(
        config.filepath,
        params,
        cache_dir=cache_cfg.cache_dir,
        ttl=cache_cfg.ttl,
    )
    if cached is not None:
        return cached

    result = run_with_config(config)

    cache.put(
        config.filepath,
        params,
        result,
        cache_dir=cache_cfg.cache_dir,
    )
    return result
