"""Ordered file list for the active tool session."""
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QVBoxLayout, QWidget
)

from src.core.models import PdfFile
from src.ui.icons import get_icon
from src.ui.theme import PRIMARY


class FileQueue(QWidget):
    activeChanged = Signal(object)
    removeRequested = Signal(int)
    moveRequested = Signal(int, int)
    clearRequested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("FileQueue")
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(8)

        header = QHBoxLayout()
        self.count_label = QLabel("0 files")
        self.count_label.setObjectName("SectionLabel")
        header.addWidget(self.count_label)
        header.addStretch()
        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("Ghost")
        self.clear_button.clicked.connect(lambda: self.clearRequested.emit())
        header.addWidget(self.clear_button)
        v.addLayout(header)

        self.list = QListWidget()
        self.list.setObjectName("FileQueueList")
        self.list.setFrameShape(QFrame.NoFrame)
        self.list.setIconSize(QSize(20, 20))
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.currentItemChanged.connect(
            lambda current, _: self.activeChanged.emit(
                current.data(Qt.UserRole) if current else None
            )
        )
        v.addWidget(self.list, 1)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        self.up_button = QPushButton("▲ Up")
        self.up_button.setObjectName("Secondary")
        self.down_button = QPushButton("▼ Down")
        self.down_button.setObjectName("Secondary")
        self.remove_button = QPushButton("✕ Remove")
        self.remove_button.setObjectName("Secondary")
        buttons.addWidget(self.up_button)
        buttons.addWidget(self.down_button)
        buttons.addWidget(self.remove_button)
        buttons.addStretch()
        v.addLayout(buttons)

        self.up_button.clicked.connect(lambda: self._emit_move(-1))
        self.down_button.clicked.connect(lambda: self._emit_move(1))
        self.remove_button.clicked.connect(
            lambda: self.removeRequested.emit(self.list.currentRow())
        )
        self.set_can_reorder(False)

    def set_can_reorder(self, enabled: bool):
        self.up_button.setVisible(enabled)
        self.down_button.setVisible(enabled)
        self.up_button.setEnabled(False)
        self.down_button.setEnabled(False)

    def set_files(self, files: list[PdfFile], active: PdfFile | None = None):
        self.list.blockSignals(True)
        self.list.clear()
        for pdf in files:
            item = QListWidgetItem(f"  {pdf.name}   ({pdf.page_count}p • {pdf.size_mb:.2f} MB)")
            item.setIcon(get_icon("pdf", PRIMARY, 18))
            item.setData(Qt.UserRole, pdf)
            item.setSizeHint(QSize(0, 36))
            self.list.addItem(item)
        self.list.blockSignals(False)
        self.count_label.setText(f"{len(files)} file{'s' if len(files) != 1 else ''}")
        self.remove_button.setEnabled(len(files) > 0)
        self.clear_button.setEnabled(len(files) > 0)
        if active is not None:
            self._select(active)

    def _select(self, pdf: PdfFile):
        for i in range(self.list.count()):
            if self.list.item(i).data(Qt.UserRole) is pdf:
                self.list.setCurrentRow(i)
                return

    def _emit_move(self, delta: int):
        row = self.list.currentRow()
        if row >= 0:
            self.moveRequested.emit(row, delta)
