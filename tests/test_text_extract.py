import pytest
from pathlib import Path

from core.text_extract import extract_text, MAX_CHARS


class TestPlainText:
    def test_read_txt(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("Hello, world!", encoding="utf-8")
        assert extract_text(str(f)) == "Hello, world!"

    def test_read_md(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("# Title\n\nParagraph.", encoding="utf-8")
        text = extract_text(str(f))
        assert "Title" in text
        assert "Paragraph" in text

    def test_truncates_long_text(self, tmp_path):
        f = tmp_path / "long.txt"
        f.write_text("x" * (MAX_CHARS + 1000), encoding="utf-8")
        result = extract_text(str(f))
        assert len(result) == MAX_CHARS


class TestHtml:
    def test_strips_tags(self, tmp_path):
        f = tmp_path / "test.html"
        f.write_text("<html><body><p>Hello <b>world</b></p></body></html>", encoding="utf-8")
        text = extract_text(str(f))
        assert "Hello" in text
        assert "world" in text
        assert "<" not in text


class TestDocx:
    def test_read_docx(self):
        docx_path = Path(__file__).parent.parent / "data" / "test_docx.docx"
        if not docx_path.exists():
            pytest.skip("test_docx.docx not available")
        text = extract_text(str(docx_path))
        assert len(text) > 0


class TestUnsupported:
    def test_raises_on_unknown_extension(self, tmp_path):
        f = tmp_path / "test.xyz"
        f.write_text("data")
        with pytest.raises(ValueError, match="Unsupported"):
            extract_text(str(f))
