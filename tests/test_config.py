
from core.config import (
    ALL_EXTENSIONS,
    DEFAULT_PROMPT_DOCUMENT,
    DEFAULT_PROMPT_IMAGE,
    DEFAULTS,
    DOCUMENT_EXTENSIONS,
    IMAGE_EXTENSIONS,
    load_config,
    load_prompts,
    save_config,
    save_prompts,
)


class TestDefaults:
    def test_defaults_has_required_keys(self):
        for key in ("theme", "language", "backend", "model_id", "naming_style",
                     "max_words", "output_mode"):
            assert key in DEFAULTS

    def test_default_theme_is_dark(self):
        assert DEFAULTS["theme"] == "dark"

    def test_default_language_is_english(self):
        assert DEFAULTS["language"] == "en"


class TestExtensions:
    def test_image_extensions_include_common_formats(self):
        for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            assert ext in IMAGE_EXTENSIONS

    def test_document_extensions_include_common_formats(self):
        for ext in (".txt", ".md", ".pdf", ".docx"):
            assert ext in DOCUMENT_EXTENSIONS

    def test_all_extensions_is_union(self):
        assert ALL_EXTENSIONS == IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS


class TestConfigPersistence:
    def test_load_returns_defaults_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr("core.config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("core.config.CONFIG_FILE", tmp_path / "config.json")
        cfg = load_config()
        assert cfg == DEFAULTS

    def test_save_and_load_roundtrip(self, tmp_path, monkeypatch):
        monkeypatch.setattr("core.config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("core.config.CONFIG_FILE", tmp_path / "config.json")
        custom = {**DEFAULTS, "theme": "light", "max_words": 10}
        save_config(custom)
        loaded = load_config()
        assert loaded["theme"] == "light"
        assert loaded["max_words"] == 10

    def test_load_handles_corrupt_json(self, tmp_path, monkeypatch):
        monkeypatch.setattr("core.config.CONFIG_DIR", tmp_path)
        config_file = tmp_path / "config.json"
        monkeypatch.setattr("core.config.CONFIG_FILE", config_file)
        config_file.write_text("{invalid json", encoding="utf-8")
        cfg = load_config()
        assert cfg == DEFAULTS


class TestPromptsPersistence:
    def test_load_returns_defaults_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr("core.config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("core.config.PROMPTS_FILE", tmp_path / "prompts.json")
        prompts = load_prompts()
        assert len(prompts) == 2
        assert prompts[0]["name"] == DEFAULT_PROMPT_IMAGE["name"]

    def test_save_and_load_roundtrip(self, tmp_path, monkeypatch):
        monkeypatch.setattr("core.config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("core.config.PROMPTS_FILE", tmp_path / "prompts.json")
        custom = [{"name": "test", "prompt": "test prompt"}]
        save_prompts(custom)
        loaded = load_prompts()
        assert len(loaded) == 1
        assert loaded[0]["name"] == "test"


class TestDefaultPrompts:
    def test_image_prompt_has_placeholders(self):
        p = DEFAULT_PROMPT_IMAGE["prompt"]
        assert "{max_words}" in p
        assert "{style_instruction}" in p

    def test_document_prompt_has_placeholders(self):
        p = DEFAULT_PROMPT_DOCUMENT["prompt"]
        assert "{max_words}" in p
        assert "{document_text}" in p
