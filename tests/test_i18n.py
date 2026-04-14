import json
from pathlib import Path

from i18n import available_languages, current_language, load_fallback, set_language, tr

I18N_DIR = Path(__file__).parent.parent / "src" / "i18n"


class TestAvailableLanguages:
    def test_includes_en_and_fr(self):
        langs = available_languages()
        assert "en" in langs
        assert "fr" in langs

    def test_returns_sorted_list(self):
        langs = available_languages()
        assert langs == sorted(langs)


class TestSetLanguage:
    def test_switch_to_french(self):
        set_language("fr")
        assert current_language() == "fr"

    def test_switch_to_english(self):
        set_language("en")
        assert current_language() == "en"

    def test_unknown_language_does_not_crash(self):
        set_language("xx")
        assert current_language() == "xx"
        # Falls back to fallback (en)
        set_language("en")


class TestTranslation:
    def test_english_translation(self):
        set_language("en")
        assert tr("window_title") == "Auto Caption"

    def test_french_translation(self):
        set_language("fr")
        result = tr("start_button")
        assert result == "Lancer le renommage"
        set_language("en")

    def test_missing_key_returns_key(self):
        set_language("en")
        assert tr("nonexistent_key_xyz") == "nonexistent_key_xyz"

    def test_placeholder_substitution(self):
        set_language("en")
        result = tr("status_done", count=5)
        assert "5" in result

    def test_fallback_to_english(self):
        set_language("xx")  # nonexistent language
        load_fallback()
        result = tr("window_title")
        assert result == "Auto Caption"
        set_language("en")


class TestJsonIntegrity:
    def test_all_json_files_are_valid(self):
        for f in I18N_DIR.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            assert isinstance(data, dict)
            assert len(data) > 0

    def test_en_and_fr_have_same_keys(self):
        en = json.loads((I18N_DIR / "en.json").read_text(encoding="utf-8"))
        fr = json.loads((I18N_DIR / "fr.json").read_text(encoding="utf-8"))
        assert set(en.keys()) == set(fr.keys())

    def test_no_empty_values(self):
        for f in I18N_DIR.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            for key, value in data.items():
                assert value.strip(), f"Empty value for key '{key}' in {f.name}"
