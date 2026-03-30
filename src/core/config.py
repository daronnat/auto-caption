import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "auto-caption"
CONFIG_FILE = CONFIG_DIR / "config.json"
PROMPTS_FILE = CONFIG_DIR / "prompts.json"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".tif"}
DOCUMENT_EXTENSIONS = {".txt", ".md", ".docx", ".pdf", ".rst", ".html", ".htm"}
ALL_EXTENSIONS = IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS

DEFAULT_MODEL_ID = "Qwen/Qwen3.5-0.8B"
DEFAULT_GGUF_REPO = "unsloth/Qwen3.5-0.8B-GGUF"
DEFAULT_GGUF_FILE = "Qwen3.5-0.8B-Q4_K_M.gguf"
DEFAULT_MMPROJ_FILE = "Qwen3.5-0.8B-mmproj-f16.gguf"

DEFAULTS = {
    "theme": "dark",
    "language": "en",
    "backend": "transformers",
    "model_id": DEFAULT_MODEL_ID,
    "naming_style": "snake_case",
    "max_words": 5,
    "output_mode": "copy",
}

DEFAULT_PROMPT_IMAGE = {
    "name": "Default (Image)",
    "prompt": "Describe this image in {max_words} words or fewer to create a filename. {style_instruction} {extra} Return ONLY the filename without extension. No explanation, no punctuation, no quotes.",
    "temperature": 0.0,
    "top_p": 1.0,
    "max_new_tokens": 50,
}

DEFAULT_PROMPT_DOCUMENT = {
    "name": "Default (Document)",
    "prompt": "Based on the following document content, suggest a filename of {max_words} words or fewer that captures the main topic. {style_instruction} {extra} Return ONLY the filename without extension. No explanation, no punctuation, no quotes.\n\nDocument content:\n{document_text}",
    "temperature": 0.0,
    "top_p": 1.0,
    "max_new_tokens": 50,
}


def _ensure_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    _ensure_dir()
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return {**DEFAULTS, **cfg}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULTS)


def save_config(cfg: dict):
    _ensure_dir()
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def load_prompts() -> list[dict]:
    _ensure_dir()
    if PROMPTS_FILE.exists():
        try:
            prompts = json.loads(PROMPTS_FILE.read_text(encoding="utf-8"))
            if prompts:
                return prompts
        except (json.JSONDecodeError, OSError):
            pass
    return [dict(DEFAULT_PROMPT_IMAGE), dict(DEFAULT_PROMPT_DOCUMENT)]


def save_prompts(prompts: list[dict]):
    _ensure_dir()
    PROMPTS_FILE.write_text(json.dumps(prompts, indent=2), encoding="utf-8")
