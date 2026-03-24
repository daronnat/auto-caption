import shutil
from pathlib import Path


def rename_file(original_path: str, new_name: str, mode: str = "copy") -> str:
    """
    Rename or copy a file with the new stem.
    Returns the destination path as a string.
    """
    src = Path(original_path)
    dest_name = new_name + src.suffix

    if mode == "rename":
        dest = _unique_path(src.parent / dest_name)
        src.rename(dest)
    else:  # copy to ai-renamed/
        ai_dir = src.parent / "ai-renamed"
        ai_dir.mkdir(exist_ok=True)
        dest = _unique_path(ai_dir / dest_name)
        shutil.copy2(str(src), str(dest))

    return str(dest)


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 1
    while True:
        candidate = path.parent / f"{path.stem}_{counter}{path.suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
