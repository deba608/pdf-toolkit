import os
import subprocess
from pathlib import Path

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMenu, QPushButton, QStackedWidget, QVBoxLayout, QWidget
)

from src.core.models import PdfFile
from src.ui.theme import (ACCENT, BG_1, BG_2, BORDER, BORDER_STRONG, TEXT,
                          TEXT_FAINT, TEXT_MUTED)


class FileListWidget(QWidget):
    file_selected = Signal(PdfFile)
    files_reordered = Signal(list)
    open_requested = Signal()

    def __init__(self):
        super().__init__()
        self._files: list[PdfFile] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Search / filter bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍  Filter loaded PDFs…")
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self._filter_items)
        layout.addWidget(self.search_bar)

        # Stack to toggle between empty drop zone and actual file list
        self.stack = QStackedWidget()

        # 0: File list
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
        self.stack.addWidget(self.list)

        # 1: Empty state / drop zone
        self.empty_zone = self._build_empty_zone()
        self.stack.addWidget(self.empty_zone)

        layout.addWidget(self.stack, 1)
        self._update_empty_state()

    def _build_empty_zone(self) -> QWidget:
        w = QFrame()
        w.setStyleSheet(
            f"QFrame{{"
            f"  background:{BG_2};"
            f"  border:2px dashed {BORDER_STRONG};"
            f"  border-radius:8px;"
            f"}}"
            f"QFrame:hover{{"
            f"  border-color:{ACCENT};"
            f"}}"
        )
        v = QVBoxLayout(w)
        v.setAlignment(Qt.AlignCenter)
        v.setSpacing(10)
        v.setContentsMargins(20, 24, 20, 24)

        icon = QLabel("📄")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(f"font-size:36px;background:transparent;border:none;")

        title = QLabel("No PDFs Loaded")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size:14px;font-weight:600;color:{TEXT};background:transparent;border:none;")

        desc = QLabel("Drag & drop PDF files here\nor click the button below to browse")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size:12px;color:{TEXT_MUTED};background:transparent;border:none;")

        browse_btn = QPushButton("+ Browse PDFs")
        browse_btn.setObjectName("Primary")
        browse_btn.setMinimumHeight(32)
        browse_btn.clicked.connect(lambda: self.open_requested.emit())

        v.addWidget(icon)
        v.addWidget(title)
        v.addWidget(desc)
        v.addSpacing(4)
        v.addWidget(browse_btn)
        return w

    def _update_empty_state(self):
        if len(self._files) == 0:
            self.stack.setCurrentIndex(1)
            self.search_bar.setEnabled(False)
        else:
            self.stack.setCurrentIndex(0)
            self.search_bar.setEnabled(True)

    # ---------- data ----------
    @property
    def files(self) -> list[PdfFile]:
        return list(self._files)

    def add_file(self, pdf: PdfFile):
        self._files.append(pdf)
        item = QListWidgetItem(self._label(pdf))
        item.setData(Qt.UserRole, pdf)
        item.setToolTip(f"{pdf.path}\nPages: {pdf.page_count} | Size: {pdf.size_mb:.2f} MB")
        item.setSizeHint(QSize(0, 44))
        self.list.addItem(item)
        self._update_empty_state()

    def update_file(self, pdf: PdfFile):
        for i in range(self.list.count()):
            item = self.list.item(i)
            existing = item.data(Qt.UserRole)
            if existing.path == pdf.path:
                item.setText(self._label(pdf))
                item.setData(Qt.UserRole, pdf)
                item.setToolTip(f"{pdf.path}\nPages: {pdf.page_count} | Size: {pdf.size_mb:.2f} MB")
                self._files[i] = pdf
                break
        self._update_empty_state()

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
        self._update_empty_state()
        self.files_reordered.emit([])

    def remove_current(self):
        item = self.list.currentItem()
        if item:
            self._remove_item(item)

    # ---------- internals ----------
    @staticmethod
    def _label(pdf: PdfFile) -> str:
        # Formatted cleanly with document icon and metadata line
        return f"  📄  {pdf.name}\n        {pdf.page_count} pages  •  {pdf.size_mb:.2f} MB"

    def _filter_items(self, query: str):
        query = query.strip().lower()
        for i in range(self.list.count()):
            item = self.list.item(i)
            pdf = item.data(Qt.UserRole)
            matches = not query or query in pdf.name.lower() or query in str(pdf.path).lower()
            item.setHidden(not matches)

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
        pdf: PdfFile = item.data(Qt.UserRole)
        menu = QMenu(self)

        remove_act = menu.addAction("✕  Remove from Library")
        menu.addSeparator()
        open_folder_act = menu.addAction("📁  Open Containing Folder")
        copy_path_act = menu.addAction("📋  Copy Full Path")

        chosen = menu.exec(self.list.mapToGlobal(pos))
        if chosen == remove_act:
            self._remove_item(item)
        elif chosen == open_folder_act:
            if pdf.path.exists():
                subprocess.Popen(f'explorer /select,"{pdf.path}"')
        elif chosen == copy_path_act:
            QApplication.clipboard().setText(str(pdf.path))

    def _remove_item(self, item: QListWidgetItem):
        pdf = item.data(Qt.UserRole)
        self._files = [f for f in self._files if f.path.resolve() != pdf.path.resolve()]
        self.list.takeItem(self.list.row(item))
        self._update_empty_state()
        self.files_reordered.emit(list(self._files))
