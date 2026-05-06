"""Simple file-based cache for parsed log results."""

import hashlib
import json
import os
import time
from typing import Any, Optional

DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".logslice", "cache")
DEFAULT_TTL = 3600  # seconds


def _cache_key(filepath: str, params: dict) -> str:
    """Generate a unique cache key from filepath and query params."""
    raw = json.dumps({"file": filepath, "params": params}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def _cache_path(cache_dir: str, key: str) -> str:
    return os.path.join(cache_dir, f"{key}.json")


def get(filepath: str, params: dict, cache_dir: str = DEFAULT_CACHE_DIR, ttl: int = DEFAULT_TTL) -> Optional[Any]:
    """Return cached result if present and not expired, else None."""
    key = _cache_key(filepath, params)
    path = _cache_path(cache_dir, key)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            entry = json.load(f)
        if time.time() - entry["timestamp"] > ttl:
            os.remove(path)
            return None
        return entry["data"]
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def put(filepath: str, params: dict, data: Any, cache_dir: str = DEFAULT_CACHE_DIR) -> None:
    """Store result in cache."""
    os.makedirs(cache_dir, exist_ok=True)
    key = _cache_key(filepath, params)
    path = _cache_path(cache_dir, key)
    entry = {"timestamp": time.time(), "data": data}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entry, f)


def invalidate(filepath: str, params: dict, cache_dir: str = DEFAULT_CACHE_DIR) -> bool:
    """Remove a specific cache entry. Returns True if removed."""
    key = _cache_key(filepath, params)
    path = _cache_path(cache_dir, key)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def clear_all(cache_dir: str = DEFAULT_CACHE_DIR) -> int:
    """Remove all cache entries. Returns count of removed files."""
    if not os.path.exists(cache_dir):
        return 0
    count = 0
    for fname in os.listdir(cache_dir):
        if fname.endswith(".json"):
            os.remove(os.path.join(cache_dir, fname))
            count += 1
    return count
