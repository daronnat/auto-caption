from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

DARK_COLORS = {
    "window": "#1e1e2e",
    "window_text": "#cdd6f4",
    "base": "#181825",
    "alt_base": "#1e1e2e",
    "text": "#cdd6f4",
    "button": "#313244",
    "button_text": "#cdd6f4",
    "highlight": "#89b4fa",
    "highlight_text": "#1e1e2e",
    "mid": "#45475a",
    "dark": "#11111b",
    "light": "#585b70",
    "link": "#89b4fa",
    "disabled_text": "#6c7086",
}

LIGHT_COLORS = {
    "window": "#eff1f5",
    "window_text": "#4c4f69",
    "base": "#ffffff",
    "alt_base": "#e6e9ef",
    "text": "#4c4f69",
    "button": "#ccd0da",
    "button_text": "#4c4f69",
    "highlight": "#1e66f5",
    "highlight_text": "#ffffff",
    "mid": "#9ca0b0",
    "dark": "#bcc0cc",
    "light": "#e6e9ef",
    "link": "#1e66f5",
    "disabled_text": "#9ca0b0",
}

DARK_STYLESHEET = """
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QPushButton {
    padding: 6px 14px;
    border-radius: 4px;
    border: 1px solid #45475a;
    background: #313244;
}
QPushButton:hover { background: #45475a; }
QPushButton:pressed { background: #585b70; }
QPushButton:checked { background: #89b4fa; color: #1e1e2e; border-color: #89b4fa; }
QPushButton:disabled { background: #1e1e2e; color: #6c7086; }
QProgressBar {
    border: 1px solid #45475a;
    border-radius: 4px;
    text-align: center;
    background: #181825;
    color: #cdd6f4;
    height: 22px;
}
QProgressBar::chunk { background: #89b4fa; border-radius: 3px; }
QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px;
    background: #181825;
}
QListWidget {
    border: 1px solid #45475a;
    border-radius: 4px;
    background: #181825;
}
QListWidget::item:selected { background: #313244; }
QSplitter::handle { background: #45475a; width: 2px; }
QComboBox::drop-down { border: none; padding-right: 6px; }
"""

LIGHT_STYLESHEET = """
QGroupBox {
    border: 1px solid #bcc0cc;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QPushButton {
    padding: 6px 14px;
    border-radius: 4px;
    border: 1px solid #bcc0cc;
    background: #ccd0da;
}
QPushButton:hover { background: #bcc0cc; }
QPushButton:pressed { background: #9ca0b0; }
QPushButton:checked { background: #1e66f5; color: #ffffff; border-color: #1e66f5; }
QPushButton:disabled { background: #e6e9ef; color: #9ca0b0; }
QProgressBar {
    border: 1px solid #bcc0cc;
    border-radius: 4px;
    text-align: center;
    background: #e6e9ef;
    color: #4c4f69;
    height: 22px;
}
QProgressBar::chunk { background: #1e66f5; border-radius: 3px; }
QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
    border: 1px solid #bcc0cc;
    border-radius: 4px;
    padding: 4px;
    background: #ffffff;
}
QListWidget {
    border: 1px solid #bcc0cc;
    border-radius: 4px;
    background: #ffffff;
}
QListWidget::item:selected { background: #ccd0da; }
QSplitter::handle { background: #bcc0cc; width: 2px; }
QComboBox::drop-down { border: none; padding-right: 6px; }
"""


def _build_palette(colors: dict) -> QPalette:
    p = QPalette()
    p.setColor(QPalette.Window, QColor(colors["window"]))
    p.setColor(QPalette.WindowText, QColor(colors["window_text"]))
    p.setColor(QPalette.Base, QColor(colors["base"]))
    p.setColor(QPalette.AlternateBase, QColor(colors["alt_base"]))
    p.setColor(QPalette.Text, QColor(colors["text"]))
    p.setColor(QPalette.Button, QColor(colors["button"]))
    p.setColor(QPalette.ButtonText, QColor(colors["button_text"]))
    p.setColor(QPalette.Highlight, QColor(colors["highlight"]))
    p.setColor(QPalette.HighlightedText, QColor(colors["highlight_text"]))
    p.setColor(QPalette.Mid, QColor(colors["mid"]))
    p.setColor(QPalette.Dark, QColor(colors["dark"]))
    p.setColor(QPalette.Light, QColor(colors["light"]))
    p.setColor(QPalette.Link, QColor(colors["link"]))
    p.setColor(QPalette.Disabled, QPalette.Text, QColor(colors["disabled_text"]))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(colors["disabled_text"]))
    return p


def apply_theme(app: QApplication, theme: str):
    if theme == "dark":
        app.setPalette(_build_palette(DARK_COLORS))
        app.setStyleSheet(DARK_STYLESHEET)
    else:
        app.setPalette(_build_palette(LIGHT_COLORS))
        app.setStyleSheet(LIGHT_STYLESHEET)
