import sys
from pathlib import Path

# Ensure src/ is on the path when run as a script or via PyInstaller
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication

from core.config import load_config
from i18n import set_language
from ui.theme import apply_theme
from ui.main_window import MainWindow
from version import __version__


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Auto Caption")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("AutoCaption")
    app.setStyle("Fusion")

    config = load_config()
    set_language(config.get("language", "en"))
    apply_theme(app, config.get("theme", "dark"))

    win = MainWindow(config)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
