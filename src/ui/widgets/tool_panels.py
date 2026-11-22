from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout,
    QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QSpinBox,
    QStackedWidget, QVBoxLayout, QWidget
)

from src.core.models import PdfFile
from src.core.pdf_engine import PERM_ALL, PERM_PRINT
from src.ui.icons import get_icon
from src.ui.theme import (
    ACCENT, BG_1, BG_2, BG_3, BORDER, BORDER_STRONG, TEXT, TEXT_FAINT, TEXT_MUTED
)


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
        self._actions: list[tuple[QPushButton, str]] = []
        self._setup_ui()

    # ---------- setup ----------
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(0)

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
            "to images": self._create_to_images_panel(),
            "images to pdf": self._create_images_to_pdf_panel(),
        }

        for panel in self.panels.values():
            self.stack.addWidget(panel)

        self.empty = QLabel("Select a tool from the sidebar")
        self.empty.setAlignment(Qt.AlignCenter)
        self.empty.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px;")
        self.stack.addWidget(self.empty)
        self.stack.setCurrentWidget(self.empty)

    def _primary_button(self, text: str, icon_name: str, handler, requirement: str = "file") -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("Primary")
        btn.setIcon(get_icon(icon_name, "#ffffff", 16))
        btn.setMinimumHeight(42)
        btn.clicked.connect(handler)
        self._actions.append((btn, requirement))
        return btn

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{TEXT};font-size:12px;font-weight:600;")
        return lbl

    def _hint(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:12px;line-height:16px;")
        lbl.setWordWrap(True)
        return lbl

    def _section_header(self, title: str) -> QWidget:
        """Clean semantic section header with subtle divider - no nested cards!"""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 8, 0, 4)
        v.setSpacing(6)

        lbl = QLabel(title)
        lbl.setStyleSheet(f"color:{TEXT};font-size:13px;font-weight:600;letter-spacing:-0.2px;")
        v.addWidget(lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
        v.addWidget(sep)
        return w

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
        has_images = hasattr(self, "img_list") and self.img_list.count() > 0
        for btn, requirement in self._actions:
            if requirement == "file":
                btn.setEnabled(has_file)
            elif requirement == "images":
                btn.setEnabled(has_images)
            else:
                btn.setEnabled(True)

    def _emit(self, op: str, build_params):
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
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Merge Configuration"))
        layout.addWidget(self._hint(
            "Combines all PDF files currently loaded in your Home Library in top-to-bottom sequence. "
            "You can drag items in the library list to rearrange their merge order."
        ))

        layout.addWidget(self._section_header("Output Destination"))
        layout.addWidget(self._field_label("Destination File"))
        self.merge_out = QLineEdit()
        self.merge_out.setPlaceholderText("Default: merged.pdf next to the first source file")
        browse = QPushButton("Browse…")
        browse.clicked.connect(lambda: self._browse_save(self.merge_out, "PDF Files (*.pdf)"))
        hbox = QHBoxLayout()
        hbox.addWidget(self.merge_out, 1)
        hbox.addWidget(browse)
        layout.addLayout(hbox)

        btn = self._primary_button(
            "  Merge PDFs Now", "merge",
            lambda: self._emit("merge", lambda: {
                "output_path": Path(self.merge_out.text().strip()) if self.merge_out.text().strip() else None
            })
        )
        layout.addSpacing(10)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_split_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Split Settings"))
        form = QFormLayout()
        form.setSpacing(12)
        self.split_every = QSpinBox()
        self.split_every.setRange(1, 1000)
        self.split_every.setValue(1)
        self.split_every.setSuffix(" page(s)")
        form.addRow("Pages per chunk:", self.split_every)

        self.split_outdir = QLineEdit()
        self.split_outdir.setPlaceholderText("Output folder (default: same folder as source)")
        browse = QPushButton("Browse…")
        browse.clicked.connect(lambda: self._browse_dir(self.split_outdir))
        hbox = QHBoxLayout()
        hbox.addWidget(self.split_outdir, 1)
        hbox.addWidget(browse)
        form.addRow("Output folder:", hbox)
        layout.addLayout(form)

        btn = self._primary_button(
            "  Split PDF", "split",
            lambda: self._emit("split", lambda: {
                "every": self.split_every.value(),
                "output_dir": Path(self.split_outdir.text().strip()) if self.split_outdir.text().strip() else None
            })
        )
        layout.addSpacing(10)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_rotate_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Rotation Settings"))
        form = QFormLayout()
        form.setSpacing(12)
        self.rotate_degrees = QComboBox()
        self.rotate_degrees.addItems(["90°", "180°", "270°"])
        form.addRow("Rotation angle:", self.rotate_degrees)

        self.rotate_pages = QLineEdit()
        self.rotate_pages.setPlaceholderText("e.g. 1,3,5-8  (leave blank to rotate all pages)")
        form.addRow("Pages to rotate:", self.rotate_pages)
        layout.addLayout(form)

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Presets:"))
        for deg in ("90°", "180°", "270°"):
            p_btn = QPushButton(deg)
            p_btn.setObjectName("PresetBtn")
            p_btn.clicked.connect(lambda _, d=deg: self.rotate_degrees.setCurrentText(d))
            preset_row.addWidget(p_btn)
        preset_row.addStretch()
        layout.addLayout(preset_row)

        btn = self._primary_button(
            "  Rotate Pages", "rotate",
            lambda: self._emit("rotate", lambda: {
                "degrees": int(self.rotate_degrees.currentText().replace("°", "")),
                "page_indices": _parse_page_list(self.rotate_pages.text(), self._page_count),
            })
        )
        layout.addSpacing(10)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_reorder_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Page Sequence"))
        layout.addWidget(self._field_label("New 1-based page order"))
        self.reorder_order = QLineEdit()
        self.reorder_order.setPlaceholderText("e.g. 3,1,2,4")
        layout.addWidget(self.reorder_order)
        layout.addWidget(self._hint(
            "Enter comma-separated page numbers. Omitted pages will be dropped. "
            "Leave blank to keep original sequence."
        ))

        btn = self._primary_button(
            "  Apply Reorder", "reorder",
            lambda: self._emit("reorder", lambda: {
                "new_order": _parse_page_list(self.reorder_order.text(), self._page_count),
            })
        )
        layout.addSpacing(10)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_watermark_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Watermark Text"))
        form = QFormLayout()
        form.setSpacing(12)
        self.wm_text = QLineEdit()
        self.wm_text.setPlaceholderText("CONFIDENTIAL")
        form.addRow("Text string:", self.wm_text)

        preset_row = QHBoxLayout()
        for word in ("CONFIDENTIAL", "DRAFT", "COPY", "APPROVED"):
            p_btn = QPushButton(word)
            p_btn.setObjectName("PresetBtn")
            p_btn.clicked.connect(lambda _, txt=word: self.wm_text.setText(txt))
            preset_row.addWidget(p_btn)
        preset_row.addStretch()
        form.addRow("Presets:", preset_row)

        layout.addWidget(self._section_header("Appearance"))
        form2 = QFormLayout()
        form2.setSpacing(12)
        self.wm_opacity = QDoubleSpinBox()
        self.wm_opacity.setRange(0.1, 1.0)
        self.wm_opacity.setSingleStep(0.05)
        self.wm_opacity.setValue(0.3)
        form2.addRow("Opacity (0.1 - 1.0):", self.wm_opacity)

        self.wm_size = QSpinBox()
        self.wm_size.setRange(12, 200)
        self.wm_size.setValue(48)
        self.wm_size.setSuffix(" pt")
        form2.addRow("Font size:", self.wm_size)
        layout.addLayout(form)
        layout.addLayout(form2)

        def params():
            if not self.wm_text.text().strip():
                raise ValueError("Enter the watermark text first.")
            return {
                "text": self.wm_text.text(),
                "opacity": self.wm_opacity.value(),
                "font_size": self.wm_size.value(),
            }

        btn = self._primary_button(
            "  Add Watermark", "watermark",
            lambda: self._emit("add_watermark", params)
        )
        layout.addSpacing(10)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_encrypt_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Passwords & Protection"))
        form = QFormLayout()
        form.setSpacing(12)
        self.enc_user_pw = QLineEdit()
        self.enc_user_pw.setEchoMode(QLineEdit.Password)
        self.enc_user_pw.setPlaceholderText("User password (required to open)")
        form.addRow("User Password:", self.enc_user_pw)

        self.enc_owner_pw = QLineEdit()
        self.enc_owner_pw.setEchoMode(QLineEdit.Password)
        self.enc_owner_pw.setPlaceholderText("Owner password (defaults to user password)")
        form.addRow("Owner Password:", self.enc_owner_pw)

        self.enc_perms = QComboBox()
        self.enc_perms.addItems([
            "Strict: View only (printing and copying denied)",
            "Allow printing only",
            "Full access: Allow printing and editing",
        ])
        self.enc_perms.setCurrentIndex(2)
        form.addRow("Permissions:", self.enc_perms)
        layout.addLayout(form)
        layout.addWidget(self._hint(
            "Encrypts document with standard AES-256 encryption. Keep your password safely recorded."
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

        btn = self._primary_button(
            "  Encrypt PDF", "encrypt",
            lambda: self._emit("encrypt", params)
        )
        layout.addSpacing(10)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_decrypt_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Decryption Password"))
        form = QFormLayout()
        form.setSpacing(12)
        self.dec_pw = QLineEdit()
        self.dec_pw.setEchoMode(QLineEdit.Password)
        self.dec_pw.setPlaceholderText("Enter password (leave blank if already unlocked)")
        form.addRow("Current Password:", self.dec_pw)
        layout.addLayout(form)
        layout.addWidget(self._hint(
            "Permanently removes security locks and exports an unencrypted document."
        ))

        btn = self._primary_button(
            "  Decrypt PDF", "decrypt",
            lambda: self._emit("decrypt", lambda: {
                "password": self.dec_pw.text()
            })
        )
        layout.addSpacing(10)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_compress_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Optimization & Quality"))
        form = QFormLayout()
        form.setSpacing(12)
        self.comp_quality = QSpinBox()
        self.comp_quality.setRange(10, 100)
        self.comp_quality.setValue(75)
        self.comp_quality.setSuffix(" %")
        form.addRow("Image quality:", self.comp_quality)

        preset_row = QHBoxLayout()
        for label, val in (("High (85%)", 85), ("Balanced (75%)", 75), ("Max Compression (50%)", 50)):
            p_btn = QPushButton(label)
            p_btn.setObjectName("PresetBtn")
            p_btn.clicked.connect(lambda _, v=val: self.comp_quality.setValue(v))
            preset_row.addWidget(p_btn)
        preset_row.addStretch()
        form.addRow("Presets:", preset_row)
        layout.addLayout(form)

        layout.addWidget(self._hint(
            "Downsamples high-DPI images to 150 DPI and applies lossless deflate stream compression. "
            "Cleans up unreferenced fonts and redundant PDF objects."
        ))

        btn = self._primary_button(
            "  Compress PDF", "compress",
            lambda: self._emit("compress", lambda: {
                "quality": self.comp_quality.value()
            })
        )
        layout.addSpacing(10)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_to_images_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Image Export Settings"))
        form = QFormLayout()
        form.setSpacing(12)
        self.img_dpi = QSpinBox()
        self.img_dpi.setRange(72, 600)
        self.img_dpi.setValue(200)
        self.img_dpi.setSuffix(" DPI")
        form.addRow("Resolution:", self.img_dpi)

        self.img_format = QComboBox()
        self.img_format.addItems(["PNG", "JPG"])
        form.addRow("Image format:", self.img_format)

        self.img_outdir = QLineEdit()
        self.img_outdir.setPlaceholderText("Output folder (default: same folder as source)")
        browse = QPushButton("Browse…")
        browse.clicked.connect(lambda: self._browse_dir(self.img_outdir))
        hbox = QHBoxLayout()
        hbox.addWidget(self.img_outdir, 1)
        hbox.addWidget(browse)
        form.addRow("Output folder:", hbox)
        layout.addLayout(form)

        btn = self._primary_button(
            "  Export Images", "to_images",
            lambda: self._emit("to_images", lambda: {
                "dpi": self.img_dpi.value(),
                "fmt": self.img_format.currentText().lower(),
                "output_dir": Path(self.img_outdir.text().strip()) if self.img_outdir.text().strip() else None
            })
        )
        layout.addSpacing(10)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_images_to_pdf_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Queued Source Images"))
        self.img_list = QListWidget()
        self.img_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.img_list.model().rowsInserted.connect(self._update_panel_state)
        self.img_list.model().rowsRemoved.connect(self._update_panel_state)
        self.img_list.setMaximumHeight(140)
        layout.addWidget(self.img_list)

        btns = QHBoxLayout()
        add_btn = QPushButton("+ Add Images…")
        add_btn.clicked.connect(self._add_images)
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("Ghost")
        clear_btn.clicked.connect(self.img_list.clear)
        btns.addWidget(add_btn)
        btns.addWidget(clear_btn)
        btns.addStretch()
        layout.addLayout(btns)

        layout.addWidget(self._section_header("Output File"))
        self.img2pdf_out = QLineEdit()
        self.img2pdf_out.setPlaceholderText("Default: output.pdf in the first image's folder")
        browse = QPushButton("Browse…")
        browse.clicked.connect(lambda: self._browse_save(self.img2pdf_out, "PDF Files (*.pdf)"))
        hbox = QHBoxLayout()
        hbox.addWidget(self.img2pdf_out, 1)
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
            "  Create PDF from Images", "images_to_pdf",
            lambda: self._emit("images_to_pdf", params),
            requirement="images"
        )
        layout.addSpacing(10)
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
