from pathlib import Path

from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QButtonGroup, QComboBox, QFileDialog,
    QFileIconProvider, QFrame, QGroupBox, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QMainWindow, QPushButton, QRadioButton, QSpinBox,
    QSplitter, QVBoxLayout, QWidget,
)

from backend.base import InferenceBackend
from backend.registry import available_backends, get_backend
from core.config import (
    DEFAULT_MODEL_ID, DEFAULT_GGUF_REPO, DEFAULT_GGUF_FILE, DEFAULT_MMPROJ_FILE,
    IMAGE_EXTENSIONS, DOCUMENT_EXTENSIONS, ALL_EXTENSIONS, load_config, save_config,
)
from core.worker import RenameWorker
from core.style import STYLE_NAMES
from i18n import tr, set_language, current_language, available_languages
from ui.theme import apply_theme
from ui.prompt_manager import PromptManager
from ui.progress_widget import ProgressWidget


class ModelLoader(QThread):
    done = Signal(str)  # error or empty

    def __init__(self, backend: InferenceBackend, model_id: str, **kwargs):
        super().__init__()
        self._backend = backend
        self._model_id = model_id
        self._kwargs = kwargs

    def run(self):
        try:
            self._backend.load_model(self._model_id, **self._kwargs)
            self.done.emit("")
        except Exception as e:
            self.done.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self, config: dict):
        super().__init__()
        self._config = config
        self._backend: InferenceBackend | None = None
        self._worker: RenameWorker | None = None
        self._model_loader: ModelLoader | None = None
        self._pending_start = False

        self.setWindowTitle(tr("window_title"))
        self.setMinimumSize(1000, 650)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(8)
        root.setContentsMargins(10, 10, 10, 10)

        # Top toolbar
        root.addLayout(self._build_toolbar())

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._build_file_panel())
        splitter.addWidget(self._build_settings_panel())
        splitter.setSizes([480, 500])
        root.addWidget(splitter, stretch=1)

        # Bottom
        root.addWidget(self._build_bottom_panel())

    def _build_toolbar(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        # Model info
        row.addWidget(QLabel(tr("model_label")))
        self._model_status = QLabel(tr("model_not_loaded"))
        self._model_status.setStyleSheet("font-weight: bold;")
        row.addWidget(self._model_status)

        row.addWidget(self._vsep())

        # Backend selector
        row.addWidget(QLabel(tr("backend_label")))
        self._backend_combo = QComboBox()
        backends = available_backends()
        if not backends:
            backends = ["transformers"]
        self._backend_combo.addItems(backends)
        current = self._config.get("backend", "transformers")
        if current in backends:
            self._backend_combo.setCurrentText(current)
        self._backend_combo.setFixedWidth(130)
        row.addWidget(self._backend_combo)

        self._load_model_btn = QPushButton(tr("status_loading_model").replace("...", ""))
        self._load_model_btn.setFixedWidth(120)
        self._load_model_btn.clicked.connect(self._load_model)
        row.addWidget(self._load_model_btn)

        row.addStretch()

        # Language selector
        row.addWidget(QLabel(tr("language_label")))
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(available_languages())
        self._lang_combo.setCurrentText(current_language())
        self._lang_combo.setFixedWidth(60)
        self._lang_combo.currentTextChanged.connect(self._change_language)
        row.addWidget(self._lang_combo)

        # Theme toggle
        self._theme_btn = QPushButton(self._theme_icon())
        self._theme_btn.setFixedSize(32, 32)
        self._theme_btn.setToolTip(tr("theme_toggle"))
        self._theme_btn.clicked.connect(self._toggle_theme)
        row.addWidget(self._theme_btn)

        return row

    def _build_file_panel(self) -> QGroupBox:
        box = QGroupBox(tr("files_group"))
        layout = QVBoxLayout(box)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_list.setIconSize(QSize(56, 56))
        self.file_list.setSpacing(2)
        layout.addWidget(self.file_list)

        btn_row = QHBoxLayout()
        for label_key, slot in [
            ("add_files", self._add_files),
            ("add_folder", self._add_folder),
            ("remove_selected", self._remove_selected),
            ("clear_all", self.file_list.clear),
        ]:
            btn = QPushButton(tr(label_key))
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)
        return box

    def _build_settings_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # Naming style
        style_box = QGroupBox(tr("naming_style"))
        style_row = QHBoxLayout(style_box)
        self._style_group = QButtonGroup(self)
        self._style_group.setExclusive(True)
        default_style = self._config.get("naming_style", "snake_case")
        for idx, label in enumerate(STYLE_NAMES):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(label == default_style)
            self._style_group.addButton(btn, idx)
            style_row.addWidget(btn)
        layout.addWidget(style_box)

        # Max words
        words_row = QHBoxLayout()
        words_row.addWidget(QLabel(tr("max_words_label")))
        self._max_words = QSpinBox()
        self._max_words.setRange(1, 20)
        self._max_words.setValue(self._config.get("max_words", 5))
        self._max_words.setFixedWidth(60)
        words_row.addWidget(self._max_words)
        words_row.addStretch()
        layout.addLayout(words_row)

        # Prompt manager
        self._prompt_mgr = PromptManager()
        layout.addWidget(self._prompt_mgr)

        # Output mode
        out_box = QGroupBox(tr("output_group"))
        out_layout = QVBoxLayout(out_box)
        self._radio_rename = QRadioButton(tr("rename_in_place"))
        self._radio_copy = QRadioButton(tr("copy_to_subfolder"))
        default_mode = self._config.get("output_mode", "copy")
        self._radio_copy.setChecked(default_mode == "copy")
        self._radio_rename.setChecked(default_mode == "rename")
        out_layout.addWidget(self._radio_rename)
        out_layout.addWidget(self._radio_copy)
        layout.addWidget(out_box)

        layout.addStretch()
        return container

    def _build_bottom_panel(self) -> QFrame:
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._progress = ProgressWidget()
        layout.addWidget(self._progress)

        row = QHBoxLayout()
        self._status = QLabel(tr("status_ready"))
        self._run_btn = QPushButton(tr("start_button"))
        self._run_btn.setMinimumHeight(36)
        self._run_btn.clicked.connect(self._start)

        self._cancel_btn = QPushButton(tr("cancel_button"))
        self._cancel_btn.setMinimumHeight(36)
        self._cancel_btn.setVisible(False)
        self._cancel_btn.clicked.connect(self._cancel)

        row.addWidget(self._status, stretch=1)
        row.addWidget(self._cancel_btn)
        row.addWidget(self._run_btn)
        layout.addLayout(row)
        return frame

    # ── File management ───────────────────────────────────────────

    def _add_files(self):
        img_filter = "Images (" + " ".join(f"*{e}" for e in sorted(IMAGE_EXTENSIONS)) + ")"
        doc_filter = "Documents (" + " ".join(f"*{e}" for e in sorted(DOCUMENT_EXTENSIONS)) + ")"
        all_filter = "All supported (" + " ".join(f"*{e}" for e in sorted(ALL_EXTENSIONS)) + ")"
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Files", "",
            f"{all_filter};;{img_filter};;{doc_filter}",
        )
        for p in paths:
            self._add_item(p)

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            for p in sorted(Path(folder).iterdir()):
                if p.suffix.lower() in ALL_EXTENSIONS:
                    self._add_item(str(p))

    def _add_item(self, path: str):
        for i in range(self.file_list.count()):
            if self.file_list.item(i).data(Qt.UserRole) == path:
                return
        p = Path(path)
        item = QListWidgetItem(p.name)
        item.setData(Qt.UserRole, path)
        if p.suffix.lower() in IMAGE_EXTENSIONS:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                item.setIcon(
                    QIcon(pixmap.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                )
        else:
            from PySide6.QtCore import QFileInfo
            provider = QFileIconProvider()
            icon = provider.icon(QFileInfo(path))
            item.setIcon(icon)
            item.setToolTip(f"Document: {p.suffix}")
        self.file_list.addItem(item)

    def _remove_selected(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    # ── Model management ──────────────────────────────────────────

    def _load_model(self):
        backend_name = self._backend_combo.currentText()
        self._backend = get_backend(backend_name)

        self._load_model_btn.setEnabled(False)
        self._model_status.setText(tr("status_loading_model"))
        self._status.setText(tr("status_loading_model"))

        kwargs = {}
        if backend_name == "llama.cpp":
            kwargs = {
                "gguf_repo": DEFAULT_GGUF_REPO,
                "gguf_file": DEFAULT_GGUF_FILE,
                "mmproj_file": DEFAULT_MMPROJ_FILE,
            }

        self._model_loader = ModelLoader(
            self._backend, DEFAULT_MODEL_ID, **kwargs
        )
        self._model_loader.done.connect(self._on_model_loaded)
        self._model_loader.start()

    def _on_model_loaded(self, error: str):
        self._load_model_btn.setEnabled(True)
        self._run_btn.setEnabled(True)
        if error:
            self._model_status.setText(tr("status_model_fail", error=error[:60]))
            self._status.setText(tr("status_model_fail", error=error))
            self._pending_start = False
        else:
            name = self._backend.model_name()
            backend = self._backend.backend_name()
            self._model_status.setText(f"{name} ({backend})")
            self._status.setText(tr("status_ready"))
            self._config["backend"] = backend
            save_config(self._config)
            if self._pending_start:
                self._pending_start = False
                self._run_after_ready()

    # ── Worker interaction ────────────────────────────────────────

    def _get_naming_style(self) -> str:
        return STYLE_NAMES[self._style_group.checkedId()]

    def _start(self):
        if self._backend is None or not self._backend.is_loaded():
            self._pending_start = True
            self._run_btn.setEnabled(False)
            self._load_model()
            return

        self._run_after_ready()

    def _run_after_ready(self):
        files = [
            self.file_list.item(i).data(Qt.UserRole)
            for i in range(self.file_list.count())
        ]
        if not files:
            self._status.setText(tr("status_no_files"))
            return

        img_template, doc_template = self._prompt_mgr.get_prompt_texts()
        config = {
            "files": files,
            "naming_style": self._get_naming_style(),
            "max_words": self._max_words.value(),
            "extra_prompt": self._prompt_mgr.get_extra_prompt(),
            "prompt_template": img_template,
            "doc_prompt_template": doc_template,
            "mode": "copy" if self._radio_copy.isChecked() else "rename",
            "inference_params": self._prompt_mgr.get_params(),
        }

        self._run_btn.setVisible(False)
        self._cancel_btn.setVisible(True)
        self._progress.start(len(files))

        self._worker = RenameWorker(self._backend, config)
        self._worker.progress.connect(self._progress.update)
        self._worker.status.connect(self._status.setText)
        self._worker.file_done.connect(self._on_file_done)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _cancel(self):
        if self._worker:
            self._worker.cancel()
            self._status.setText(tr("status_cancelled"))

    def _on_file_done(self, index: int, path: str, new_name: str, error: str):
        item = self.file_list.item(index)
        if item is None:
            return
        original = Path(path).name
        if error:
            item.setText(f"{original}  \u2717  {error}")
        else:
            item.setText(f"{original}  \u2192  {new_name}{Path(path).suffix}")

    def _on_finished(self, results: list):
        self._run_btn.setVisible(True)
        self._cancel_btn.setVisible(False)
        self._progress.finish()
        count = len(results)
        self._status.setText(tr("status_done", count=count))

    # ── Theme / Language ──────────────────────────────────────────

    def _toggle_theme(self):
        new_theme = "light" if self._config.get("theme") == "dark" else "dark"
        self._config["theme"] = new_theme
        save_config(self._config)
        apply_theme(QApplication.instance(), new_theme)
        self._theme_btn.setText(self._theme_icon())

    def _theme_icon(self) -> str:
        return "Light" if self._config.get("theme") == "dark" else "Dark"

    def _change_language(self, lang: str):
        set_language(lang)
        self._config["language"] = lang
        save_config(self._config)
        self._status.setText(f"Language changed to '{lang}'. Restart for full effect.")

    @staticmethod
    def _vsep() -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)
        sep.setFixedWidth(2)
        return sep
