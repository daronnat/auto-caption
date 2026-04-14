from pathlib import Path

from PySide6.QtCore import QSize, Qt, QThread, Signal
from PySide6.QtGui import QCloseEvent, QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFileIconProvider,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from backend.base import InferenceBackend
from backend.registry import available_backends, get_backend
from core.config import (
    ALL_EXTENSIONS,
    DEFAULT_GGUF_FILE,
    DEFAULT_GGUF_REPO,
    DEFAULT_MMPROJ_FILE,
    DEFAULT_MODEL_ID,
    DOCUMENT_EXTENSIONS,
    IMAGE_EXTENSIONS,
    save_config,
)
from core.style import STYLE_NAMES
from core.worker import RenameWorker
from i18n import available_languages, current_language, set_language, tr
from ui.progress_widget import ProgressWidget
from ui.prompt_manager import PromptManager
from ui.theme import apply_theme


class GpuDetector(QThread):
    """Background thread for GPU detection (avoids blocking UI on torch import)."""
    detected = Signal(dict)

    def run(self):
        from core.gpu import detect_gpu
        self.detected.emit(detect_gpu())


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
        self._gpu_detector: GpuDetector | None = None
        self._gpu_info: dict | None = None
        self._pending_start = False
        self._tr: dict[str, tuple] = {}

        self.setWindowTitle(tr("window_title"))
        self.setMinimumSize(1000, 650)
        self._setup_ui()
        self._setup_statusbar()
        self._start_gpu_detection()

    # ── Translation helpers ──────────────────────────────────────

    def _trl(self, key: str) -> QLabel:
        """Create a QLabel registered for automatic retranslation."""
        lbl = QLabel(tr(key))
        self._tr[key] = (lbl, "setText")
        return lbl

    def _trb(self, key: str) -> QPushButton:
        """Create a QPushButton registered for automatic retranslation."""
        btn = QPushButton(tr(key))
        self._tr[key] = (btn, "setText")
        return btn

    def _trg(self, key: str) -> QGroupBox:
        """Create a QGroupBox registered for automatic retranslation."""
        box = QGroupBox(tr(key))
        self._tr[key] = (box, "setTitle")
        return box

    def _retranslate(self):
        """Update all UI text after language change — no restart needed."""
        self.setWindowTitle(tr("window_title"))
        for key, (widget, method) in self._tr.items():
            getattr(widget, method)(tr(key))
        self._theme_btn.setText(self._theme_icon())
        self._update_file_count()
        self._update_gpu_display()
        self._update_cache_display()
        self._prompt_mgr.retranslate()

    # ── UI setup ─────────────────────────────────────────────────

    def _setup_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        central.setAttribute(Qt.WA_StyledBackground, True)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(12, 12, 12, 12)

        root.addLayout(self._build_toolbar())

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._build_file_panel())
        splitter.addWidget(self._build_settings_panel())
        splitter.setSizes([480, 500])
        root.addWidget(splitter, stretch=1)

        root.addWidget(self._build_bottom_panel())

    def _build_toolbar(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        # Model info
        row.addWidget(self._trl("model_label"))
        self._model_status = QLabel(tr("model_not_loaded"))
        self._model_status.setStyleSheet("font-weight: bold;")
        row.addWidget(self._model_status)

        row.addWidget(self._vsep())

        # Backend selector
        row.addWidget(self._trl("backend_label"))
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

        self._load_model_btn = self._trb("load_model_btn")
        self._load_model_btn.setFixedWidth(130)
        self._load_model_btn.clicked.connect(self._load_model)
        row.addWidget(self._load_model_btn)

        row.addStretch()

        # Model manager
        self._manage_btn = self._trb("manage_models")
        self._manage_btn.setFixedWidth(90)
        self._manage_btn.clicked.connect(self._open_model_manager)
        row.addWidget(self._manage_btn)

        row.addWidget(self._vsep())

        # Language selector
        row.addWidget(self._trl("language_label"))
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
        box = self._trg("files_group")
        layout = QVBoxLayout(box)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_list.setIconSize(QSize(56, 56))
        self.file_list.setSpacing(2)
        layout.addWidget(self.file_list)

        # File count
        self._file_count_label = QLabel(tr("files_count", count=0))
        self._file_count_label.setStyleSheet("font-size: 11px; opacity: 0.7;")
        layout.addWidget(self._file_count_label)

        btn_row = QHBoxLayout()
        for label_key, slot in [
            ("add_files", self._add_files),
            ("add_folder", self._add_folder),
            ("remove_selected", self._remove_selected),
            ("clear_all", self._clear_all),
        ]:
            btn = self._trb(label_key)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)
        return box

    def _build_settings_panel(self) -> QWidget:
        container = QWidget()
        container.setObjectName("settingsPanel")
        container.setAttribute(Qt.WA_StyledBackground, True)
        layout = QVBoxLayout(container)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # Naming style
        style_box = self._trg("naming_style")
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
        words_row.addWidget(self._trl("max_words_label"))
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
        out_box = self._trg("output_group")
        out_layout = QVBoxLayout(out_box)
        self._radio_rename = QRadioButton(tr("rename_in_place"))
        self._radio_copy = QRadioButton(tr("copy_to_subfolder"))
        self._tr["rename_in_place"] = (self._radio_rename, "setText")
        self._tr["copy_to_subfolder"] = (self._radio_copy, "setText")
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
        frame.setObjectName("bottomPanel")
        frame.setAttribute(Qt.WA_StyledBackground, True)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._progress = ProgressWidget()
        layout.addWidget(self._progress)

        row = QHBoxLayout()
        self._status = QLabel(tr("status_ready"))

        self._run_btn = self._trb("start_button")
        self._run_btn.setObjectName("startButton")
        self._run_btn.setMinimumHeight(40)
        self._run_btn.clicked.connect(self._start)

        self._cancel_btn = self._trb("cancel_button")
        self._cancel_btn.setMinimumHeight(36)
        self._cancel_btn.setVisible(False)
        self._cancel_btn.clicked.connect(self._cancel)

        row.addWidget(self._status, stretch=1)
        row.addWidget(self._cancel_btn)
        row.addWidget(self._run_btn)
        layout.addLayout(row)
        return frame

    def _setup_statusbar(self):
        sb = self.statusBar()
        self._gpu_status = QLabel(tr("gpu_detecting"))
        self._vram_status = QLabel("")
        self._cache_status = QLabel("")

        self._clear_cache_btn = QPushButton(tr("clear_cache"))
        self._tr["clear_cache"] = (self._clear_cache_btn, "setText")
        self._clear_cache_btn.setFixedHeight(20)
        self._clear_cache_btn.setStyleSheet("font-size: 11px; padding: 1px 8px;")
        self._clear_cache_btn.clicked.connect(self._clear_cache)

        sb.addPermanentWidget(self._gpu_status)
        sb.addPermanentWidget(self._vram_status)
        sb.addPermanentWidget(self._cache_status)
        sb.addPermanentWidget(self._clear_cache_btn)
        self._update_cache_display()

    # ── GPU detection ────────────────────────────────────────────

    def _start_gpu_detection(self):
        self._gpu_detector = GpuDetector()
        self._gpu_detector.detected.connect(self._on_gpu_detected)
        self._gpu_detector.start()

    def _on_gpu_detected(self, info: dict):
        self._gpu_info = info
        self._update_gpu_display()

    def _update_gpu_display(self):
        if self._gpu_info is None:
            self._gpu_status.setText(f"GPU: {tr('gpu_detecting')}")
            return
        if self._gpu_info["backend_hint"] == "cpu":
            self._gpu_status.setText(f"GPU: {tr('gpu_cpu_only')}")
        else:
            self._gpu_status.setText(f"GPU: {self._gpu_info['device_name']}")
        self._update_vram_display()

    def _update_vram_display(self):
        from core.gpu import get_vram_usage
        used, total = get_vram_usage()
        if total > 0:
            self._vram_status.setText(
                tr("vram_label", used=f"{used / 1024:.1f}", total=f"{total / 1024:.1f}")
            )
        elif self._gpu_info and self._gpu_info["device"] == "mps":
            total_mb = self._gpu_info.get("vram_total_mb", 0)
            if total_mb > 0:
                self._vram_status.setText(f"RAM: {total_mb / 1024:.0f} GB (unified)")
            else:
                self._vram_status.setText("")
        else:
            self._vram_status.setText("")

    # ── Cache ────────────────────────────────────────────────────

    def _update_cache_display(self):
        from core.cache import cache_count, cache_size_str
        count = cache_count()
        size = cache_size_str()
        if count > 0:
            self._cache_status.setText(tr("cache_label", size=f"{count} items, {size}"))
        else:
            self._cache_status.setText(tr("cache_label", size="empty"))

    def _clear_cache(self):
        from core.cache import clear_cache
        reply = QMessageBox.question(
            self, tr("clear_cache"), tr("clear_cache_confirm"),
        )
        if reply == QMessageBox.Yes:
            cleared = clear_cache()
            self._status.setText(f"Cache cleared ({cleared} entries)")
            self._update_cache_display()

    # ── File management ──────────────────────────────────────────

    def _add_files(self):
        img_filter = "Images (" + " ".join(f"*{e}" for e in sorted(IMAGE_EXTENSIONS)) + ")"
        doc_filter = "Documents (" + " ".join(f"*{e}" for e in sorted(DOCUMENT_EXTENSIONS)) + ")"
        all_filter = "All supported (" + " ".join(f"*{e}" for e in sorted(ALL_EXTENSIONS)) + ")"
        paths, _ = QFileDialog.getOpenFileNames(
            self, tr("add_files"), "",
            f"{all_filter};;{img_filter};;{doc_filter}",
        )
        for p in paths:
            self._add_item(p)
        self._update_file_count()

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, tr("add_folder"))
        if folder:
            for p in sorted(Path(folder).iterdir()):
                if p.suffix.lower() in ALL_EXTENSIONS:
                    self._add_item(str(p))
            self._update_file_count()

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
        self._update_file_count()

    def _clear_all(self):
        self.file_list.clear()
        self._update_file_count()

    def _update_file_count(self):
        count = self.file_list.count()
        self._file_count_label.setText(tr("files_count", count=count))

    # ── Model management ─────────────────────────────────────────

    def _load_model(self):
        # VRAM check before loading
        if self._gpu_info:
            from core.gpu import check_vram_sufficient
            ok, warning = check_vram_sufficient(DEFAULT_MODEL_ID, self._gpu_info)
            if not ok:
                reply = QMessageBox.warning(
                    self, tr("vram_warning_title"),
                    tr("vram_warning_msg", details=warning),
                    QMessageBox.Ok | QMessageBox.Cancel,
                )
                if reply == QMessageBox.Cancel:
                    return
            elif warning:
                self._status.setText(warning)

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
            info = self._backend.device_info()
            device = info.get("device", "")
            dtype = info.get("dtype", "")
            self._model_status.setText(f"{name} ({backend}, {device}, {dtype})")
            self._status.setText(tr("status_ready"))
            self._config["backend"] = backend
            save_config(self._config)
            self._update_vram_display()
            if self._pending_start:
                self._pending_start = False
                self._run_after_ready()

    def _open_model_manager(self):
        from ui.model_manager import ModelManagerDialog
        dlg = ModelManagerDialog(self)
        dlg.exec()

    # ── Worker interaction ───────────────────────────────────────

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
        self._update_vram_display()
        self._update_cache_display()

    # ── Theme / Language ─────────────────────────────────────────

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
        self._retranslate()

    # ── Helpers ──────────────────────────────────────────────────

    def closeEvent(self, event: QCloseEvent):
        """Ensure background threads are stopped before closing."""
        for thread in (self._gpu_detector, self._model_loader, self._worker):
            if thread is not None and thread.isRunning():
                thread.quit()
                thread.wait(2000)
        super().closeEvent(event)

    @staticmethod
    def _vsep() -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)
        sep.setFixedWidth(2)
        return sep
