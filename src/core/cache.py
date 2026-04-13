"""Inference result cache to avoid re-processing unchanged files."""

import hashlib
import json
from pathlib import Path

from core.config import CONFIG_DIR

CACHE_DIR = CONFIG_DIR / "cache"


def _hash_key(path: str, prompt: str, params: dict) -> str:
    """Deterministic hash from file identity + prompt + params."""
    h = hashlib.sha256()
    p = Path(path)
    if p.exists():
        stat = p.stat()
        # Use name + size + mtime for fast change detection (no full file hash)
        h.update(f"{p.name}:{stat.st_size}:{stat.st_mtime_ns}".encode())
    h.update(prompt.encode())
    h.update(json.dumps(params, sort_keys=True).encode())
    return h.hexdigest()[:16]


def get_cached(path: str, prompt: str, params: dict) -> str | None:
    """Return cached result or None."""
    key = _hash_key(path, prompt, params)
    cache_file = CACHE_DIR / f"{key}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8")).get("result")
        except (json.JSONDecodeError, OSError):
            pass
    return None


def set_cached(path: str, prompt: str, params: dict, result: str):
    """Store a result in the cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = _hash_key(path, prompt, params)
    cache_file = CACHE_DIR / f"{key}.json"
    cache_file.write_text(
        json.dumps({"path": path, "result": result}, ensure_ascii=False),
        encoding="utf-8",
    )


def clear_cache() -> int:
    """Delete all cached results. Returns number of entries cleared."""
    if not CACHE_DIR.exists():
        return 0
    count = 0
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()
        count += 1
    return count


def cache_size_str() -> str:
    """Human-readable total cache size."""
    if not CACHE_DIR.exists():
        return "0 KB"
    total = sum(f.stat().st_size for f in CACHE_DIR.glob("*.json"))
    if total < 1024:
        return f"{total} B"
    if total < 1024 * 1024:
        return f"{total // 1024} KB"
    return f"{total / (1024 * 1024):.1f} MB"


def cache_count() -> int:
    """Number of cached entries."""
    if not CACHE_DIR.exists():
        return 0
    return sum(1 for _ in CACHE_DIR.glob("*.json"))
