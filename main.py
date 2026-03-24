import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QButtonGroup,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from worker import RenameWorker

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".tif"}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Caption")
        self.setMinimumSize(920, 580)
        self._worker = None
        self._setup_ui()

    # ------------------------------------------------------------------ #
    #  UI construction                                                     #
    # ------------------------------------------------------------------ #

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(8)
        root.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._build_file_panel())
        splitter.addWidget(self._build_settings_panel())
        splitter.setSizes([480, 420])
        root.addWidget(splitter, stretch=1)
        root.addWidget(self._build_bottom_panel())

    def _build_file_panel(self) -> QGroupBox:
        box = QGroupBox("Files")
        layout = QVBoxLayout(box)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_list.setIconSize(QSize(56, 56))
        self.file_list.setSpacing(2)
        layout.addWidget(self.file_list)

        btn_row = QHBoxLayout()
        for label, slot in [
            ("Add Files", self._add_files),
            ("Add Folder", self._add_folder),
            ("Remove Selected", self._remove_selected),
            ("Clear All", self.file_list.clear),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)
        return box

    def _build_settings_panel(self) -> QGroupBox:
        box = QGroupBox("Settings")
        layout = QVBoxLayout(box)
        layout.setSpacing(12)

        # ── Naming style ──────────────────────────────────────────────
        style_box = QGroupBox("Naming style")
        style_row = QHBoxLayout(style_box)
        self._style_group = QButtonGroup(self)
        self._style_group.setExclusive(True)
        for idx, label in enumerate(["camelCase", "snake_case", "kebab-case", "Title Case"]):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(idx == 1)  # default: snake_case
            self._style_group.addButton(btn, idx)
            style_row.addWidget(btn)
        layout.addWidget(style_box)

        # ── Max words ─────────────────────────────────────────────────
        words_row = QHBoxLayout()
        words_row.addWidget(QLabel("Max words in filename:"))
        self._max_words = QSpinBox()
        self._max_words.setRange(1, 20)
        self._max_words.setValue(5)
        self._max_words.setFixedWidth(60)
        words_row.addWidget(self._max_words)
        words_row.addStretch()
        layout.addLayout(words_row)

        # ── Extra instructions ────────────────────────────────────────
        layout.addWidget(QLabel("Additional instructions (optional):"))
        self._extra_prompt = QTextEdit()
        self._extra_prompt.setPlaceholderText(
            "e.g. Focus on the main subject. Be concise and descriptive."
        )
        self._extra_prompt.setFixedHeight(90)
        layout.addWidget(self._extra_prompt)

        # ── Output mode ───────────────────────────────────────────────
        out_box = QGroupBox("Output")
        out_layout = QVBoxLayout(out_box)
        self._radio_rename = QRadioButton("Rename files in place")
        self._radio_copy = QRadioButton('Copy renamed files to an "ai-renamed" sub-folder')
        self._radio_copy.setChecked(True)
        out_layout.addWidget(self._radio_rename)
        out_layout.addWidget(self._radio_copy)
        layout.addWidget(out_box)

        layout.addStretch()
        return box

    def _build_bottom_panel(self) -> QFrame:
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._progress = QProgressBar()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        row = QHBoxLayout()
        self._status = QLabel("Ready.")
        self._run_btn = QPushButton("Start Renaming")
        self._run_btn.setMinimumHeight(36)
        self._run_btn.clicked.connect(self._start)
        row.addWidget(self._status, stretch=1)
        row.addWidget(self._run_btn)
        layout.addLayout(row)
        return frame

    # ------------------------------------------------------------------ #
    #  File management                                                     #
    # ------------------------------------------------------------------ #

    def _add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp *.gif *.webp *.tiff *.tif)",
        )
        for p in paths:
            self._add_item(p)

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            for p in sorted(Path(folder).iterdir()):
                if p.suffix.lower() in IMAGE_EXTENSIONS:
                    self._add_item(str(p))

    def _add_item(self, path: str):
        # Deduplicate
        for i in range(self.file_list.count()):
            if self.file_list.item(i).data(Qt.UserRole) == path:
                return
        item = QListWidgetItem(Path(path).name)
        item.setData(Qt.UserRole, path)
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            item.setIcon(
                QIcon(pixmap.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            )
        self.file_list.addItem(item)

    def _remove_selected(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    # ------------------------------------------------------------------ #
    #  Worker interaction                                                  #
    # ------------------------------------------------------------------ #

    def _get_naming_style(self) -> str:
        labels = ["camelCase", "snake_case", "kebab-case", "Title Case"]
        return labels[self._style_group.checkedId()]

    def _start(self):
        files = [
            self.file_list.item(i).data(Qt.UserRole)
            for i in range(self.file_list.count())
        ]
        if not files:
            self._status.setText("No files in the list.")
            return

        config = {
            "files": files,
            "naming_style": self._get_naming_style(),
            "max_words": self._max_words.value(),
            "extra_prompt": self._extra_prompt.toPlainText().strip(),
            "mode": "copy" if self._radio_copy.isChecked() else "rename",
        }

        self._run_btn.setEnabled(False)
        self._progress.setRange(0, len(files))
        self._progress.setValue(0)
        self._progress.setVisible(True)

        self._worker = RenameWorker(config)
        self._worker.progress.connect(self._progress.setValue)
        self._worker.status.connect(self._status.setText)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_finished(self, results: list):
        self._run_btn.setEnabled(True)
        self._progress.setVisible(False)

        for i, (path, new_name, error) in enumerate(results):
            item = self.file_list.item(i)
            if item is None:
                continue
            original = Path(path).name
            if error:
                item.setText(f"{original}  ✗  {error}")
            else:
                item.setText(f"{original}  →  {new_name}{Path(path).suffix}")


# ------------------------------------------------------------------ #
#  Entry point                                                         #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
