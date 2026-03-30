import json
from pathlib import Path

_strings: dict[str, str] = {}
_fallback: dict[str, str] = {}
_current_lang = "en"
_I18N_DIR = Path(__file__).parent


def set_language(lang: str):
    global _strings, _current_lang
    _current_lang = lang
    path = _I18N_DIR / f"{lang}.json"
    if path.exists():
        _strings = json.loads(path.read_text(encoding="utf-8"))
    else:
        _strings = {}


def load_fallback():
    global _fallback
    path = _I18N_DIR / "en.json"
    if path.exists():
        _fallback = json.loads(path.read_text(encoding="utf-8"))


def tr(key: str, **kwargs) -> str:
    text = _strings.get(key) or _fallback.get(key) or key
    if kwargs:
        text = text.format(**kwargs)
    return text


def current_language() -> str:
    return _current_lang


def available_languages() -> list[str]:
    return sorted(p.stem for p in _I18N_DIR.glob("*.json"))


load_fallback()
