from pathlib import Path

from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame, QListWidget, QListWidgetItem, QMenu, QVBoxLayout, QWidget
)

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

        self.list = QListWidget()
        self.list.setObjectName("FileList")
        self.list.setDragDropMode(QListWidget.InternalMove)
        self.list.setDefaultDropAction(Qt.MoveAction)
        self.list.setSelectionMode(QListWidget.SingleSelection)
        self.list.setFrameShape(QFrame.NoFrame)
        self.list.currentItemChanged.connect(self._on_selection_changed)
        self.list.model().rowsMoved.connect(self._on_rows_moved)
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list)

        # README promises Delete = remove selected file.
        self._delete_shortcut = QShortcut(QKeySequence.Delete, self.list)
        self._delete_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self._delete_shortcut.activated.connect(self.remove_current)

    # ---------- data ----------
    @property
    def files(self) -> list[PdfFile]:
        return list(self._files)

    def add_file(self, pdf: PdfFile):
        self._files.append(pdf)
        item = QListWidgetItem(self._label(pdf))
        item.setData(Qt.UserRole, pdf)
        item.setToolTip(str(pdf.path))
        self.list.addItem(item)

    def update_file(self, pdf: PdfFile):
        for i in range(self.list.count()):
            item = self.list.item(i)
            existing = item.data(Qt.UserRole)
            if existing.path == pdf.path:
                item.setText(self._label(pdf))
                item.setData(Qt.UserRole, pdf)
                self._files[i] = pdf
                break

    def has_path(self, path: Path) -> bool:
        resolved = Path(path).resolve()
        return any(f.path.resolve() == resolved for f in self._files)

    def select_path(self, path: Path) -> bool:
        resolved = Path(path).resolve()
        for i in range(self.list.count()):
            if self.list.item(i).data(Qt.UserRole).path.resolve() == resolved:
                self.list.setCurrentRow(i)
                return True
        return False

    def clear(self):
        self._files.clear()
        self.list.clear()
        self.files_reordered.emit([])

    def remove_current(self):
        item = self.list.currentItem()
        if item:
            self._remove_item(item)

    # ---------- internals ----------
    @staticmethod
    def _label(pdf: PdfFile) -> str:
        return f"{pdf.name} ({pdf.page_count} pages, {pdf.size_mb:.1f} MB)"

    def _on_selection_changed(self, current, previous):
        if current:
            self.file_selected.emit(current.data(Qt.UserRole))

    def _on_rows_moved(self, parent, start, end, dest, dest_row):
        self._files = [
            self.list.item(i).data(Qt.UserRole) for i in range(self.list.count())
        ]
        self.files_reordered.emit(list(self._files))

    def _show_context_menu(self, pos: QPoint):
        item = self.list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        remove = menu.addAction("Remove")
        if menu.exec(self.list.mapToGlobal(pos)) == remove:
            self._remove_item(item)

    def _remove_item(self, item: QListWidgetItem):
        pdf = item.data(Qt.UserRole)
        self._files = [f for f in self._files if f.path.resolve() != pdf.path.resolve()]
        self.list.takeItem(self.list.row(item))
        self.files_reordered.emit(list(self._files))
