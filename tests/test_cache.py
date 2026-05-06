"""Tests for logslice.cache module."""

import json
import os
import time
import unittest
from unittest.mock import patch

from logslice import cache


class TestCacheKey(unittest.TestCase):
    def test_same_inputs_produce_same_key(self):
        k1 = cache._cache_key("/var/log/app.log", {"pattern": "ERROR"})
        k2 = cache._cache_key("/var/log/app.log", {"pattern": "ERROR"})
        self.assertEqual(k1, k2)

    def test_different_params_produce_different_key(self):
        k1 = cache._cache_key("/var/log/app.log", {"pattern": "ERROR"})
        k2 = cache._cache_key("/var/log/app.log", {"pattern": "WARN"})
        self.assertNotEqual(k1, k2)

    def test_key_is_hex_string(self):
        k = cache._cache_key("file.log", {})
        self.assertTrue(all(c in "0123456789abcdef" for c in k))


class TestCacheGetPut(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmpdir = tempfile.mkdtemp()
        self.filepath = "/logs/test.log"
        self.params = {"pattern": "ERROR", "start": None}

    def test_get_returns_none_when_no_entry(self):
        result = cache.get(self.filepath, self.params, cache_dir=self.tmpdir)
        self.assertIsNone(result)

    def test_put_and_get_round_trip(self):
        data = ["line1", "line2"]
        cache.put(self.filepath, self.params, data, cache_dir=self.tmpdir)
        result = cache.get(self.filepath, self.params, cache_dir=self.tmpdir)
        self.assertEqual(result, data)

    def test_get_returns_none_after_ttl_expired(self):
        cache.put(self.filepath, self.params, ["x"], cache_dir=self.tmpdir)
        with patch("logslice.cache.time") as mock_time:
            mock_time.time.return_value = time.time() + 9999
            result = cache.get(self.filepath, self.params, cache_dir=self.tmpdir, ttl=1)
        self.assertIsNone(result)

    def test_get_returns_none_on_corrupt_file(self):
        key = cache._cache_key(self.filepath, self.params)
        path = cache._cache_path(self.tmpdir, key)
        os.makedirs(self.tmpdir, exist_ok=True)
        with open(path, "w") as f:
            f.write("not valid json")
        result = cache.get(self.filepath, self.params, cache_dir=self.tmpdir)
        self.assertIsNone(result)


class TestCacheInvalidateAndClear(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmpdir = tempfile.mkdtemp()
        self.filepath = "/logs/app.log"
        self.params = {"q": "timeout"}

    def test_invalidate_removes_entry(self):
        cache.put(self.filepath, self.params, ["hit"], cache_dir=self.tmpdir)
        removed = cache.invalidate(self.filepath, self.params, cache_dir=self.tmpdir)
        self.assertTrue(removed)
        self.assertIsNone(cache.get(self.filepath, self.params, cache_dir=self.tmpdir))

    def test_invalidate_returns_false_when_no_entry(self):
        result = cache.invalidate(self.filepath, self.params, cache_dir=self.tmpdir)
        self.assertFalse(result)

    def test_clear_all_removes_all_entries(self):
        cache.put(self.filepath, {"a": 1}, ["a"], cache_dir=self.tmpdir)
        cache.put(self.filepath, {"b": 2}, ["b"], cache_dir=self.tmpdir)
        count = cache.clear_all(cache_dir=self.tmpdir)
        self.assertEqual(count, 2)

    def test_clear_all_on_empty_dir_returns_zero(self):
        count = cache.clear_all(cache_dir=self.tmpdir)
        self.assertEqual(count, 0)

    def test_clear_all_nonexistent_dir_returns_zero(self):
        count = cache.clear_all(cache_dir="/tmp/logslice_nonexistent_xyz")
        self.assertEqual(count, 0)
