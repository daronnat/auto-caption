import time
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout
from i18n import tr


class ProgressWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._start_time = 0.0
        self._total = 0
        self._setup_ui()
        self.setVisible(False)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)

        self._bar = QProgressBar()
        self._bar.setMinimumHeight(22)
        layout.addWidget(self._bar)

        info_row = QHBoxLayout()
        self._count_label = QLabel()
        self._elapsed_label = QLabel()
        self._eta_label = QLabel()
        info_row.addWidget(self._count_label)
        info_row.addStretch()
        info_row.addWidget(self._elapsed_label)
        info_row.addWidget(self._eta_label)
        layout.addLayout(info_row)

    def start(self, total: int):
        self._total = total
        self._start_time = time.monotonic()
        self._bar.setRange(0, total)
        self._bar.setValue(0)
        self._bar.setFormat(f"0/{total}")
        self._count_label.setText(tr("progress_label", current=0, total=total))
        self._elapsed_label.setText("")
        self._eta_label.setText("")
        self.setVisible(True)

    def update(self, current: int):
        self._bar.setValue(current)
        self._bar.setFormat(f"{current}/{self._total}")
        self._count_label.setText(
            tr("progress_label", current=current, total=self._total)
        )

        elapsed = time.monotonic() - self._start_time
        self._elapsed_label.setText(tr("elapsed_label", time=self._format_time(elapsed)))

        if current > 0:
            eta = (elapsed / current) * (self._total - current)
            self._eta_label.setText(tr("eta_label", time=self._format_time(eta)))
        else:
            self._eta_label.setText("")

    def finish(self):
        elapsed = time.monotonic() - self._start_time
        self._bar.setValue(self._total)
        self._bar.setFormat(f"{self._total}/{self._total}")
        self._eta_label.setText("")
        self._elapsed_label.setText(tr("elapsed_label", time=self._format_time(elapsed)))

    def reset(self):
        self.setVisible(False)

    @staticmethod
    def _format_time(seconds: float) -> str:
        m, s = divmod(int(seconds), 60)
        if m > 0:
            return f"{m}m {s}s"
        return f"{s}s"
