"""In-app PDF preview built on Qt's native PDF engine (QPdfDocument + QPdfView).

Includes an integrated preview toolbar with vector icon controls, page navigation,
zoom controls, fit modes, and page rotation on a clean dark canvas.
"""
from pathlib import Path

from PySide6.QtCore import QPointF, Qt
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QSpinBox, QVBoxLayout, QWidget
)

from src.core.models import PdfFile
from src.ui.icons import get_icon, get_pixmap
from src.ui.theme import BG_1, BG_2, BORDER, BORDER_STRONG, TEXT, TEXT_FAINT, TEXT_MUTED


class PreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_pdf: PdfFile | None = None
        self._zoom = 1.0
        self._view_rotation = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Preview Toolbar
        self.toolbar = QFrame()
        self.toolbar.setObjectName("PreviewToolbar")
        self.toolbar.setStyleSheet(
            f"QFrame#PreviewToolbar{{"
            f"  background:{BG_2};"
            f"  border-bottom:1px solid {BORDER};"
            f"  padding:4px 8px;"
            f"}}"
        )
        tb_layout = QHBoxLayout(self.toolbar)
        tb_layout.setContentsMargins(4, 3, 4, 3)
        tb_layout.setSpacing(6)

        # Page navigation
        self.prev_btn = QPushButton()
        self.prev_btn.setIcon(get_icon("prev", TEXT, 14))
        self.prev_btn.setToolTip("Previous page (Left Arrow)")
        self.prev_btn.setFixedSize(30, 28)
        self.prev_btn.clicked.connect(self._prev_page)

        self.page_spin = QSpinBox()
        self.page_spin.setRange(1, 1)
        self.page_spin.setValue(1)
        self.page_spin.setFixedWidth(54)
        self.page_spin.setFixedHeight(28)
        self.page_spin.setToolTip("Jump to page")
        self.page_spin.valueChanged.connect(self._on_spin_page_changed)

        self.page_count_label = QLabel("/ 1")
        self.page_count_label.setStyleSheet(f"color:{TEXT_MUTED};font-size:12px;margin-right:6px;")

        self.next_btn = QPushButton()
        self.next_btn.setIcon(get_icon("next", TEXT, 14))
        self.next_btn.setToolTip("Next page (Right Arrow)")
        self.next_btn.setFixedSize(30, 28)
        self.next_btn.clicked.connect(self._next_page)

        tb_layout.addWidget(self.prev_btn)
        tb_layout.addWidget(self.page_spin)
        tb_layout.addWidget(self.page_count_label)
        tb_layout.addWidget(self.next_btn)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        sep1.setStyleSheet(f"background:{BORDER};max-width:1px;margin:2px 4px;")
        tb_layout.addWidget(sep1)

        # Zoom controls
        self.zoom_out_btn = QPushButton()
        self.zoom_out_btn.setIcon(get_icon("zoom_out", TEXT, 14))
        self.zoom_out_btn.setToolTip("Zoom out (Ctrl + -)")
        self.zoom_out_btn.setFixedSize(30, 28)
        self.zoom_out_btn.clicked.connect(self.zoom_out)

        self.zoom_label = QLabel("100%")
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setFixedWidth(46)
        self.zoom_label.setStyleSheet(f"color:{TEXT};font-size:12px;font-weight:600;")

        self.zoom_in_btn = QPushButton()
        self.zoom_in_btn.setIcon(get_icon("zoom_in", TEXT, 14))
        self.zoom_in_btn.setToolTip("Zoom in (Ctrl + +)")
        self.zoom_in_btn.setFixedSize(30, 28)
        self.zoom_in_btn.clicked.connect(self.zoom_in)

        self.fit_width_btn = QPushButton("Fit Width")
        self.fit_width_btn.setIcon(get_icon("fit_width", TEXT_MUTED, 14))
        self.fit_width_btn.setToolTip("Fit page to pane width")
        self.fit_width_btn.setFixedHeight(28)
        self.fit_width_btn.clicked.connect(self.reset_zoom)

        self.fit_page_btn = QPushButton("Fit Page")
        self.fit_page_btn.setIcon(get_icon("fit_page", TEXT_MUTED, 14))
        self.fit_page_btn.setToolTip("Fit whole page")
        self.fit_page_btn.setFixedHeight(28)
        self.fit_page_btn.clicked.connect(self._fit_page)

        tb_layout.addWidget(self.zoom_out_btn)
        tb_layout.addWidget(self.zoom_label)
        tb_layout.addWidget(self.zoom_in_btn)
        tb_layout.addWidget(self.fit_width_btn)
        tb_layout.addWidget(self.fit_page_btn)

        tb_layout.addStretch()

        # Rotate view button
        self.rotate_view_btn = QPushButton("Rotate")
        self.rotate_view_btn.setIcon(get_icon("rotate", TEXT_MUTED, 14))
        self.rotate_view_btn.setToolTip("Temporarily rotate current view clockwise 90°")
        self.rotate_view_btn.setFixedHeight(28)
        self.rotate_view_btn.clicked.connect(self._rotate_view_clockwise)
        tb_layout.addWidget(self.rotate_view_btn)

        layout.addWidget(self.toolbar)

        # Document & View
        self.document = QPdfDocument(self)
        self.view = QPdfView(self)
        self.view.setDocument(self.document)
        self.view.setPageMode(QPdfView.PageMode.MultiPage)
        self.view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        self.view.setPageSpacing(12)
        # Deep dark canvas background
        self.view.setStyleSheet("background:#12151e;border:none;")

        self.error_label = QLabel()
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet(f"color:{TEXT_MUTED};font-size:13px;padding:24px;")
        self.error_label.setVisible(False)

        layout.addWidget(self.error_label)
        layout.addWidget(self.view, 1)

        self.document.statusChanged.connect(self._on_status_changed)

        nav = self.view.pageNavigator()
        if hasattr(nav, "currentPageChanged"):
            nav.currentPageChanged.connect(self._on_view_page_changed)

    # ---------- loading ----------
    def load_pdf(self, pdf: PdfFile | None):
        self.current_pdf = pdf
        self.document.close()
        self.error_label.setVisible(False)
        self.view.setVisible(True)
        self._zoom = 1.0
        self._view_rotation = 0
        self.view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        self.zoom_label.setText("100%")

        if pdf is None:
            self.toolbar.setEnabled(False)
            self.page_spin.setRange(1, 1)
            self.page_spin.setValue(1)
            self.page_count_label.setText("/ 1")
            return

        self.toolbar.setEnabled(True)
        path = Path(pdf.path)
        if not path.exists():
            self._show_error(f"File not found: {path.name}")
            return

        self.document.load(str(path))
        if self.document.status() == QPdfDocument.Status.Error and pdf.password:
            self.document.setPassword(pdf.password.encode("utf-8"))
            self.document.load(str(path))

        if self.document.status() == QPdfDocument.Status.Error:
            self._show_error(f"Cannot preview {path.name} ({self.document.error()}).")
        else:
            total_pages = max(1, self.document.pageCount())
            self.page_spin.blockSignals(True)
            self.page_spin.setRange(1, total_pages)
            self.page_spin.setValue(1)
            self.page_spin.blockSignals(False)
            self.page_count_label.setText(f"/ {total_pages}")

    def _on_status_changed(self, status):
        if status == QPdfDocument.Status.Error:
            self._show_error(
                f"Cannot preview {self.current_pdf.name if self.current_pdf else 'file'} "
                f"({self.document.error()})."
            )
        elif status == QPdfDocument.Status.Ready:
            total_pages = max(1, self.document.pageCount())
            self.page_spin.blockSignals(True)
            self.page_spin.setRange(1, total_pages)
            self.page_spin.setValue(1)
            self.page_spin.blockSignals(False)
            self.page_count_label.setText(f"/ {total_pages}")

    def _show_error(self, message: str):
        self.view.setVisible(False)
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    # ---------- navigation / zoom ----------
    def go_to_page(self, page: int):
        """Jump to a 0-based page index."""
        if self.document.status() != QPdfDocument.Status.Ready:
            return
        page = max(0, min(page, self.document.pageCount() - 1))
        self.view.pageNavigator().jump(page, QPointF(), self.view.zoomFactor())
        self.page_spin.blockSignals(True)
        self.page_spin.setValue(page + 1)
        self.page_spin.blockSignals(False)

    def _prev_page(self):
        curr = self.view.pageNavigator().currentPage()
        if curr > 0:
            self.go_to_page(curr - 1)

    def _next_page(self):
        curr = self.view.pageNavigator().currentPage()
        if curr < self.document.pageCount() - 1:
            self.go_to_page(curr + 1)

    def _on_spin_page_changed(self, val: int):
        self.go_to_page(val - 1)

    def _on_view_page_changed(self, page: int):
        self.page_spin.blockSignals(True)
        self.page_spin.setValue(page + 1)
        self.page_spin.blockSignals(False)

    def zoom_in(self):
        self._sync_zoom_from_view()
        self._set_zoom(self._zoom * 1.25)

    def zoom_out(self):
        self._sync_zoom_from_view()
        self._set_zoom(self._zoom / 1.25)

    def reset_zoom(self):
        self._zoom = 1.0
        self.view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        self.zoom_label.setText("Fit W")

    def _fit_page(self):
        self._zoom = 1.0
        self.view.setZoomMode(QPdfView.ZoomMode.FitInView)
        self.zoom_label.setText("Fit Pg")

    def _rotate_view_clockwise(self):
        self._view_rotation = (self._view_rotation + 90) % 360

    def _sync_zoom_from_view(self):
        if self.view.zoomMode() != QPdfView.ZoomMode.Custom:
            self._zoom = self.view.zoomFactor() or 1.0

    def _set_zoom(self, factor: float):
        self._zoom = max(0.2, min(5.0, factor))
        self.view.setZoomMode(QPdfView.ZoomMode.Custom)
        self.view.setZoomFactor(self._zoom)
        self.zoom_label.setText(f"{int(round(self._zoom * 100))}%")
