from pathlib import Path

DOCUMENT_EXTENSIONS = {".txt", ".md", ".docx", ".pdf", ".rst", ".html", ".htm"}

MAX_CHARS = 3000


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext in (".txt", ".md", ".rst"):
        return _read_plain(path)
    elif ext in (".html", ".htm"):
        return _read_html(path)
    elif ext == ".docx":
        return _read_docx(path)
    elif ext == ".pdf":
        return _read_pdf(path)
    else:
        raise ValueError(f"Unsupported document format: {ext}")


def _read_plain(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:MAX_CHARS]


def _read_html(path: Path) -> str:
    import re
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_CHARS]


def _read_docx(path: Path) -> str:
    from docx import Document
    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs)
    return text[:MAX_CHARS]


def _read_pdf(path: Path) -> str:
    import fitz  # PyMuPDF
    doc = fitz.open(str(path))
    parts = []
    for page in doc:
        parts.append(page.get_text())
        if len("".join(parts)) > MAX_CHARS:
            break
    doc.close()
    return "".join(parts)[:MAX_CHARS]
