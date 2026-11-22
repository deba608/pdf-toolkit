"""In-app PDF preview built on Qt's native PDF engine (QtPdf).

Native rendering keeps the promise of the app: no network, no bundled
JavaScript, and password-protected files can be opened with the password the
user already typed when loading them.
"""
from pathlib import Path

from PySide6.QtCore import QPointF, Qt
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.core.models import PdfFile


class PreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_pdf: PdfFile | None = None
        self._zoom = 1.0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.document = QPdfDocument(self)
        self.view = QPdfView(self)
        self.view.setDocument(self.document)
        self.view.setPageMode(QPdfView.PageMode.MultiPage)
        self.view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        self.view.setPageSpacing(8)
        self.view.setStyleSheet("background:#f0f0f0;border:none;")

        self.error_label = QLabel()
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("color:#9aa1b2;font-size:12px;padding:16px;")
        self.error_label.setVisible(False)

        layout.addWidget(self.error_label)
        layout.addWidget(self.view, 1)

        self.document.statusChanged.connect(self._on_status_changed)

    # ---------- loading ----------
    def load_pdf(self, pdf: PdfFile | None):
        self.current_pdf = pdf
        self.document.close()
        self.error_label.setVisible(False)
        self.view.setVisible(True)
        self._zoom = 1.0
        self.view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

        if pdf is None:
            return
        path = Path(pdf.path)
        if not path.exists():
            self._show_error(f"File not found: {path.name}")
            return

        self.document.load(str(path))
        # A locked document reports Error/IncorrectPassword: supply the
        # password captured when the file was added and try once more.
        if (self.document.status() == QPdfDocument.Status.Error
                and pdf.password):
            self.document.setPassword(pdf.password.encode("utf-8"))
            self.document.load(str(path))

        if self.document.status() == QPdfDocument.Status.Error:
            self._show_error(
                f"Cannot preview {path.name} ({self.document.error()})."
            )

    def _on_status_changed(self, status):
        if status == QPdfDocument.Status.Error:
            self._show_error(
                f"Cannot preview {self.current_pdf.name if self.current_pdf else 'file'} "
                f"({self.document.error()})."
            )

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

    def zoom_in(self):
        self._set_zoom(self._zoom * 1.2)

    def zoom_out(self):
        self._set_zoom(self._zoom / 1.2)

    def reset_zoom(self):
        self._zoom = 1.0
        self.view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

    def _set_zoom(self, factor: float):
        self._zoom = max(0.25, min(4.0, factor))
        self.view.setZoomMode(QPdfView.ZoomMode.Custom)
        self.view.setZoomFactor(self._zoom)
