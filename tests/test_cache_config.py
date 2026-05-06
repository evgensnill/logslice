"""Tests for logslice.cache_config module."""

import unittest

from logslice.cache import DEFAULT_CACHE_DIR, DEFAULT_TTL
from logslice import cache_config
from logslice.cache_config import CacheConfig


class TestCacheConfigDefaults(unittest.TestCase):
    def setUp(self):
        self.cfg = CacheConfig()

    def test_default_enabled_is_false(self):
        self.assertFalse(self.cfg.enabled)

    def test_default_cache_dir(self):
        self.assertEqual(self.cfg.cache_dir, DEFAULT_CACHE_DIR)

    def test_default_ttl(self):
        self.assertEqual(self.cfg.ttl, DEFAULT_TTL)

    def test_default_max_entries_is_none(self):
        self.assertIsNone(self.cfg.max_entries)


class TestCacheConfigValidation(unittest.TestCase):
    def test_valid_config_does_not_raise(self):
        cfg = CacheConfig(enabled=True, ttl=60, max_entries=100)
        cfg.validate()  # should not raise

    def test_zero_ttl_raises(self):
        cfg = CacheConfig(ttl=0)
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_negative_ttl_raises(self):
        cfg = CacheConfig(ttl=-10)
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_zero_max_entries_raises(self):
        cfg = CacheConfig(max_entries=0)
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_none_max_entries_is_valid(self):
        cfg = CacheConfig(max_entries=None)
        cfg.validate()  # should not raise

    def test_empty_cache_dir_raises(self):
        cfg = CacheConfig(cache_dir="")
        with self.assertRaises(ValueError):
            cfg.validate()


class TestCacheConfigFromDict(unittest.TestCase):
    def test_builds_from_full_dict(self):
        data = {"enabled": True, "cache_dir": "/tmp/lsc", "ttl": 120, "max_entries": 50}
        cfg = cache_config.from_dict(data)
        self.assertTrue(cfg.enabled)
        self.assertEqual(cfg.cache_dir, "/tmp/lsc")
        self.assertEqual(cfg.ttl, 120)
        self.assertEqual(cfg.max_entries, 50)

    def test_builds_from_empty_dict_uses_defaults(self):
        cfg = cache_config.from_dict({})
        self.assertFalse(cfg.enabled)
        self.assertEqual(cfg.ttl, DEFAULT_TTL)
        self.assertEqual(cfg.cache_dir, DEFAULT_CACHE_DIR)

    def test_enabled_coerced_to_bool(self):
        cfg = cache_config.from_dict({"enabled": 1})
        self.assertIs(type(cfg.enabled), bool)
        self.assertTrue(cfg.enabled)
