import os
import subprocess
from pathlib import Path

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtGui import QAction, QColor, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMenu, QPushButton, QStackedWidget, QVBoxLayout, QWidget
)

from src.core.models import PdfFile
from src.ui.icons import get_icon, get_pixmap
from src.ui.theme import (
    ACCENT, BG_1, BG_2, BORDER, BORDER_STRONG, CANVAS, CANVAS_SOFT,
    DANGER, HAIRLINE, HAIRLINE_STRONG, INK, INK_FAINT, INK_MUTE, INK_MUTE_2,
    ON_PRIMARY, PRIMARY, RADIUS_MD, RADIUS_SM, SUCCESS, TEXT, TEXT_FAINT, TEXT_MUTED
)


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
        self.search_bar.setPlaceholderText("Filter files by name…")
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.addAction(get_icon("search", TEXT_MUTED, 14), QLineEdit.LeadingPosition)
        self.search_bar.textChanged.connect(self._filter_items)
        layout.addWidget(self.search_bar)

        # Stack to toggle between empty drop zone and file list
        self.stack = QStackedWidget()

        # 0: File list
        self.list = QListWidget()
        self.list.setObjectName("FileList")
        self.list.setDragDropMode(QListWidget.InternalMove)
        self.list.setDefaultDropAction(Qt.MoveAction)
        self.list.setSelectionMode(QListWidget.SingleSelection)
        self.list.setFrameShape(QFrame.NoFrame)
        self.list.setIconSize(QSize(24, 24))
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
            f"  background:{CANVAS_SOFT};"
            f"  border:2px dashed {HAIRLINE};"
            f"  border-radius:{RADIUS_MD}px;"
            f"}}"
            f"QFrame:hover{{"
            f"  border-color:{PRIMARY};"
            f"}}"
        )
        v = QVBoxLayout(w)
        v.setAlignment(Qt.AlignCenter)
        v.setSpacing(10)
        v.setContentsMargins(20, 28, 20, 28)

        icon_label = QLabel()
        icon_label.setPixmap(get_pixmap("pdf", INK_MUTE_2, 38))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background:transparent;border:none;")

        title = QLabel("Library is Empty")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size:14px;font-weight:500;color:{INK};background:transparent;border:none;")

        desc = QLabel("Drag & drop PDF files here\nor choose files from your computer")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size:12px;color:{INK_MUTE};background:transparent;border:none;")

        browse_btn = QPushButton("  Browse PDFs…")
        browse_btn.setObjectName("Primary")
        browse_btn.setIcon(get_icon("add", ON_PRIMARY, 14))
        browse_btn.setMinimumHeight(34)
        browse_btn.clicked.connect(lambda: self.open_requested.emit())

        v.addWidget(icon_label)
        v.addWidget(title)
        v.addWidget(desc)
        v.addSpacing(6)
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
        item.setIcon(get_icon("pdf", PRIMARY, 22))
        item.setData(Qt.UserRole, pdf)
        item.setToolTip(f"{pdf.path}\nPages: {pdf.page_count} | Size: {pdf.size_mb:.2f} MB")
        item.setSizeHint(QSize(0, 50))
        self.list.addItem(item)
        self._update_empty_state()

    def update_file(self, pdf: PdfFile):
        for i in range(self.list.count()):
            item = self.list.item(i)
            existing = item.data(Qt.UserRole)
            if existing.path == pdf.path:
                item.setText(self._label(pdf))
                item.setIcon(get_icon("pdf", DANGER, 22))
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
        return f"{pdf.name}\n{pdf.page_count} page{'s' if pdf.page_count != 1 else ''}  •  {pdf.size_mb:.2f} MB"

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

        remove_act = menu.addAction(get_icon("trash", DANGER, 14), "Remove from Library")
        menu.addSeparator()
        open_folder_act = menu.addAction(get_icon("home", TEXT_MUTED, 14), "Open Containing Folder")
        copy_path_act = menu.addAction("Copy Full Path")

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
