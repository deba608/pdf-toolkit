"""Reusable dashed drag-and-drop target."""
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

from src.ui.icons import get_pixmap
from src.ui.theme import TEXT_1, TEXT_2, TEXT_3
from src.ui.widgets.tool_session import IMAGE_SUFFIXES


class DropZone(QFrame):
    filesDropped = Signal(list)
    browseRequested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.spec = None

        v = QVBoxLayout(self)
        v.setAlignment(Qt.AlignCenter)
        v.setSpacing(8)
        v.setContentsMargins(24, 28, 24, 28)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(get_pixmap("pdf", TEXT_3, 40))
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel("Drop files here")
        self.title_label.setObjectName("DropZoneTitle")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.subtitle_label = QLabel("or browse from your computer")
        self.subtitle_label.setObjectName("DropZoneSubtitle")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)

        self.browse_button = QPushButton("  Browse files…")
        self.browse_button.setObjectName("Secondary")
        self.browse_button.clicked.connect(lambda: self.browseRequested.emit())

        v.addWidget(self.icon_label)
        v.addWidget(self.title_label)
        v.addWidget(self.subtitle_label)
        v.addWidget(self.browse_button, 0, Qt.AlignCenter)

    def set_spec(self, spec):
        self.spec = spec
        if spec is None:
            self.title_label.setText("Drop PDFs here to get started")
            self.subtitle_label.setText("or choose files from your computer")
            return
        label = "images" if spec.input_mode == "multi_image" else "PDFs"
        verb = "Merge" if spec.key == "merge" else spec.label
        self.title_label.setText(f"Drop {label} here for {verb}")
        self.subtitle_label.setText(f"{spec.description}. Drag files in or browse.")

    def accepts_suffix(self, suffix: str) -> bool:
        suffix = suffix.lower()
        if self.spec is None:
            return suffix == ".pdf"
        if self.spec.input_mode == "multi_image":
            return suffix in IMAGE_SUFFIXES
        return suffix == ".pdf"

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dropActive", True)
            self._repolish()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.setProperty("dropActive", False)
        self._repolish()

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dropActive", False)
        self._repolish()
        paths = [Path(u.toLocalFile()) for u in event.mimeData().urls() if u.toLocalFile()]
        if paths:
            self.filesDropped.emit(paths)

    def _repolish(self):
        self.style().unpolish(self)
        self.style().polish(self)
