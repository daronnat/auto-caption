from pathlib import Path
from PySide6.QtCore import QThread, Signal
from inference import ImageRenamer
from renamer import rename_file


class RenameWorker(QThread):
    progress = Signal(int)        # current file index (1-based)
    status = Signal(str)          # status message
    finished = Signal(list)       # list of (original_path, new_name_or_None, error_or_None)

    def __init__(self, config: dict):
        super().__init__()
        self.config = config

    def run(self):
        renamer = ImageRenamer()

        self.status.emit("Loading model…")
        try:
            renamer.load_model()
        except Exception as e:
            self.status.emit(f"Failed to load model: {e}")
            self.finished.emit([])
            return

        results = []
        files = self.config["files"]

        for i, path in enumerate(files):
            self.status.emit(f"Processing {Path(path).name}  ({i + 1}/{len(files)})")
            try:
                new_name = renamer.generate_filename(
                    path,
                    naming_style=self.config["naming_style"],
                    max_words=self.config["max_words"],
                    extra_prompt=self.config["extra_prompt"],
                )
                rename_file(path, new_name, mode=self.config["mode"])
                results.append((path, new_name, None))
            except Exception as e:
                results.append((path, None, str(e)))

            self.progress.emit(i + 1)

        self.status.emit(f"Done — {len(files)} file(s) processed.")
        self.finished.emit(results)
