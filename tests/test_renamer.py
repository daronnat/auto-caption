from pathlib import Path

from core.renamer import rename_file, _unique_path


class TestUniquePath:
    def test_returns_original_when_no_conflict(self, tmp_path):
        target = tmp_path / "hello.txt"
        assert _unique_path(target) == target

    def test_appends_counter_on_conflict(self, tmp_path):
        existing = tmp_path / "hello.txt"
        existing.write_text("exists")
        result = _unique_path(existing)
        assert result == tmp_path / "hello_1.txt"

    def test_increments_counter(self, tmp_path):
        (tmp_path / "hello.txt").write_text("1")
        (tmp_path / "hello_1.txt").write_text("2")
        result = _unique_path(tmp_path / "hello.txt")
        assert result == tmp_path / "hello_2.txt"


class TestRenameFile:
    def test_copy_mode_creates_subfolder(self, tmp_path):
        src = tmp_path / "photo.jpg"
        src.write_bytes(b"fake image")
        rename_file(str(src), "sunset_beach", mode="copy")

        dest = tmp_path / "ai-renamed" / "sunset_beach.jpg"
        assert dest.exists()
        assert src.exists()  # original preserved

    def test_rename_mode_moves_file(self, tmp_path):
        src = tmp_path / "photo.jpg"
        src.write_bytes(b"fake image")
        rename_file(str(src), "sunset_beach", mode="rename")

        dest = tmp_path / "sunset_beach.jpg"
        assert dest.exists()
        assert not src.exists()  # original gone

    def test_copy_mode_handles_collision(self, tmp_path):
        src = tmp_path / "photo.jpg"
        src.write_bytes(b"fake image")

        ai_dir = tmp_path / "ai-renamed"
        ai_dir.mkdir()
        (ai_dir / "sunset_beach.jpg").write_text("occupied")

        rename_file(str(src), "sunset_beach", mode="copy")

        assert (ai_dir / "sunset_beach_1.jpg").exists()

    def test_preserves_extension(self, tmp_path):
        src = tmp_path / "document.pdf"
        src.write_bytes(b"fake pdf")
        rename_file(str(src), "annual_report", mode="copy")

        dest = tmp_path / "ai-renamed" / "annual_report.pdf"
        assert dest.exists()
