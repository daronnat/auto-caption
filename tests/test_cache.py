import json
from pathlib import Path

from core.cache import (
    get_cached, set_cached, clear_cache, cache_size_str, cache_count, CACHE_DIR,
)


class TestCache:
    def setup_method(self, method):
        """Store original CACHE_DIR for restoration."""
        self._orig_cache_dir = CACHE_DIR

    def test_miss_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr("core.cache.CACHE_DIR", tmp_path / "cache")
        assert get_cached("/fake/path.jpg", "prompt", {}) is None

    def test_set_then_get(self, tmp_path, monkeypatch):
        cache_dir = tmp_path / "cache"
        monkeypatch.setattr("core.cache.CACHE_DIR", cache_dir)

        # Create a fake file to hash against
        fake_file = tmp_path / "photo.jpg"
        fake_file.write_bytes(b"fake image data")

        params = {"temperature": 0.0, "naming_style": "snake_case"}
        set_cached(str(fake_file), "describe this", params, "sunset_beach")

        result = get_cached(str(fake_file), "describe this", params)
        assert result == "sunset_beach"

    def test_different_prompt_is_cache_miss(self, tmp_path, monkeypatch):
        cache_dir = tmp_path / "cache"
        monkeypatch.setattr("core.cache.CACHE_DIR", cache_dir)

        fake_file = tmp_path / "photo.jpg"
        fake_file.write_bytes(b"fake image data")

        params = {"temperature": 0.0}
        set_cached(str(fake_file), "prompt A", params, "result_a")

        assert get_cached(str(fake_file), "prompt B", params) is None

    def test_different_params_is_cache_miss(self, tmp_path, monkeypatch):
        cache_dir = tmp_path / "cache"
        monkeypatch.setattr("core.cache.CACHE_DIR", cache_dir)

        fake_file = tmp_path / "photo.jpg"
        fake_file.write_bytes(b"fake image data")

        set_cached(str(fake_file), "prompt", {"temp": 0.0}, "result_cold")
        assert get_cached(str(fake_file), "prompt", {"temp": 0.5}) is None

    def test_clear_cache(self, tmp_path, monkeypatch):
        cache_dir = tmp_path / "cache"
        monkeypatch.setattr("core.cache.CACHE_DIR", cache_dir)

        fake_file = tmp_path / "photo.jpg"
        fake_file.write_bytes(b"data")
        set_cached(str(fake_file), "p", {}, "r")
        assert cache_count() == 1

        cleared = clear_cache()
        assert cleared == 1
        assert cache_count() == 0

    def test_cache_size_str_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr("core.cache.CACHE_DIR", tmp_path / "nonexistent")
        assert cache_size_str() == "0 KB"

    def test_cache_count_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr("core.cache.CACHE_DIR", tmp_path / "nonexistent")
        assert cache_count() == 0

    def test_cache_invalidated_on_file_change(self, tmp_path, monkeypatch):
        import time
        cache_dir = tmp_path / "cache"
        monkeypatch.setattr("core.cache.CACHE_DIR", cache_dir)

        fake_file = tmp_path / "doc.txt"
        fake_file.write_bytes(b"version 1")
        set_cached(str(fake_file), "prompt", {}, "result_v1")
        assert get_cached(str(fake_file), "prompt", {}) == "result_v1"

        # Modify the file (change size + mtime)
        time.sleep(0.01)
        fake_file.write_bytes(b"version 2 with more content")
        assert get_cached(str(fake_file), "prompt", {}) is None
