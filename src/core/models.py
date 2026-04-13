"""HuggingFace model cache management — list, inspect, and delete downloaded models."""

from pathlib import Path


def get_downloaded_models() -> list[dict]:
    """List all downloaded HuggingFace models with size info."""
    try:
        from huggingface_hub import scan_cache_dir
        cache_info = scan_cache_dir()
        models = []
        for repo in cache_info.repos:
            size_mb = repo.size_on_disk / (1024 * 1024)
            models.append({
                "repo_id": repo.repo_id,
                "size_mb": round(size_mb, 1),
                "nb_files": repo.nb_files,
                "last_modified": max(rev.last_modified for rev in repo.revisions),
            })
        return sorted(models, key=lambda x: x["size_mb"], reverse=True)
    except Exception:
        return []


def delete_model(repo_id: str) -> bool:
    """Delete a downloaded model from the HuggingFace cache."""
    try:
        from huggingface_hub import scan_cache_dir
        cache_info = scan_cache_dir()
        hashes = []
        for repo in cache_info.repos:
            if repo.repo_id == repo_id:
                for rev in repo.revisions:
                    hashes.append(rev.commit_hash)
        if hashes:
            strategy = cache_info.delete_revisions(*hashes)
            strategy.execute()
            return True
    except Exception:
        pass
    return False


def total_cache_size_mb() -> float:
    """Total size of all downloaded models in MB."""
    try:
        from huggingface_hub import scan_cache_dir
        return round(scan_cache_dir().size_on_disk / (1024 * 1024), 1)
    except Exception:
        return 0.0


def cache_dir_path() -> str:
    """Path to the HuggingFace cache directory."""
    try:
        from huggingface_hub import constants
        return str(constants.HF_HUB_CACHE)
    except Exception:
        return str(Path.home() / ".cache" / "huggingface" / "hub")
