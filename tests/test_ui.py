"""UI tests using QT_QPA_PLATFORM=offscreen (no display required)."""

import os
import sys

# Must be set before any Qt import
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
from PySide6.QtWidgets import QApplication

from i18n import set_language


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication once for all UI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
    set_language("en")
    return app


def _close_window(win):
    """Safely close a MainWindow, waiting for background threads."""
    if win._gpu_detector is not None and win._gpu_detector.isRunning():
        win._gpu_detector.wait(3000)
    win.close()


class TestTheme:
    def test_apply_dark_theme(self, qapp):
        from ui.theme import apply_theme
        apply_theme(qapp, "dark")
        palette = qapp.palette()
        assert palette.window().color().lightness() < 50

    def test_apply_light_theme(self, qapp):
        from ui.theme import apply_theme
        apply_theme(qapp, "light")
        palette = qapp.palette()
        assert palette.window().color().lightness() > 200

    def test_toggle_theme(self, qapp):
        from ui.theme import apply_theme
        apply_theme(qapp, "dark")
        dark_color = qapp.palette().window().color().name()
        apply_theme(qapp, "light")
        light_color = qapp.palette().window().color().name()
        assert dark_color != light_color


class TestMainWindow:
    def _make_window(self, qapp):
        from ui.theme import apply_theme
        from core.config import load_config
        from ui.main_window import MainWindow
        apply_theme(qapp, "dark")
        config = load_config()
        return MainWindow(config)

    def test_window_creates_without_crash(self, qapp):
        win = self._make_window(qapp)
        assert win.windowTitle() == "Auto Caption"
        _close_window(win)

    def test_window_minimum_size(self, qapp):
        win = self._make_window(qapp)
        assert win.minimumWidth() >= 1000
        assert win.minimumHeight() >= 650
        _close_window(win)

    def test_retranslate_does_not_crash(self, qapp):
        win = self._make_window(qapp)
        set_language("fr")
        win._retranslate()
        set_language("en")
        win._retranslate()
        _close_window(win)

    def test_file_list_starts_empty(self, qapp):
        win = self._make_window(qapp)
        assert win.file_list.count() == 0
        _close_window(win)

    def test_status_bar_has_gpu_label(self, qapp):
        win = self._make_window(qapp)
        assert win._gpu_status is not None
        assert win._vram_status is not None
        assert win._cache_status is not None
        _close_window(win)

    def test_add_item_increments_count(self, qapp, tmp_path):
        win = self._make_window(qapp)
        fake = tmp_path / "test.txt"
        fake.write_text("hello")
        win._add_item(str(fake))
        win._update_file_count()
        assert win.file_list.count() == 1
        _close_window(win)

    def test_clear_all_empties_list(self, qapp, tmp_path):
        win = self._make_window(qapp)
        fake = tmp_path / "test.txt"
        fake.write_text("hello")
        win._add_item(str(fake))
        win._clear_all()
        assert win.file_list.count() == 0
        _close_window(win)

    def test_duplicate_add_is_ignored(self, qapp, tmp_path):
        win = self._make_window(qapp)
        fake = tmp_path / "test.txt"
        fake.write_text("hello")
        win._add_item(str(fake))
        win._add_item(str(fake))  # duplicate
        assert win.file_list.count() == 1
        _close_window(win)


class TestPromptManager:
    def test_creates_without_crash(self, qapp):
        from ui.prompt_manager import PromptManager
        pm = PromptManager()
        assert pm is not None

    def test_get_prompt_texts_returns_tuple(self, qapp):
        from ui.prompt_manager import PromptManager
        pm = PromptManager()
        img, doc = pm.get_prompt_texts()
        assert isinstance(img, str)
        assert isinstance(doc, str)
        assert len(img) > 0
        assert len(doc) > 0

    def test_get_params_returns_dict(self, qapp):
        from ui.prompt_manager import PromptManager
        pm = PromptManager()
        params = pm.get_params()
        assert "temperature" in params
        assert "top_p" in params
        assert "max_new_tokens" in params

    def test_retranslate_does_not_crash(self, qapp):
        from ui.prompt_manager import PromptManager
        pm = PromptManager()
        set_language("fr")
        pm.retranslate()
        set_language("en")
        pm.retranslate()


class TestProgressWidget:
    def test_creates_hidden(self, qapp):
        from ui.progress_widget import ProgressWidget
        pw = ProgressWidget()
        assert not pw.isVisible()

    def test_start_makes_visible(self, qapp):
        from ui.progress_widget import ProgressWidget
        pw = ProgressWidget()
        pw.start(10)
        assert pw.isVisible()

    def test_update_and_finish(self, qapp):
        from ui.progress_widget import ProgressWidget
        pw = ProgressWidget()
        pw.start(5)
        pw.update(3)
        pw.finish()
        assert pw.isVisible()

    def test_reset_hides(self, qapp):
        from ui.progress_widget import ProgressWidget
        pw = ProgressWidget()
        pw.start(5)
        pw.reset()
        assert not pw.isVisible()


class TestModelManagerDialog:
    def test_creates_without_crash(self, qapp):
        from ui.model_manager import ModelManagerDialog
        dlg = ModelManagerDialog()
        assert dlg.windowTitle() != ""
        dlg.close()
