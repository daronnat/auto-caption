from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

# ── Catppuccin-based glassmorphism palette ──────────────────────

DARK_COLORS = {
    "window": "#0d0d1a",
    "window_text": "#cdd6f4",
    "base": "#0a0a15",
    "alt_base": "#111122",
    "text": "#cdd6f4",
    "button": "#1e1e32",
    "button_text": "#cdd6f4",
    "highlight": "#89b4fa",
    "highlight_text": "#0d0d1a",
    "mid": "#2a2a44",
    "dark": "#08080f",
    "light": "#3a3a55",
    "link": "#89b4fa",
    "disabled_text": "#555570",
}

LIGHT_COLORS = {
    "window": "#f0f1f8",
    "window_text": "#4c4f69",
    "base": "#f8f9fe",
    "alt_base": "#ecedf6",
    "text": "#4c4f69",
    "button": "#e0e2ee",
    "button_text": "#4c4f69",
    "highlight": "#1e66f5",
    "highlight_text": "#ffffff",
    "mid": "#b0b3c6",
    "dark": "#c8cad8",
    "light": "#ecedf6",
    "link": "#1e66f5",
    "disabled_text": "#9ca0b0",
}

# ── Dark glassmorphism stylesheet ───────────────────────────────

DARK_STYLESHEET = """
/* ── Main container gradient ── */
#centralWidget {
    background: qlineargradient(x1:0, y1:0, x2:0.4, y2:1,
        stop:0 #0d0d1a, stop:0.5 #111128, stop:1 #16162e);
}

/* ── Glass panels ── */
QGroupBox {
    background-color: rgba(25, 25, 45, 180);
    border: 1px solid rgba(137, 180, 250, 35);
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px 10px 10px 10px;
    font-weight: bold;
    color: #cdd6f4;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: #b4befe;
}

/* ── Glass buttons ── */
QPushButton {
    padding: 7px 16px;
    border-radius: 6px;
    border: 1px solid rgba(137, 180, 250, 40);
    background-color: rgba(35, 35, 60, 200);
    color: #cdd6f4;
}
QPushButton:hover {
    background-color: rgba(55, 55, 85, 220);
    border-color: rgba(137, 180, 250, 70);
}
QPushButton:pressed {
    background-color: rgba(70, 70, 100, 220);
}
QPushButton:checked {
    background-color: rgba(137, 180, 250, 200);
    color: #0d0d1a;
    border-color: rgba(137, 180, 250, 255);
}
QPushButton:disabled {
    background-color: rgba(15, 15, 25, 150);
    color: rgba(85, 85, 112, 180);
    border-color: rgba(50, 50, 70, 80);
}

/* ── Glass progress bar ── */
QProgressBar {
    border: 1px solid rgba(137, 180, 250, 30);
    border-radius: 6px;
    text-align: center;
    background-color: rgba(8, 8, 18, 180);
    color: #cdd6f4;
    height: 24px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #89b4fa, stop:1 #b4befe);
    border-radius: 5px;
}

/* ── Glass inputs ── */
QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
    border: 1px solid rgba(137, 180, 250, 25);
    border-radius: 6px;
    padding: 5px;
    background-color: rgba(8, 8, 20, 180);
    color: #cdd6f4;
    selection-background-color: rgba(137, 180, 250, 80);
}
QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {
    border-color: rgba(137, 180, 250, 90);
}

/* ── Glass list ── */
QListWidget {
    border: 1px solid rgba(137, 180, 250, 25);
    border-radius: 8px;
    background-color: rgba(8, 8, 18, 160);
    color: #cdd6f4;
}
QListWidget::item {
    padding: 3px;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: rgba(137, 180, 250, 40);
}
QListWidget::item:hover {
    background-color: rgba(40, 40, 65, 140);
}

/* ── Glass tabs ── */
QTabWidget::pane {
    border: 1px solid rgba(137, 180, 250, 25);
    border-radius: 6px;
    background-color: rgba(15, 15, 30, 150);
    top: -1px;
}
QTabBar::tab {
    padding: 6px 18px;
    border: 1px solid rgba(137, 180, 250, 15);
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    background-color: rgba(25, 25, 45, 140);
    color: #8888aa;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: rgba(35, 35, 60, 200);
    color: #cdd6f4;
    border-color: rgba(137, 180, 250, 35);
}
QTabBar::tab:hover:!selected {
    background-color: rgba(35, 35, 55, 170);
    color: #a6adc8;
}

/* ── Misc ── */
QSplitter::handle {
    background: rgba(137, 180, 250, 20);
    width: 2px;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: rgba(18, 18, 35, 245);
    border: 1px solid rgba(137, 180, 250, 35);
    border-radius: 4px;
    selection-background-color: rgba(137, 180, 250, 60);
    color: #cdd6f4;
}
QRadioButton {
    spacing: 6px;
    color: #cdd6f4;
}
QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border-radius: 7px;
    border: 2px solid rgba(137, 180, 250, 60);
    background-color: rgba(8, 8, 18, 180);
}
QRadioButton::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}
QLabel {
    color: #cdd6f4;
}
QToolTip {
    background-color: rgba(20, 20, 38, 240);
    border: 1px solid rgba(137, 180, 250, 40);
    border-radius: 4px;
    color: #cdd6f4;
    padding: 4px 8px;
}

/* ── Accent start button ── */
#startButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(137, 180, 250, 200), stop:1 rgba(180, 190, 254, 200));
    color: #0d0d1a;
    font-weight: bold;
    font-size: 13px;
    padding: 10px 28px;
    border-radius: 8px;
    border: 1px solid rgba(137, 180, 250, 150);
}
#startButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(137, 180, 250, 240), stop:1 rgba(180, 190, 254, 240));
}
#startButton:pressed {
    background: rgba(137, 180, 250, 255);
}
#startButton:disabled {
    background: rgba(40, 40, 60, 180);
    color: rgba(85, 85, 112, 180);
    border-color: rgba(50, 50, 70, 80);
}

/* ── Status bar ── */
QStatusBar {
    background-color: rgba(8, 8, 15, 200);
    border-top: 1px solid rgba(137, 180, 250, 20);
    font-size: 12px;
}
QStatusBar QLabel {
    padding: 2px 8px;
    color: #8888aa;
}
QStatusBar::item {
    border: none;
}
"""

# ── Light glassmorphism stylesheet ──────────────────────────────

LIGHT_STYLESHEET = """
/* ── Main container gradient ── */
#centralWidget {
    background: qlineargradient(x1:0, y1:0, x2:0.4, y2:1,
        stop:0 #f8f9fe, stop:0.5 #f0f1fa, stop:1 #e8eaf5);
}

/* ── Glass panels ── */
QGroupBox {
    background-color: rgba(255, 255, 255, 150);
    border: 1px solid rgba(0, 0, 0, 20);
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px 10px 10px 10px;
    font-weight: bold;
    color: #4c4f69;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: #1e66f5;
}

/* ── Glass buttons ── */
QPushButton {
    padding: 7px 16px;
    border-radius: 6px;
    border: 1px solid rgba(0, 0, 0, 22);
    background-color: rgba(255, 255, 255, 170);
    color: #4c4f69;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 220);
    border-color: rgba(30, 102, 245, 50);
}
QPushButton:pressed {
    background-color: rgba(230, 233, 239, 220);
}
QPushButton:checked {
    background-color: rgba(30, 102, 245, 210);
    color: #ffffff;
    border-color: rgba(30, 102, 245, 255);
}
QPushButton:disabled {
    background-color: rgba(239, 241, 245, 140);
    color: rgba(156, 160, 176, 180);
    border-color: rgba(0, 0, 0, 10);
}

/* ── Glass progress bar ── */
QProgressBar {
    border: 1px solid rgba(0, 0, 0, 15);
    border-radius: 6px;
    text-align: center;
    background-color: rgba(255, 255, 255, 120);
    color: #4c4f69;
    height: 24px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1e66f5, stop:1 #7287fd);
    border-radius: 5px;
}

/* ── Glass inputs ── */
QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
    border: 1px solid rgba(0, 0, 0, 15);
    border-radius: 6px;
    padding: 5px;
    background-color: rgba(255, 255, 255, 190);
    color: #4c4f69;
    selection-background-color: rgba(30, 102, 245, 50);
}
QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {
    border-color: rgba(30, 102, 245, 70);
}

/* ── Glass list ── */
QListWidget {
    border: 1px solid rgba(0, 0, 0, 12);
    border-radius: 8px;
    background-color: rgba(255, 255, 255, 140);
    color: #4c4f69;
}
QListWidget::item {
    padding: 3px;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: rgba(30, 102, 245, 30);
}
QListWidget::item:hover {
    background-color: rgba(230, 233, 240, 140);
}

/* ── Glass tabs ── */
QTabWidget::pane {
    border: 1px solid rgba(0, 0, 0, 12);
    border-radius: 6px;
    background-color: rgba(255, 255, 255, 100);
    top: -1px;
}
QTabBar::tab {
    padding: 6px 18px;
    border: 1px solid rgba(0, 0, 0, 8);
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    background-color: rgba(255, 255, 255, 90);
    color: #8888a0;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: rgba(255, 255, 255, 190);
    color: #4c4f69;
    border-color: rgba(0, 0, 0, 15);
}
QTabBar::tab:hover:!selected {
    background-color: rgba(255, 255, 255, 150);
    color: #6c6f85;
}

/* ── Misc ── */
QSplitter::handle {
    background: rgba(0, 0, 0, 10);
    width: 2px;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: rgba(255, 255, 255, 245);
    border: 1px solid rgba(0, 0, 0, 15);
    border-radius: 4px;
    selection-background-color: rgba(30, 102, 245, 30);
    color: #4c4f69;
}
QRadioButton {
    spacing: 6px;
    color: #4c4f69;
}
QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border-radius: 7px;
    border: 2px solid rgba(30, 102, 245, 50);
    background-color: rgba(255, 255, 255, 200);
}
QRadioButton::indicator:checked {
    background-color: #1e66f5;
    border-color: #1e66f5;
}
QLabel {
    color: #4c4f69;
}
QToolTip {
    background-color: rgba(255, 255, 255, 240);
    border: 1px solid rgba(0, 0, 0, 15);
    border-radius: 4px;
    color: #4c4f69;
    padding: 4px 8px;
}

/* ── Accent start button ── */
#startButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(30, 102, 245, 220), stop:1 rgba(114, 135, 253, 220));
    color: #ffffff;
    font-weight: bold;
    font-size: 13px;
    padding: 10px 28px;
    border-radius: 8px;
    border: 1px solid rgba(30, 102, 245, 180);
}
#startButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(30, 102, 245, 255), stop:1 rgba(114, 135, 253, 255));
}
#startButton:pressed {
    background: rgba(30, 102, 245, 255);
}
#startButton:disabled {
    background: rgba(200, 203, 218, 180);
    color: rgba(156, 160, 176, 180);
    border-color: rgba(0, 0, 0, 15);
}

/* ── Status bar ── */
QStatusBar {
    background-color: rgba(255, 255, 255, 180);
    border-top: 1px solid rgba(0, 0, 0, 10);
    font-size: 12px;
}
QStatusBar QLabel {
    padding: 2px 8px;
    color: #6c6f85;
}
QStatusBar::item {
    border: none;
}
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
