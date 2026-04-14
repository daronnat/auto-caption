from pathlib import Path

from PySide6.QtCore import QThread, Signal

from backend.base import InferenceBackend
from core.cache import get_cached, set_cached
from core.config import DOCUMENT_EXTENSIONS, IMAGE_EXTENSIONS
from core.renamer import rename_file
from core.style import STYLE_INSTRUCTIONS
from core.text_extract import extract_text
from i18n import tr


class RenameWorker(QThread):
    progress = Signal(int)
    status = Signal(str)
    file_done = Signal(int, str, str, str)  # index, path, new_name, error
    finished = Signal(list)

    def __init__(self, backend: InferenceBackend, config: dict):
        super().__init__()
        self.backend = backend
        self.config = config
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        results = []
        files = self.config["files"]
        naming_style = self.config["naming_style"]
        max_words = self.config["max_words"]
        extra_prompt = self.config.get("extra_prompt", "")
        prompt_template = self.config.get("prompt_template", "")
        doc_prompt_template = self.config.get("doc_prompt_template", "")
        mode = self.config["mode"]

        params = {
            "naming_style": naming_style,
            **self.config.get("inference_params", {}),
        }

        for i, path in enumerate(files):
            if self._cancelled:
                self.status.emit(tr("status_cancelled"))
                break

            filename = Path(path).name
            self.status.emit(tr("status_processing",
                                filename=filename, current=i + 1, total=len(files)))

            try:
                ext = Path(path).suffix.lower()
                style_instruction = STYLE_INSTRUCTIONS.get(naming_style, "")

                if ext in IMAGE_EXTENSIONS:
                    prompt = prompt_template.format(
                        max_words=max_words,
                        style_instruction=style_instruction,
                        extra=extra_prompt,
                    )
                    cached = get_cached(path, prompt, params)
                    if cached is not None:
                        new_name = cached
                        self.status.emit(tr("cache_hit", filename=filename))
                    else:
                        new_name = self.backend.generate_caption(path, prompt, params)
                        set_cached(path, prompt, params, new_name)

                elif ext in DOCUMENT_EXTENSIONS:
                    doc_text = extract_text(path)
                    prompt = doc_prompt_template.format(
                        max_words=max_words,
                        style_instruction=style_instruction,
                        extra=extra_prompt,
                        document_text=doc_text,
                    )
                    cached = get_cached(path, prompt, params)
                    if cached is not None:
                        new_name = cached
                        self.status.emit(tr("cache_hit", filename=filename))
                    else:
                        new_name = self.backend.generate_caption_from_text(prompt, params)
                        set_cached(path, prompt, params, new_name)
                else:
                    raise ValueError(f"Unsupported file type: {ext}")

                rename_file(path, new_name, mode=mode)
                results.append((path, new_name, None))
                self.file_done.emit(i, path, new_name, "")
            except Exception as e:
                results.append((path, None, str(e)))
                self.file_done.emit(i, path, "", str(e))

            self.progress.emit(i + 1)

        if not self._cancelled:
            self.status.emit(tr("status_done", count=len(results)))
        self.finished.emit(results)
