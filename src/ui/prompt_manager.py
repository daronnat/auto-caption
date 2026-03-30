from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QGroupBox, QHBoxLayout, QInputDialog,
    QLabel, QMessageBox, QPushButton, QSpinBox, QTabWidget, QTextEdit,
    QVBoxLayout, QWidget,
)
from core.config import (
    DEFAULT_PROMPT_IMAGE, DEFAULT_PROMPT_DOCUMENT, load_prompts, save_prompts,
)
from i18n import tr


class PromptManager(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(tr("prompt_presets"), parent)
        self._prompts = load_prompts()
        self._setup_ui()
        self._load_preset(0)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Preset selector
        row = QHBoxLayout()
        self._combo = QComboBox()
        self._combo.currentIndexChanged.connect(self._load_preset)
        row.addWidget(self._combo, stretch=1)

        self._save_btn = QPushButton(tr("save_preset"))
        self._save_btn.clicked.connect(self._save_preset)
        row.addWidget(self._save_btn)

        self._del_btn = QPushButton(tr("delete_preset"))
        self._del_btn.clicked.connect(self._delete_preset)
        row.addWidget(self._del_btn)
        layout.addLayout(row)

        # Prompt tabs for image vs document
        tabs = QTabWidget()

        # Image prompt tab
        img_tab = QWidget()
        img_layout = QVBoxLayout(img_tab)
        img_layout.addWidget(QLabel("Image prompt template:"))
        self._img_prompt_edit = QTextEdit()
        self._img_prompt_edit.setFixedHeight(70)
        self._img_prompt_edit.setPlaceholderText(
            "Use {max_words}, {style_instruction}, {extra} as placeholders"
        )
        img_layout.addWidget(self._img_prompt_edit)
        tabs.addTab(img_tab, "Image")

        # Document prompt tab
        doc_tab = QWidget()
        doc_layout = QVBoxLayout(doc_tab)
        doc_layout.addWidget(QLabel("Document prompt template:"))
        self._doc_prompt_edit = QTextEdit()
        self._doc_prompt_edit.setFixedHeight(70)
        self._doc_prompt_edit.setPlaceholderText(
            "Use {max_words}, {style_instruction}, {extra}, {document_text} as placeholders"
        )
        doc_layout.addWidget(self._doc_prompt_edit)
        tabs.addTab(doc_tab, "Document")

        layout.addWidget(tabs)

        # Extra instructions
        layout.addWidget(QLabel(tr("extra_prompt_label")))
        self._extra_edit = QTextEdit()
        self._extra_edit.setFixedHeight(40)
        self._extra_edit.setPlaceholderText(tr("prompt_placeholder"))
        layout.addWidget(self._extra_edit)

        # Inference params row
        params_box = QGroupBox(tr("inference_group"))
        params_layout = QHBoxLayout(params_box)

        params_layout.addWidget(QLabel(tr("temperature_label")))
        self._temperature = QDoubleSpinBox()
        self._temperature.setRange(0.0, 2.0)
        self._temperature.setSingleStep(0.1)
        self._temperature.setFixedWidth(70)
        params_layout.addWidget(self._temperature)

        params_layout.addWidget(QLabel(tr("top_p_label")))
        self._top_p = QDoubleSpinBox()
        self._top_p.setRange(0.0, 1.0)
        self._top_p.setSingleStep(0.05)
        self._top_p.setFixedWidth(70)
        params_layout.addWidget(self._top_p)

        params_layout.addWidget(QLabel(tr("max_tokens_label")))
        self._max_tokens = QSpinBox()
        self._max_tokens.setRange(10, 500)
        self._max_tokens.setFixedWidth(70)
        params_layout.addWidget(self._max_tokens)

        params_layout.addStretch()
        layout.addWidget(params_box)

        self._refresh_combo()

    def _refresh_combo(self):
        self._combo.blockSignals(True)
        self._combo.clear()
        for p in self._prompts:
            self._combo.addItem(p["name"])
        self._combo.blockSignals(False)

    def _load_preset(self, index: int):
        if index < 0 or index >= len(self._prompts):
            return
        p = self._prompts[index]
        self._img_prompt_edit.setPlainText(
            p.get("prompt", p.get("img_prompt", DEFAULT_PROMPT_IMAGE["prompt"]))
        )
        self._doc_prompt_edit.setPlainText(
            p.get("doc_prompt", DEFAULT_PROMPT_DOCUMENT["prompt"])
        )
        self._temperature.setValue(p.get("temperature", 0.0))
        self._top_p.setValue(p.get("top_p", 1.0))
        self._max_tokens.setValue(p.get("max_new_tokens", 50))

    def _save_preset(self):
        name, ok = QInputDialog.getText(self, tr("save_preset"), tr("new_preset_name"))
        if not ok or not name.strip():
            return
        preset = self._current_values()
        preset["name"] = name.strip()
        for i, p in enumerate(self._prompts):
            if p["name"] == preset["name"]:
                self._prompts[i] = preset
                break
        else:
            self._prompts.append(preset)
        save_prompts(self._prompts)
        self._refresh_combo()
        self._combo.setCurrentText(preset["name"])

    def _delete_preset(self):
        idx = self._combo.currentIndex()
        if idx < 0 or len(self._prompts) <= 1:
            return
        name = self._prompts[idx]["name"]
        reply = QMessageBox.question(
            self, tr("delete_preset"), f"Delete preset \"{name}\"?",
        )
        if reply == QMessageBox.Yes:
            self._prompts.pop(idx)
            save_prompts(self._prompts)
            self._refresh_combo()
            self._load_preset(0)
            self._combo.setCurrentIndex(0)

    def _current_values(self) -> dict:
        return {
            "name": self._combo.currentText(),
            "img_prompt": self._img_prompt_edit.toPlainText(),
            "doc_prompt": self._doc_prompt_edit.toPlainText(),
            "temperature": self._temperature.value(),
            "top_p": self._top_p.value(),
            "max_new_tokens": self._max_tokens.value(),
        }

    def get_prompt_texts(self) -> tuple[str, str]:
        return (
            self._img_prompt_edit.toPlainText(),
            self._doc_prompt_edit.toPlainText(),
        )

    def get_extra_prompt(self) -> str:
        return self._extra_edit.toPlainText().strip()

    def get_params(self) -> dict:
        return {
            "temperature": self._temperature.value(),
            "top_p": self._top_p.value(),
            "max_new_tokens": self._max_tokens.value(),
        }
