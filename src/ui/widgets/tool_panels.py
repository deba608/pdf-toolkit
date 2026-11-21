from pathlib import Path
import pymupdf as fitz
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QLabel, QPushButton,
    QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox, QComboBox,
    QFileDialog, QHBoxLayout, QGroupBox, QFormLayout, QListWidget,
    QListWidgetItem, QAbstractItemView
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor

from src.core.models import PdfFile

_PERM_PRINT = fitz.PDF_PERM_PRINT | fitz.PDF_PERM_PRINT_HQ
_PERM_MODIFY = fitz.PDF_PERM_MODIFY
_PERM_COPY = fitz.PDF_PERM_COPY
_PERM_ANNOTATE = fitz.PDF_PERM_ANNOTATE
_PERM_FORM = fitz.PDF_PERM_FORM
_PERM_ACCESSIBILITY = fitz.PDF_PERM_ACCESSIBILITY
_PERM_ASSEMBLE = fitz.PDF_PERM_ASSEMBLE


def _parse_page_list(text: str, page_count: int, zero_based: bool = False):
    """Parse '1,3,5-8' into a list of indices. Blank -> None (means all pages).

    With zero_based=False the returned indices are converted to 0-based, which is
    what the engine expects. With zero_based=True the numbers are taken as-is.
    """
    text = (text or "").strip()
    if not text:
        return None
    pages = []
    for chunk in text.replace(" ", "").split(","):
        if not chunk:
            continue
        if "-" in chunk:
            start_s, _, end_s = chunk.partition("-")
            start, end = int(start_s), int(end_s)
            if end < start:
                raise ValueError(f"Invalid page range: {chunk}")
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(chunk))
    if page_count:
        for p in pages:
            if p < 1 or p > page_count:
                raise ValueError(f"Page {p} out of range 1-{page_count}")
    if zero_based:
        return pages
    return [p - 1 for p in pages]


class ToolPanelsStack(QWidget):
    operation_requested = Signal(str, dict)

    def __init__(self):
        super().__init__()
        self.current_file: PdfFile = None
        self._page_count: int = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Create panels
        self.panels = {
            "merge": self._create_merge_panel(),
            "split": self._create_split_panel(),
            "rotate": self._create_rotate_panel(),
            "reorder": self._create_reorder_panel(),
            "watermark": self._create_watermark_panel(),
            "encrypt": self._create_encrypt_panel(),
            "decrypt": self._create_decrypt_panel(),
            "compress": self._create_compress_panel(),
            "to images": self._create_to_images_panel(),
            "images to pdf": self._create_images_to_pdf_panel(),
        }

        for panel in self.panels.values():
            self.stack.addWidget(panel)

        # Default empty state
        self.empty = QLabel("Select a tool from the Tools tab or menu")
        self.empty.setAlignment(Qt.AlignCenter)
        self.empty.setStyleSheet("color: #888; font-size: 14px;")
        self.stack.addWidget(self.empty)
        self.stack.setCurrentWidget(self.empty)

    def set_file(self, pdf: PdfFile):
        self.current_file = pdf
        self._page_count = pdf.page_count if pdf else 0
        self._update_panel_state()

    def _update_panel_state(self):
        """Enable/disable tool panel operations based on whether a file is loaded."""
        has_file = self.current_file is not None
        # Enable/disable operations that require a file
        # We'll enable/disable by finding buttons in each panel
        for i in range(self.stack.count()):
            panel = self.stack.widget(i)
            if panel is self.empty:
                continue
            # Find enable/disableable buttons
            for btn in panel.findChildren(QPushButton):
                txt = btn.text()
                # Buttons that should be disabled without a file
                if not has_file:
                    if txt in {"Rotate Pages", "Apply Reorder", "Add Watermark",
                              "Encrypt", "Decrypt", "Compress", "Convert",
                              "Browse"}:
                        btn.setEnabled(False)
                else:
                    if txt in {"Rotate Pages", "Apply Reorder", "Add Watermark",
                              "Encrypt", "Decrypt", "Compress", "Convert"}:
                        btn.setEnabled(True)

    def show_tool(self, name: str):
        panel = self.panels.get(name.lower())
        if panel:
            self.stack.setCurrentWidget(panel)
        else:
            self.stack.setCurrentWidget(self.empty)

    def _create_merge_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Merge PDFs"))
        layout.addWidget(QLabel("Add multiple PDFs to the Files tab, then click Merge"))

        self.merge_out = QLineEdit()
        self.merge_out.setPlaceholderText("Output PDF path (default: merged.pdf in source folder)")
        browse = QPushButton("Browse")
        browse.clicked.connect(lambda: self._browse_save(self.merge_out, "PDF Files (*.pdf)"))
        hbox = QHBoxLayout()
        hbox.addWidget(self.merge_out)
        hbox.addWidget(browse)
        layout.addLayout(hbox)

        btn = QPushButton("Merge All Files")
        btn.clicked.connect(lambda: self.operation_requested.emit("merge", {
            "output_path": Path(self.merge_out.text()) if self.merge_out.text() else None
        }))
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_split_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Split PDF"))
        form = QFormLayout()
        self.split_every = QSpinBox()
        self.split_every.setRange(1, 1000)
        self.split_every.setValue(1)
        form.addRow("Pages per file:", self.split_every)

        self.split_outdir = QLineEdit()
        self.split_outdir.setPlaceholderText("Output folder (default: same as source)")
        browse = QPushButton("Browse")
        browse.clicked.connect(lambda: self._browse_dir(self.split_outdir))
        hbox = QHBoxLayout()
        hbox.addWidget(self.split_outdir)
        hbox.addWidget(browse)
        form.addRow("Output:", hbox)
        layout.addLayout(form)

        btn = QPushButton("Split")
        btn.clicked.connect(lambda: self.operation_requested.emit("split", {
            "every": self.split_every.value(),
            "output_dir": Path(self.split_outdir.text()) if self.split_outdir.text() else None
        }))
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _browse_dir(self, line_edit: QLineEdit):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if dir_path:
            line_edit.setText(dir_path)

    def _create_rotate_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Rotate Pages"))
        form = QFormLayout()
        self.rotate_degrees = QComboBox()
        self.rotate_degrees.addItems(["90°", "180°", "270°"])
        form.addRow("Rotation:", self.rotate_degrees)
        self.rotate_pages = QLineEdit()
        self.rotate_pages.setPlaceholderText("Pages e.g. 1,3,5-8 (blank = all pages)")
        form.addRow("Pages:", self.rotate_pages)
        layout.addLayout(form)
        btn = QPushButton("Rotate Pages")
        btn.clicked.connect(lambda: self.operation_requested.emit("rotate", {
            "degrees": int(self.rotate_degrees.currentText().replace("°", "")),
            "page_indices": _parse_page_list(self.rotate_pages.text(), self._page_count),
        }))
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_reorder_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Reorder Pages"))
        self.reorder_order = QLineEdit()
        self.reorder_order.setPlaceholderText("New page order e.g. 3,1,2 (1-based)")
        layout.addWidget(self.reorder_order)
        layout.addWidget(QLabel("Blank keeps the current order."))
        btn = QPushButton("Apply Reorder")
        btn.clicked.connect(lambda: self.operation_requested.emit("reorder", {
            "new_order": _parse_page_list(self.reorder_order.text(), self._page_count, zero_based=True),
        }))
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_watermark_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Add Watermark"))
        form = QFormLayout()
        self.wm_text = QLineEdit()
        self.wm_text.setPlaceholderText("CONFIDENTIAL")
        form.addRow("Text:", self.wm_text)
        self.wm_opacity = QDoubleSpinBox()
        self.wm_opacity.setRange(0.1, 1.0)
        self.wm_opacity.setSingleStep(0.1)
        self.wm_opacity.setValue(0.3)
        form.addRow("Opacity:", self.wm_opacity)
        self.wm_size = QSpinBox()
        self.wm_size.setRange(12, 200)
        self.wm_size.setValue(48)
        form.addRow("Font Size:", self.wm_size)
        layout.addLayout(form)
        btn = QPushButton("Add Watermark")
        btn.clicked.connect(lambda: self.operation_requested.emit("add_watermark", {
            "text": self.wm_text.text(),
            "opacity": self.wm_opacity.value(),
            "font_size": self.wm_size.value()
        }))
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_encrypt_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Encrypt PDF"))
        form = QFormLayout()
        self.enc_user_pw = QLineEdit()
        self.enc_user_pw.setEchoMode(QLineEdit.Password)
        self.enc_user_pw.setPlaceholderText("User password (required)")
        form.addRow("User Password:", self.enc_user_pw)
        self.enc_owner_pw = QLineEdit()
        self.enc_owner_pw.setEchoMode(QLineEdit.Password)
        self.enc_owner_pw.setPlaceholderText("Owner password (optional)")
        form.addRow("Owner Password:", self.enc_owner_pw)
        self.enc_perms = QComboBox()
        self.enc_perms.addItems(["No permissions (print/copy/edit denied)", "Allow printing", "Allow all"])
        form.addRow("Permissions:", self.enc_perms)
        layout.addLayout(form)
        btn = QPushButton("Encrypt")
        btn.clicked.connect(lambda: self.operation_requested.emit("encrypt", {
            "user_password": self.enc_user_pw.text(),
            "owner_password": self.enc_owner_pw.text() or None,
            "permissions": {
                0: 0,                                              # nothing allowed
                1: _PERM_PRINT,                                    # printing only
                2: _PERM_PRINT | _PERM_MODIFY | _PERM_COPY
                   | _PERM_ANNOTATE | _PERM_FORM | _PERM_ACCESSIBILITY
                   | _PERM_ASSEMBLE,                               # everything
            }[self.enc_perms.currentIndex()],
        }))
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_decrypt_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Decrypt PDF"))
        form = QFormLayout()
        self.dec_pw = QLineEdit()
        self.dec_pw.setEchoMode(QLineEdit.Password)
        self.dec_pw.setPlaceholderText("Enter password")
        form.addRow("Password:", self.dec_pw)
        layout.addLayout(form)
        btn = QPushButton("Decrypt")
        btn.clicked.connect(lambda: self.operation_requested.emit("decrypt", {
            "password": self.dec_pw.text()
        }))
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_compress_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Compress PDF"))
        form = QFormLayout()
        self.comp_quality = QSpinBox()
        self.comp_quality.setRange(10, 100)
        self.comp_quality.setValue(75)
        form.addRow("Image Quality (%):", self.comp_quality)
        layout.addLayout(form)
        btn = QPushButton("Compress")
        btn.clicked.connect(lambda: self.operation_requested.emit("compress", {
            "quality": self.comp_quality.value()
        }))
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_to_images_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Convert to Images"))
        form = QFormLayout()
        self.img_dpi = QSpinBox()
        self.img_dpi.setRange(72, 600)
        self.img_dpi.setValue(200)
        form.addRow("DPI:", self.img_dpi)
        self.img_format = QComboBox()
        self.img_format.addItems(["PNG", "JPG"])
        form.addRow("Format:", self.img_format)

        self.img_outdir = QLineEdit()
        self.img_outdir.setPlaceholderText("Output folder (default: same as source)")
        browse = QPushButton("Browse")
        browse.clicked.connect(lambda: self._browse_dir(self.img_outdir))
        hbox = QHBoxLayout()
        hbox.addWidget(self.img_outdir)
        hbox.addWidget(browse)
        form.addRow("Output:", hbox)
        layout.addLayout(form)

        btn = QPushButton("Convert")
        btn.clicked.connect(lambda: self.operation_requested.emit("to_images", {
            "dpi": self.img_dpi.value(),
            "fmt": self.img_format.currentText().lower(),
            "output_dir": Path(self.img_outdir.text()) if self.img_outdir.text() else None
        }))
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_images_to_pdf_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Images to PDF"))
        layout.addWidget(QLabel("Select image files:"))
        self.img_list = QListWidget()
        self.img_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.img_list)
        btns = QHBoxLayout()
        add_btn = QPushButton("Add Images")
        add_btn.clicked.connect(self._add_images)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.img_list.clear)
        btns.addWidget(add_btn)
        btns.addWidget(clear_btn)
        layout.addLayout(btns)

        self.img2pdf_out = QLineEdit()
        self.img2pdf_out.setPlaceholderText("Output PDF path")
        browse = QPushButton("Browse")
        browse.clicked.connect(lambda: self._browse_save(self.img2pdf_out, "PDF Files (*.pdf)"))
        hbox = QHBoxLayout()
        hbox.addWidget(self.img2pdf_out)
        hbox.addWidget(browse)
        layout.addLayout(hbox)

        convert_btn = QPushButton("Create PDF")
        convert_btn.clicked.connect(lambda: self.operation_requested.emit("images_to_pdf", {
            "image_paths": [Path(self.img_list.item(i).text()) for i in range(self.img_list.count())],
            "output_path": Path(self.img2pdf_out.text()) if self.img2pdf_out.text() else None
        }))
        layout.addWidget(convert_btn)
        layout.addStretch()
        return w

    def _browse_save(self, line_edit: QLineEdit, filter_str: str):
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "", filter_str)
        if path:
            line_edit.setText(path)

    def _add_images(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        for p in paths:
            self.img_list.addItem(p)