from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QHBoxLayout, QMenu
)
from PySide6.QtCore import Qt, Signal, QMimeData, QPoint
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QIcon

from src.core.models import PdfFile


class FileListWidget(QWidget):
    file_selected = Signal(PdfFile)
    files_reordered = Signal(list)

    def __init__(self):
        super().__init__()
        self._files: list[PdfFile] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # List
        self.list = QListWidget()
        self.list.setObjectName("FileList")
        self.list.setDragDropMode(QListWidget.InternalMove)
        self.list.setDefaultDropAction(Qt.MoveAction)
        self.list.setSelectionMode(QListWidget.SingleSelection)
        from PySide6.QtWidgets import QFrame
        self.list.setFrameShape(QFrame.NoFrame)
        self.list.currentItemChanged.connect(self._on_selection_changed)
        self.list.model().rowsMoved.connect(self._on_rows_moved)
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list)

    def add_file(self, pdf: PdfFile):
        self._files.append(pdf)
        item = QListWidgetItem(f"{pdf.name} ({pdf.page_count} pages, {pdf.size_mb:.1f} MB)")
        item.setData(Qt.UserRole, pdf)
        item.setToolTip(str(pdf.path))
        self.list.addItem(item)

    def update_file(self, pdf: PdfFile):
        for i in range(self.list.count()):
            item = self.list.item(i)
            if item.data(Qt.UserRole).path == pdf.path:
                item.setText(f"{pdf.name} ({pdf.page_count} pages, {pdf.size_mb:.1f} MB)")
                item.setData(Qt.UserRole, pdf)
                break

    def _on_selection_changed(self, current, previous):
        if current:
            pdf = current.data(Qt.UserRole)
            self.file_selected.emit(pdf)

    def _on_rows_moved(self, parent, start, end, dest, dest_row):
        # Rebuild _files in new order
        new_files = []
        for i in range(self.list.count()):
            new_files.append(self.list.item(i).data(Qt.UserRole))
        self._files = new_files
        self.files_reordered.emit(new_files)

    def _show_context_menu(self, pos: QPoint):
        item = self.list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        remove = menu.addAction("Remove")
        action = menu.exec(self.list.mapToGlobal(pos))
        if action == remove:
            self._remove_item(item)

    def _remove_item(self, item: QListWidgetItem):
        pdf = item.data(Qt.UserRole)
        self._files = [f for f in self._files if f.path != pdf.path]
        self.list.takeItem(self.list.row(item))
        self.files_reordered.emit(self._files)

    def _clear_all(self):
        self._files.clear()
        self.list.clear()
        self.files_reordered.emit([])