from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QSpinBox,
    QStackedWidget, QVBoxLayout, QWidget
)

from src.core.models import PdfFile
from src.core.pdf_engine import PERM_ALL, PERM_PRINT


def _parse_page_list(text: str, page_count: int, zero_based: bool = False):
    """Parse ``1,3,5-8`` into a list of indices.

    Blank text returns ``None`` (meaning "all pages"). With ``zero_based=False``
    the numbers are 1-based user input and are converted to 0-based indices;
    with ``zero_based=True`` they are returned unchanged.
    """
    text = (text or "").strip()
    if not text:
        return None

    pages: list[int] = []
    for chunk in text.replace(" ", "").split(","):
        if not chunk:
            continue
        if "-" in chunk:
            parts = chunk.split("-")
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                raise ValueError(
                    f"Invalid page range “{chunk}”. Use numbers like 1,3,5-8."
                )
            start, end = int(parts[0]), int(parts[1])
            if end < start:
                raise ValueError(f"Page range “{chunk}” ends before it starts.")
            pages.extend(range(start, end + 1))
        else:
            if not chunk.isdigit():
                raise ValueError(
                    f"Invalid page number “{chunk}”. Use numbers like 1,3,5-8."
                )
            pages.append(int(chunk))

    if page_count:
        out_of_range = [p for p in pages if p < 1 or p > page_count]
        if out_of_range:
            raise ValueError(
                f"Page {out_of_range[0]} is out of range 1-{page_count}."
            )

    return pages if zero_based else [p - 1 for p in pages]


class ToolPanelsStack(QWidget):
    operation_requested = Signal(str, dict)
    validation_failed = Signal(str)

    def __init__(self):
        super().__init__()
        self.current_file: PdfFile | None = None
        self._page_count: int = 0
        # tool key -> (button, requirement) where requirement is
        # "file" (needs a loaded PDF) or "images" (needs queued images).
        self._actions: list[tuple[QPushButton, str]] = []
        self._setup_ui()

    # ---------- setup ----------
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 18)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.panels = {
            "merge": self._create_merge_panel(),
            "split": self._create_split_panel(),
            "rotate": self._create_rotate_panel(),
            "reorder": self._create_reorder_panel(),
            "watermark": self._create_watermark_panel(),
            "encrypt": self._create_encrypt_panel(),
            "decrypt": self._create_decrypt_panel(),
            "compress": self._create_compress_panel(),
            "linearize": self._create_linearize_panel(),
            "to images": self._create_to_images_panel(),
            "images to pdf": self._create_images_to_pdf_panel(),
        }

        for panel in self.panels.values():
            self.stack.addWidget(panel)

        self.empty = QLabel("Select a tool from the sidebar")
        self.empty.setAlignment(Qt.AlignCenter)
        self.empty.setStyleSheet("color: #888; font-size: 14px;")
        self.stack.addWidget(self.empty)
        self.stack.setCurrentWidget(self.empty)

    def _primary_button(self, text: str, handler, requirement: str = "file") -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("Primary")
        btn.setMinimumHeight(36)
        btn.clicked.connect(handler)
        self._actions.append((btn, requirement))
        return btn

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color:#9aa1b2;font-size:12px;font-weight:500;")
        return lbl

    def _hint(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color:#6b7284;font-size:11px;")
        lbl.setWordWrap(True)
        return lbl

    # ---------- public API ----------
    def set_file(self, pdf: PdfFile | None):
        self.current_file = pdf
        self._page_count = pdf.page_count if pdf else 0
        self._update_panel_state()

    def show_tool(self, name: str):
        panel = self.panels.get(name.lower())
        self.stack.setCurrentWidget(panel if panel else self.empty)
        self._update_panel_state()

    def _update_panel_state(self):
        has_file = self.current_file is not None
        has_images = self.img_list.count() > 0
        for btn, requirement in self._actions:
            if requirement == "file":
                btn.setEnabled(has_file)
            elif requirement == "images":
                btn.setEnabled(has_images)
            else:
                btn.setEnabled(True)

    def _emit(self, op: str, build_params):
        """Build and emit params, turning bad input into a friendly message."""
        try:
            params = build_params()
        except ValueError as exc:
            self.validation_failed.emit(str(exc))
            return
        self.operation_requested.emit(op, params)

    # ---------- panels ----------
    def _create_merge_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        layout.addWidget(self._hint(
            "All PDFs in the Home list are merged in list order. "
            "Drag to reorder them first."
        ))

        layout.addWidget(self._field_label("Output file"))
        self.merge_out = QLineEdit()
        self.merge_out.setPlaceholderText("Default: merged.pdf next to the first source")
        browse = QPushButton("Browse…")
        browse.clicked.connect(lambda: self._browse_save(self.merge_out, "PDF Files (*.pdf)"))
        hbox = QHBoxLayout()
        hbox.addWidget(self.merge_out)
        hbox.addWidget(browse)
        layout.addLayout(hbox)

        btn = self._primary_button("Merge PDFs", lambda: self._emit("merge", lambda: {
            "output_path": Path(self.merge_out.text().strip()) if self.merge_out.text().strip() else None
        }))
        layout.addSpacing(6)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_split_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        form = QFormLayout()
        form.setSpacing(10)
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

        btn = self._primary_button("Split PDF", lambda: self._emit("split", lambda: {
            "every": self.split_every.value(),
            "output_dir": Path(self.split_outdir.text().strip()) if self.split_outdir.text().strip() else None
        }))
        layout.addSpacing(6)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_rotate_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        form = QFormLayout()
        form.setSpacing(10)
        self.rotate_degrees = QComboBox()
        self.rotate_degrees.addItems(["90°", "180°", "270°"])
        form.addRow("Rotation:", self.rotate_degrees)
        self.rotate_pages = QLineEdit()
        self.rotate_pages.setPlaceholderText("e.g. 1,3,5-8  (blank = all pages)")
        form.addRow("Pages:", self.rotate_pages)
        layout.addLayout(form)

        btn = self._primary_button("Rotate Pages", lambda: self._emit("rotate", lambda: {
            "degrees": int(self.rotate_degrees.currentText().replace("°", "")),
            "page_indices": _parse_page_list(self.rotate_pages.text(), self._page_count),
        }))
        layout.addSpacing(6)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_reorder_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        layout.addWidget(self._field_label("New page order (1-based)"))
        self.reorder_order = QLineEdit()
        self.reorder_order.setPlaceholderText("e.g. 3,1,2")
        layout.addWidget(self.reorder_order)
        layout.addWidget(self._hint(
            "Leave blank to keep the current order. Pages you leave out are dropped."
        ))

        btn = self._primary_button("Apply Reorder", lambda: self._emit("reorder", lambda: {
            "new_order": _parse_page_list(self.reorder_order.text(), self._page_count),
        }))
        layout.addSpacing(6)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_watermark_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        form = QFormLayout()
        form.setSpacing(10)
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

        def params():
            if not self.wm_text.text().strip():
                raise ValueError("Enter the watermark text first.")
            return {
                "text": self.wm_text.text(),
                "opacity": self.wm_opacity.value(),
                "font_size": self.wm_size.value(),
            }

        btn = self._primary_button("Add Watermark",
                                   lambda: self._emit("add_watermark", params))
        layout.addSpacing(6)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_encrypt_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        form = QFormLayout()
        form.setSpacing(10)
        self.enc_user_pw = QLineEdit()
        self.enc_user_pw.setEchoMode(QLineEdit.Password)
        self.enc_user_pw.setPlaceholderText("User password (required)")
        form.addRow("User Password:", self.enc_user_pw)
        self.enc_owner_pw = QLineEdit()
        self.enc_owner_pw.setEchoMode(QLineEdit.Password)
        self.enc_owner_pw.setPlaceholderText("Owner password (defaults to user password)")
        form.addRow("Owner Password:", self.enc_owner_pw)
        self.enc_perms = QComboBox()
        self.enc_perms.addItems([
            "No permissions (print/copy/edit denied)",
            "Allow printing",
            "Allow all",
        ])
        # Encrypting without restrictions is the least surprising default.
        self.enc_perms.setCurrentIndex(2)
        form.addRow("Permissions:", self.enc_perms)
        layout.addLayout(form)
        layout.addWidget(self._hint(
            "AES-256 encryption. Keep the user password somewhere safe — "
            "it cannot be recovered."
        ))

        def params():
            if not self.enc_user_pw.text():
                raise ValueError("Enter a user password to encrypt with.")
            return {
                "user_password": self.enc_user_pw.text(),
                "owner_password": self.enc_owner_pw.text() or None,
                "permissions": {
                    0: 0,
                    1: PERM_PRINT,
                    2: PERM_ALL,
                }[self.enc_perms.currentIndex()],
            }

        btn = self._primary_button("Encrypt PDF",
                                   lambda: self._emit("encrypt", params))
        layout.addSpacing(6)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_decrypt_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        form = QFormLayout()
        form.setSpacing(10)
        self.dec_pw = QLineEdit()
        self.dec_pw.setEchoMode(QLineEdit.Password)
        self.dec_pw.setPlaceholderText("Enter password (blank = one used to open)")
        form.addRow("Password:", self.dec_pw)
        layout.addLayout(form)

        btn = self._primary_button("Decrypt PDF", lambda: self._emit("decrypt", lambda: {
            "password": self.dec_pw.text()
        }))
        layout.addSpacing(6)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_compress_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        form = QFormLayout()
        form.setSpacing(10)
        self.comp_quality = QSpinBox()
        self.comp_quality.setRange(10, 100)
        self.comp_quality.setValue(75)
        form.addRow("Image quality (%):", self.comp_quality)
        layout.addLayout(form)
        layout.addWidget(self._hint(
            "Images above 150 DPI are downsampled and re-encoded at this "
            "quality; fonts and file structure are cleaned up too."
        ))

        btn = self._primary_button("Compress PDF", lambda: self._emit("compress", lambda: {
            "quality": self.comp_quality.value()
        }))
        layout.addSpacing(6)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_linearize_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        layout.addWidget(self._hint(
            "Linearizing reorganizes the file so a web viewer can display the "
            "first page before the whole document has downloaded."
        ))

        btn = self._primary_button("Linearize PDF", lambda: self._emit("linearize", lambda: {}))
        layout.addSpacing(6)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_to_images_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        form = QFormLayout()
        form.setSpacing(10)
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

        btn = self._primary_button("Export Images", lambda: self._emit("to_images", lambda: {
            "dpi": self.img_dpi.value(),
            "fmt": self.img_format.currentText().lower(),
            "output_dir": Path(self.img_outdir.text().strip()) if self.img_outdir.text().strip() else None
        }))
        layout.addSpacing(6)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_images_to_pdf_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        layout.addWidget(self._field_label("Images"))
        self.img_list = QListWidget()
        self.img_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.img_list.model().rowsInserted.connect(self._update_panel_state)
        self.img_list.model().rowsRemoved.connect(self._update_panel_state)
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

        def params():
            image_paths = [
                Path(self.img_list.item(i).text()) for i in range(self.img_list.count())
            ]
            if not image_paths:
                raise ValueError("Add at least one image.")
            return {
                "image_paths": image_paths,
                "output_path": Path(self.img2pdf_out.text().strip()) if self.img2pdf_out.text().strip() else None,
            }

        convert_btn = self._primary_button(
            "Create PDF", lambda: self._emit("images_to_pdf", params), requirement="images"
        )
        layout.addWidget(convert_btn)
        layout.addStretch()
        return w

    # ---------- browse helpers ----------
    def _browse_dir(self, line_edit: QLineEdit):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if dir_path:
            line_edit.setText(dir_path)

    def _browse_save(self, line_edit: QLineEdit, filter_str: str):
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "", filter_str)
        if path:
            line_edit.setText(path)

    def _add_images(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.tif)"
        )
        for p in paths:
            self.img_list.addItem(p)
