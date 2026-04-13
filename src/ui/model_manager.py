from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QVBoxLayout,
)

from core.models import get_downloaded_models, delete_model, total_cache_size_mb, cache_dir_path
from i18n import tr


class ModelManagerDialog(QDialog):
    """Dialog for inspecting and deleting downloaded HuggingFace models."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("model_manager_title"))
        self.setMinimumSize(600, 400)
        self._setup_ui()
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self._info_label = QLabel()
        self._info_label.setWordWrap(True)
        self._info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self._info_label)

        self._list = QListWidget()
        self._list.setSpacing(2)
        layout.addWidget(self._list)

        btn_row = QHBoxLayout()

        self._delete_btn = QPushButton(tr("model_delete"))
        self._delete_btn.clicked.connect(self._delete_selected)
        btn_row.addWidget(self._delete_btn)

        self._refresh_btn = QPushButton(tr("model_refresh"))
        self._refresh_btn.clicked.connect(self._refresh)
        btn_row.addWidget(self._refresh_btn)

        btn_row.addStretch()

        self._close_btn = QPushButton(tr("close"))
        self._close_btn.clicked.connect(self.close)
        btn_row.addWidget(self._close_btn)

        layout.addLayout(btn_row)

    def _refresh(self):
        self._list.clear()
        models = get_downloaded_models()
        total = total_cache_size_mb()
        path = cache_dir_path()
        self._info_label.setText(tr("model_cache_info", total=f"{total:.0f}", path=path))

        if not models:
            item = QListWidgetItem(tr("no_models"))
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self._list.addItem(item)
            return

        for m in models:
            text = f"{m['repo_id']}    ({m['size_mb']:.0f} MB, {m['nb_files']} files)"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, m["repo_id"])
            self._list.addItem(item)

    def _delete_selected(self):
        items = self._list.selectedItems()
        if not items:
            return
        repo_id = items[0].data(Qt.UserRole)
        if repo_id is None:
            return
        reply = QMessageBox.question(
            self, tr("model_delete"),
            tr("model_delete_confirm", model=repo_id),
        )
        if reply == QMessageBox.Yes:
            if delete_model(repo_id):
                self._refresh()
