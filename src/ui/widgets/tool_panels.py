from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout,
    QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QSlider,
    QSpinBox, QStackedWidget, QVBoxLayout, QWidget
)

from src.core.models import PdfFile
from src.core.pdf_engine import PERM_ALL, PERM_PRINT
from src.ui.icons import get_icon, get_pixmap
from src.ui.theme import (
    ACCENT, ACCENT2, BG_1, BG_2, BG_3, BORDER, BORDER_STRONG, DANGER, SUCCESS,
    TEXT, TEXT_FAINT, TEXT_MUTED, WARN
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
        layout.setContentsMargins(22, 18, 22, 22)
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

        self.empty = QLabel("Select a tool from the sidebar navigation")
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
        lbl.setStyleSheet(f"color:{TEXT};font-size:12px;font-weight:600;letter-spacing:-0.1px;")
        return lbl

    def _hint(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:12px;line-height:18px;")
        lbl.setWordWrap(True)
        return lbl

    def _section_header(self, title: str) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 10, 0, 4)
        v.setSpacing(6)

        lbl = QLabel(title)
        lbl.setStyleSheet(f"color:{TEXT};font-size:13px;font-weight:600;letter-spacing:-0.2px;")
        v.addWidget(lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
        v.addWidget(sep)
        return w

    def _info_banner(self, text: str, icon_name: str = "pdf") -> QFrame:
        banner = QFrame()
        banner.setStyleSheet(
            f"background:{BG_2};border:1px solid {BORDER};border-radius:6px;padding:8px 12px;"
        )
        hb = QHBoxLayout(banner)
        hb.setContentsMargins(4, 2, 4, 2)
        hb.setSpacing(10)
        ic = QLabel()
        ic.setPixmap(get_pixmap(icon_name, ACCENT, 18))
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:12px;font-weight:500;")
        lbl.setWordWrap(True)
        hb.addWidget(ic)
        hb.addWidget(lbl, 1)
        return banner

    # ---------- public API ----------
    def set_file(self, pdf: PdfFile | None):
        self.current_file = pdf
        self._page_count = pdf.page_count if pdf else 0
        self._update_panel_state()
        self._update_dynamic_labels()

    def show_tool(self, name: str):
        panel = self.panels.get(name.lower())
        self.stack.setCurrentWidget(panel if panel else self.empty)
        self._update_panel_state()
        self._update_dynamic_labels()

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

    def _update_dynamic_labels(self):
        """Update live calculation labels across panels when file changes."""
        # Split live label
        if hasattr(self, "split_live_label") and hasattr(self, "split_every"):
            if self.current_file and self.current_file.page_count:
                n = self.current_file.page_count
                ev = max(1, self.split_every.value())
                parts = (n + ev - 1) // ev
                self.split_live_label.setText(
                    f"Document has {n} pages → Will produce {parts} file{'s' if parts != 1 else ''}"
                )
            else:
                self.split_live_label.setText("Load a PDF to preview split chunks")

        # Reorder status label
        if hasattr(self, "reorder_info_label"):
            if self.current_file and self.current_file.page_count:
                self.reorder_info_label.setText(
                    f"Source document has {self.current_file.page_count} pages (indexed 1 to {self.current_file.page_count})"
                )
            else:
                self.reorder_info_label.setText("Load a PDF to view page indices")

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
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Merge Configuration"))
        layout.addWidget(self._info_banner(
            "Combines all documents currently loaded in the Home Library in top-to-bottom sequence. "
            "You can drag files in the library to adjust their merge order.",
            "merge"
        ))

        layout.addWidget(self._section_header("Output Destination"))
        layout.addWidget(self._field_label("Destination File"))
        self.merge_out = QLineEdit()
        self.merge_out.setPlaceholderText("Default: merged.pdf next to the first source file")
        browse = QPushButton("Browse…")
        browse.setIcon(get_icon("home", TEXT_MUTED, 14))
        browse.clicked.connect(lambda: self._browse_save(self.merge_out, "PDF Files (*.pdf)"))
        hbox = QHBoxLayout()
        hbox.addWidget(self.merge_out, 1)
        hbox.addWidget(browse)
        layout.addLayout(hbox)

        layout.addWidget(self._hint(
            "Bookmarks, page annotations, hyperlinks, and vector shapes from all files are preserved."
        ))

        btn = self._primary_button(
            "  Merge PDFs Now", "merge",
            lambda: self._emit("merge", lambda: {
                "output_path": Path(self.merge_out.text().strip()) if self.merge_out.text().strip() else None
            })
        )
        layout.addSpacing(12)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_split_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Split Strategy"))
        form = QFormLayout()
        form.setSpacing(12)

        self.split_every = QSpinBox()
        self.split_every.setRange(1, 1000)
        self.split_every.setValue(1)
        self.split_every.setSuffix(" page(s)")
        self.split_every.valueChanged.connect(lambda _: self._update_dynamic_labels())
        form.addRow("Pages per file:", self.split_every)

        self.split_live_label = QLabel("Load a PDF to preview split chunks")
        self.split_live_label.setStyleSheet(f"color:{ACCENT};font-size:12px;font-weight:600;")
        form.addRow("Projection:", self.split_live_label)

        layout.addLayout(form)

        # Quick preset buttons for chunk size
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Presets:"))
        for count in (1, 2, 5, 10):
            p_btn = QPushButton(f"{count} pg{'s' if count != 1 else ''}")
            p_btn.setObjectName("PresetBtn")
            p_btn.clicked.connect(lambda _, c=count: self.split_every.setValue(c))
            preset_row.addWidget(p_btn)
        preset_row.addStretch()
        layout.addLayout(preset_row)

        layout.addWidget(self._section_header("Output Folder"))
        self.split_outdir = QLineEdit()
        self.split_outdir.setPlaceholderText("Output folder (default: same folder as source file)")
        browse = QPushButton("Browse…")
        browse.setIcon(get_icon("home", TEXT_MUTED, 14))
        browse.clicked.connect(lambda: self._browse_dir(self.split_outdir))
        hbox = QHBoxLayout()
        hbox.addWidget(self.split_outdir, 1)
        hbox.addWidget(browse)
        layout.addLayout(hbox)

        btn = self._primary_button(
            "  Split PDF", "split",
            lambda: self._emit("split", lambda: {
                "every": self.split_every.value(),
                "output_dir": Path(self.split_outdir.text().strip()) if self.split_outdir.text().strip() else None
            })
        )
        layout.addSpacing(12)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_rotate_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Rotation Settings"))
        form = QFormLayout()
        form.setSpacing(12)
        self.rotate_degrees = QComboBox()
        self.rotate_degrees.addItems(["90°", "180°", "270°"])
        form.addRow("Rotation angle:", self.rotate_degrees)

        self.rotate_pages = QLineEdit()
        self.rotate_pages.setPlaceholderText("e.g. 1,3,5-8  (leave blank to rotate all pages)")
        form.addRow("Target pages:", self.rotate_pages)
        layout.addLayout(form)

        # Preset angles
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Angles:"))
        for deg in ("90°", "180°", "270°"):
            p_btn = QPushButton(deg)
            p_btn.setObjectName("PresetBtn")
            p_btn.clicked.connect(lambda _, d=deg: self.rotate_degrees.setCurrentText(d))
            preset_row.addWidget(p_btn)
        preset_row.addStretch()
        layout.addLayout(preset_row)

        # Quick page selector presets
        page_preset_row = QHBoxLayout()
        page_preset_row.addWidget(QLabel("Page filter:"))
        for label, val in (("All Pages", ""), ("Odd Pages", "odd"), ("Even Pages", "even"), ("First Page", "1")):
            pp_btn = QPushButton(label)
            pp_btn.setObjectName("PresetBtn")
            pp_btn.clicked.connect(lambda _, v=val: self._apply_rotate_page_preset(v))
            page_preset_row.addWidget(pp_btn)
        page_preset_row.addStretch()
        layout.addLayout(page_preset_row)

        btn = self._primary_button(
            "  Rotate Pages", "rotate",
            lambda: self._emit("rotate", lambda: {
                "degrees": int(self.rotate_degrees.currentText().replace("°", "")),
                "page_indices": _parse_page_list(self.rotate_pages.text(), self._page_count),
            })
        )
        layout.addSpacing(12)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _apply_rotate_page_preset(self, preset: str):
        if not preset:
            self.rotate_pages.setText("")
        elif preset == "odd":
            if self._page_count:
                odds = [str(i) for i in range(1, self._page_count + 1, 2)]
                self.rotate_pages.setText(",".join(odds))
        elif preset == "even":
            if self._page_count:
                evens = [str(i) for i in range(2, self._page_count + 1, 2)]
                self.rotate_pages.setText(",".join(evens))
        else:
            self.rotate_pages.setText(preset)

    def _create_reorder_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Page Sequence"))
        self.reorder_info_label = QLabel("Load a PDF to view page indices")
        self.reorder_info_label.setStyleSheet(f"color:{ACCENT};font-size:12px;font-weight:600;")
        layout.addWidget(self.reorder_info_label)

        layout.addWidget(self._field_label("New 1-based page order"))
        self.reorder_order = QLineEdit()
        self.reorder_order.setPlaceholderText("e.g. 3,1,2,4")
        layout.addWidget(self.reorder_order)

        # Quick presets for reordering
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Quick actions:"))
        rev_btn = QPushButton("Reverse Order")
        rev_btn.setObjectName("PresetBtn")
        rev_btn.clicked.connect(self._reorder_reverse)
        preset_row.addWidget(rev_btn)

        reset_btn = QPushButton("Reset Original")
        reset_btn.setObjectName("PresetBtn")
        reset_btn.clicked.connect(self._reorder_reset)
        preset_row.addWidget(reset_btn)

        drop_first = QPushButton("Drop First Page")
        drop_first.setObjectName("PresetBtn")
        drop_first.clicked.connect(self._reorder_drop_first)
        preset_row.addWidget(drop_first)

        drop_last = QPushButton("Drop Last Page")
        drop_last.setObjectName("PresetBtn")
        drop_last.clicked.connect(self._reorder_drop_last)
        preset_row.addWidget(drop_last)

        preset_row.addStretch()
        layout.addLayout(preset_row)

        layout.addWidget(self._hint(
            "Enter comma-separated page numbers. Omitted pages will be removed. "
            "Leave blank to keep the original page order."
        ))

        btn = self._primary_button(
            "  Apply Reorder", "reorder",
            lambda: self._emit("reorder", lambda: {
                "new_order": _parse_page_list(self.reorder_order.text(), self._page_count),
            })
        )
        layout.addSpacing(12)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _reorder_reverse(self):
        if self._page_count:
            self.reorder_order.setText(",".join(str(i) for i in range(self._page_count, 0, -1)))

    def _reorder_reset(self):
        if self._page_count:
            self.reorder_order.setText(",".join(str(i) for i in range(1, self._page_count + 1)))

    def _reorder_drop_first(self):
        if self._page_count > 1:
            self.reorder_order.setText(",".join(str(i) for i in range(2, self._page_count + 1)))

    def _reorder_drop_last(self):
        if self._page_count > 1:
            self.reorder_order.setText(",".join(str(i) for i in range(1, self._page_count)))

    def _create_watermark_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Watermark Text"))
        form = QFormLayout()
        form.setSpacing(12)
        self.wm_text = QLineEdit()
        self.wm_text.setPlaceholderText("CONFIDENTIAL")
        form.addRow("Text string:", self.wm_text)

        preset_row = QHBoxLayout()
        for word in ("CONFIDENTIAL", "DRAFT", "COPY", "APPROVED", "SAMPLE"):
            p_btn = QPushButton(word)
            p_btn.setObjectName("PresetBtn")
            p_btn.clicked.connect(lambda _, txt=word: self.wm_text.setText(txt))
            preset_row.addWidget(p_btn)
        preset_row.addStretch()
        form.addRow("Presets:", preset_row)

        layout.addWidget(self._section_header("Appearance & Typography"))
        form2 = QFormLayout()
        form2.setSpacing(12)

        self.wm_opacity = QDoubleSpinBox()
        self.wm_opacity.setRange(0.05, 1.0)
        self.wm_opacity.setSingleStep(0.05)
        self.wm_opacity.setValue(0.3)
        form2.addRow("Opacity (0.05 - 1.0):", self.wm_opacity)

        self.wm_size = QSpinBox()
        self.wm_size.setRange(12, 200)
        self.wm_size.setValue(48)
        self.wm_size.setSuffix(" pt")
        form2.addRow("Font size:", self.wm_size)

        layout.addLayout(form)
        layout.addLayout(form2)

        size_preset_row = QHBoxLayout()
        size_preset_row.addWidget(QLabel("Size presets:"))
        for label, s_val in (("Small (32pt)", 32), ("Medium (48pt)", 48), ("Large (72pt)", 72)):
            sp_btn = QPushButton(label)
            sp_btn.setObjectName("PresetBtn")
            sp_btn.clicked.connect(lambda _, v=s_val: self.wm_size.setValue(v))
            size_preset_row.addWidget(sp_btn)
        size_preset_row.addStretch()
        layout.addLayout(size_preset_row)

        layout.addWidget(self._hint(
            "The watermark is stamped diagonally across the center of each page at a 45° angle."
        ))

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
        layout.addSpacing(12)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_encrypt_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Passwords & Security"))
        form = QFormLayout()
        form.setSpacing(12)

        # User password with show toggle
        self.enc_user_pw = QLineEdit()
        self.enc_user_pw.setEchoMode(QLineEdit.Password)
        self.enc_user_pw.setPlaceholderText("User password (required to open document)")
        toggle_u = QPushButton("👁")
        toggle_u.setFixedSize(28, 28)
        toggle_u.setToolTip("Toggle password visibility")
        toggle_u.clicked.connect(lambda: self._toggle_echo(self.enc_user_pw))
        u_box = QHBoxLayout()
        u_box.addWidget(self.enc_user_pw, 1)
        u_box.addWidget(toggle_u)
        form.addRow("User Password:", u_box)

        # Owner password with show toggle
        self.enc_owner_pw = QLineEdit()
        self.enc_owner_pw.setEchoMode(QLineEdit.Password)
        self.enc_owner_pw.setPlaceholderText("Owner password (defaults to user password)")
        toggle_o = QPushButton("👁")
        toggle_o.setFixedSize(28, 28)
        toggle_o.setToolTip("Toggle password visibility")
        toggle_o.clicked.connect(lambda: self._toggle_echo(self.enc_owner_pw))
        o_box = QHBoxLayout()
        o_box.addWidget(self.enc_owner_pw, 1)
        o_box.addWidget(toggle_o)
        form.addRow("Owner Password:", o_box)

        self.enc_perms = QComboBox()
        self.enc_perms.addItems([
            "Strict: View only (printing and copying denied)",
            "Allow printing only",
            "Full access: Allow printing and editing",
        ])
        self.enc_perms.setCurrentIndex(2)
        form.addRow("Permissions:", self.enc_perms)
        layout.addLayout(form)

        layout.addWidget(self._info_banner(
            "Industry standard AES-256 encryption. Make sure to record the user password securely; "
            "it cannot be recovered if lost.",
            "encrypt"
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
        layout.addSpacing(12)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_decrypt_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Decryption Key"))
        form = QFormLayout()
        form.setSpacing(12)

        self.dec_pw = QLineEdit()
        self.dec_pw.setEchoMode(QLineEdit.Password)
        self.dec_pw.setPlaceholderText("Enter password (leave blank if unlocked when opening)")
        toggle_d = QPushButton("👁")
        toggle_d.setFixedSize(28, 28)
        toggle_d.clicked.connect(lambda: self._toggle_echo(self.dec_pw))
        d_box = QHBoxLayout()
        d_box.addWidget(self.dec_pw, 1)
        d_box.addWidget(toggle_d)
        form.addRow("Password:", d_box)
        layout.addLayout(form)

        layout.addWidget(self._info_banner(
            "Permanently removes AES encryption and owner restrictions, producing a clean, "
            "unlocked PDF copy.",
            "decrypt"
        ))

        btn = self._primary_button(
            "  Decrypt PDF", "decrypt",
            lambda: self._emit("decrypt", lambda: {
                "password": self.dec_pw.text()
            })
        )
        layout.addSpacing(12)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _toggle_echo(self, line_edit: QLineEdit):
        if line_edit.echoMode() == QLineEdit.Password:
            line_edit.setEchoMode(QLineEdit.Normal)
        else:
            line_edit.setEchoMode(QLineEdit.Password)

    def _create_compress_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Optimization & Quality Profile"))
        form = QFormLayout()
        form.setSpacing(12)
        self.comp_quality = QSpinBox()
        self.comp_quality.setRange(10, 100)
        self.comp_quality.setValue(75)
        self.comp_quality.setSuffix(" %")
        form.addRow("Target quality:", self.comp_quality)

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Profiles:"))
        for label, val in (("High Quality (85%)", 85), ("Balanced (75%)", 75), ("Max Compress (50%)", 50)):
            p_btn = QPushButton(label)
            p_btn.setObjectName("PresetBtn")
            p_btn.clicked.connect(lambda _, v=val: self.comp_quality.setValue(v))
            preset_row.addWidget(p_btn)
        preset_row.addStretch()
        form.addRow("", preset_row)
        layout.addLayout(form)

        layout.addWidget(self._info_banner(
            "Re-encodes embedded images above 150 DPI with lossless Deflate compression. "
            "Removes redundant metadata and unused font tables.",
            "compress"
        ))

        btn = self._primary_button(
            "  Compress PDF", "compress",
            lambda: self._emit("compress", lambda: {
                "quality": self.comp_quality.value()
            })
        )
        layout.addSpacing(12)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_to_images_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Image Rendering"))
        form = QFormLayout()
        form.setSpacing(12)
        self.img_dpi = QSpinBox()
        self.img_dpi.setRange(72, 600)
        self.img_dpi.setValue(200)
        self.img_dpi.setSuffix(" DPI")
        form.addRow("Resolution:", self.img_dpi)

        dpi_row = QHBoxLayout()
        dpi_row.addWidget(QLabel("Presets:"))
        for label, val in (("Web (72 DPI)", 72), ("Standard (150 DPI)", 150), ("Print (300 DPI)", 300)):
            d_btn = QPushButton(label)
            d_btn.setObjectName("PresetBtn")
            d_btn.clicked.connect(lambda _, v=val: self.img_dpi.setValue(v))
            dpi_row.addWidget(d_btn)
        dpi_row.addStretch()
        form.addRow("", dpi_row)

        self.img_format = QComboBox()
        self.img_format.addItems(["PNG", "JPG"])
        form.addRow("Image format:", self.img_format)
        layout.addLayout(form)

        layout.addWidget(self._section_header("Output Folder"))
        self.img_outdir = QLineEdit()
        self.img_outdir.setPlaceholderText("Output folder (default: same folder as source)")
        browse = QPushButton("Browse…")
        browse.setIcon(get_icon("home", TEXT_MUTED, 14))
        browse.clicked.connect(lambda: self._browse_dir(self.img_outdir))
        hbox = QHBoxLayout()
        hbox.addWidget(self.img_outdir, 1)
        hbox.addWidget(browse)
        layout.addLayout(hbox)

        btn = self._primary_button(
            "  Export Images", "to_images",
            lambda: self._emit("to_images", lambda: {
                "dpi": self.img_dpi.value(),
                "fmt": self.img_format.currentText().lower(),
                "output_dir": Path(self.img_outdir.text().strip()) if self.img_outdir.text().strip() else None
            })
        )
        layout.addSpacing(12)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_images_to_pdf_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._section_header("Queued Source Images"))
        self.img_list = QListWidget()
        self.img_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.img_list.model().rowsInserted.connect(self._update_panel_state)
        self.img_list.model().rowsRemoved.connect(self._update_panel_state)
        self.img_list.setMaximumHeight(140)
        layout.addWidget(self.img_list)

        btns = QHBoxLayout()
        add_btn = QPushButton("  Add Images…")
        add_btn.setIcon(get_icon("add", TEXT, 14))
        add_btn.clicked.connect(self._add_images)

        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("Ghost")
        clear_btn.setIcon(get_icon("trash", DANGER, 14))
        clear_btn.clicked.connect(self.img_list.clear)

        btns.addWidget(add_btn)
        btns.addWidget(clear_btn)
        btns.addStretch()
        layout.addLayout(btns)

        layout.addWidget(self._section_header("Output File"))
        self.img2pdf_out = QLineEdit()
        self.img2pdf_out.setPlaceholderText("Default: output.pdf in the first image's folder")
        browse = QPushButton("Browse…")
        browse.setIcon(get_icon("home", TEXT_MUTED, 14))
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
        layout.addSpacing(12)
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
