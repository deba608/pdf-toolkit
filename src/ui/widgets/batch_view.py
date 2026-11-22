"""Batch processing view — apply one operation to many PDFs."""
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox,
    QProgressBar, QPushButton, QSpinBox, QStackedWidget, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget
)

from src.core.models import PdfFile
from src.core.pdf_engine import PdfEngine
from src.ui.icons import get_icon
from src.ui.theme import (
    ACCENT, BORDER, BORDER_SUBTLE, CANVAS, CANVAS_ALT, CANVAS_ELV, CANVAS_SOFT,
    DANGER, ON_PRIMARY, PRIMARY, RADIUS_LG, RADIUS_MD, SUCCESS, TEXT,
    TEXT_1, TEXT_2, TEXT_3, TEXT_FAINT, TEXT_MUTED
)

# (key, label, description)
BATCH_OPS = [
    ("compress",  "Compress",         "Losslessly clean and recompress every PDF in the queue."),
    ("rotate",    "Rotate pages",     "Rotate selected pages by 90° / 180° / 270°."),
    ("watermark", "Add watermark",    "Stamp text diagonally across every page of every PDF."),
    ("encrypt",   "Encrypt",          "Add AES-256 password and permissions to every PDF."),
    ("decrypt",   "Decrypt",          "Remove password protection from every PDF."),
    ("to_images", "Export to images", "Render every page of every PDF as PNG or JPG."),
    ("split",     "Split",            "Split every PDF into N-page chunks."),
]


class _Signals(QObject):
    one_done = Signal(int, object)
    one_error = Signal(int, str)
    all_done = Signal()


class _BatchRunner(QRunnable):
    def __init__(self, signals: _Signals, jobs: list):
        super().__init__()
        self.signals = signals
        self.jobs = jobs

    def run(self):
        for row, fn in self.jobs:
            try:
                result = fn()
                self.signals.one_done.emit(row, result)
            except Exception as e:
                self.signals.one_error.emit(row, str(e))
        self.signals.all_done.emit()


class BatchView(QWidget):
    """Batch processing panel. Call set_files(list[PdfFile]) when the library changes."""

    status_message = Signal(str, int)
    files_produced = Signal(list)

    STATUS_PENDING = "Pending"
    STATUS_RUNNING = "Running…"
    STATUS_DONE = "✔ Done"
    STATUS_ERROR = "✖ Error"

    def __init__(self):
        super().__init__()
        self._files: list[PdfFile] = []
        self._running = False
        self._results: list[PdfFile] = []
        self._signals = _Signals()
        self._signals.one_done.connect(self._on_one_done)
        self._signals.one_error.connect(self._on_one_error)
        self._signals.all_done.connect(self._on_all_done)
        self._build()

    # ---------- API ----------
    def set_files(self, files: list[PdfFile]):
        if self._running:
            return
        self._files = list(files)
        self._refresh_table()

    # ---------- UI ----------
    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(14)

        # Top card: operation picker + params
        top = self._card()
        tv = QVBoxLayout(top)
        tv.setContentsMargins(18, 16, 18, 16)
        tv.setSpacing(12)

        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(self._field_label("Operation"))
        self.op_combo = QComboBox()
        for key, label, _ in BATCH_OPS:
            self.op_combo.addItem(label, key)
        self.op_combo.currentIndexChanged.connect(self._on_op_changed)
        self.op_combo.setMinimumWidth(220)
        row.addWidget(self.op_combo)
        row.addStretch()
        tv.addLayout(row)

        self.op_desc = QLabel()
        self.op_desc.setWordWrap(True)
        self.op_desc.setStyleSheet(f"color:{TEXT_MUTED};font-size:12px;line-height:16px;")
        tv.addWidget(self.op_desc)

        self.param_stack = QStackedWidget()
        self._build_param_panels()
        tv.addWidget(self.param_stack)

        # Output folder row
        out_row = QHBoxLayout()
        out_row.setSpacing(8)
        out_row.addWidget(self._field_label("Output folder"))
        self.out_dir = QLineEdit()
        self.out_dir.setPlaceholderText("Default: same folder as each source file")
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse_out)
        out_row.addWidget(self.out_dir, 1)
        out_row.addWidget(browse)
        tv.addLayout(out_row)

        outer.addWidget(top)

        # Files table card
        files_card = self._card()
        fv = QVBoxLayout(files_card)
        fv.setContentsMargins(18, 16, 18, 16)
        fv.setSpacing(10)

        head = QHBoxLayout()
        title = QLabel("Execution Queue")
        title.setStyleSheet(f"font-size:15px;font-weight:600;color:{TEXT_1};")
        head.addWidget(title)
        self.count_label = QLabel("0 files")
        self.count_label.setStyleSheet(f"color:{TEXT_2};font-size:12px;margin-left:4px;")
        head.addWidget(self.count_label)
        head.addStretch()
        reset_btn = QPushButton("Reset status")
        reset_btn.setObjectName("Ghost")
        reset_btn.clicked.connect(self._reset_statuses)
        head.addWidget(reset_btn)
        fv.addLayout(head)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["File Name", "Pages", "Status"])
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(False)
        self.tree.setFrameShape(QFrame.NoFrame)
        self.tree.setStyleSheet(
            f"QTreeWidget{{background:{CANVAS_ALT};border:1px solid {BORDER_SUBTLE};border-radius:6px;}}"
            "QTreeWidget::item{padding:6px 6px;}"
            f"QHeaderView::section{{background:{CANVAS_ALT};color:{TEXT_2};"
            f"padding:7px 10px;border:none;border-bottom:1px solid {BORDER_SUBTLE};font-weight:600;}}"
        )
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        fv.addWidget(self.tree, 1)

        # Action row
        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        action_row.addWidget(self.progress, 1)

        self.run_btn = QPushButton("  Run batch")
        self.run_btn.setObjectName("Primary")
        self.run_btn.setIcon(get_icon("batch", "#ffffff", 14))
        self.run_btn.setMinimumHeight(38)
        self.run_btn.clicked.connect(self._run)
        action_row.addWidget(self.run_btn)
        fv.addLayout(action_row)

        outer.addWidget(files_card, 1)

        self._on_op_changed(0)
        self._refresh_table()

    def _card(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet(
            f"QFrame{{background:{CANVAS_ELV};border:1px solid {BORDER_SUBTLE};border-radius:{RADIUS_LG}px;}}"
        )
        return f

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{TEXT_1};font-size:12px;font-weight:500;")
        return lbl

    def _build_param_panels(self):
        # compress
        p = QWidget()
        f = QFormLayout(p)
        f.setSpacing(10)
        f.setContentsMargins(0, 0, 0, 0)
        self.p_compress_quality = QSpinBox()
        self.p_compress_quality.setRange(10, 100)
        self.p_compress_quality.setValue(75)
        self.p_compress_quality.setSuffix(" %")
        f.addRow("Image quality:", self.p_compress_quality)
        self.param_stack.addWidget(p)

        # rotate
        p = QWidget()
        f = QFormLayout(p)
        f.setSpacing(10)
        f.setContentsMargins(0, 0, 0, 0)
        self.p_rotate_deg = QComboBox()
        self.p_rotate_deg.addItems(["90°", "180°", "270°"])
        f.addRow("Rotation:", self.p_rotate_deg)
        self.p_rotate_pages = QLineEdit()
        self.p_rotate_pages.setPlaceholderText("e.g. 1,3,5-8  (blank = all pages)")
        f.addRow("Pages:", self.p_rotate_pages)
        self.param_stack.addWidget(p)

        # watermark
        p = QWidget()
        f = QFormLayout(p)
        f.setSpacing(10)
        f.setContentsMargins(0, 0, 0, 0)
        self.p_wm_text = QLineEdit()
        self.p_wm_text.setPlaceholderText("CONFIDENTIAL")
        f.addRow("Text string:", self.p_wm_text)
        self.p_wm_opacity = QDoubleSpinBox()
        self.p_wm_opacity.setRange(0.1, 1.0)
        self.p_wm_opacity.setSingleStep(0.05)
        self.p_wm_opacity.setValue(0.3)
        f.addRow("Opacity:", self.p_wm_opacity)
        self.p_wm_size = QSpinBox()
        self.p_wm_size.setRange(12, 200)
        self.p_wm_size.setValue(48)
        self.p_wm_size.setSuffix(" pt")
        f.addRow("Font size:", self.p_wm_size)
        self.param_stack.addWidget(p)

        # encrypt
        p = QWidget()
        f = QFormLayout(p)
        f.setSpacing(10)
        f.setContentsMargins(0, 0, 0, 0)
        self.p_enc_user = QLineEdit()
        self.p_enc_user.setEchoMode(QLineEdit.Password)
        self.p_enc_user.setPlaceholderText("User password (required)")
        f.addRow("User password:", self.p_enc_user)
        self.p_enc_owner = QLineEdit()
        self.p_enc_owner.setEchoMode(QLineEdit.Password)
        self.p_enc_owner.setPlaceholderText("Owner password (optional)")
        f.addRow("Owner password:", self.p_enc_owner)
        self.param_stack.addWidget(p)

        # decrypt
        p = QWidget()
        f = QFormLayout(p)
        f.setSpacing(10)
        f.setContentsMargins(0, 0, 0, 0)
        self.p_dec_pw = QLineEdit()
        self.p_dec_pw.setEchoMode(QLineEdit.Password)
        self.p_dec_pw.setPlaceholderText("Shared password (or leave blank if stored on each file)")
        f.addRow("Password:", self.p_dec_pw)
        self.param_stack.addWidget(p)

        # to_images
        p = QWidget()
        f = QFormLayout(p)
        f.setSpacing(10)
        f.setContentsMargins(0, 0, 0, 0)
        self.p_img_dpi = QSpinBox()
        self.p_img_dpi.setRange(72, 600)
        self.p_img_dpi.setValue(200)
        self.p_img_dpi.setSuffix(" DPI")
        f.addRow("Resolution:", self.p_img_dpi)
        self.p_img_fmt = QComboBox()
        self.p_img_fmt.addItems(["PNG", "JPG"])
        f.addRow("Format:", self.p_img_fmt)
        self.param_stack.addWidget(p)

        # split
        p = QWidget()
        f = QFormLayout(p)
        f.setSpacing(10)
        f.setContentsMargins(0, 0, 0, 0)
        self.p_split_every = QSpinBox()
        self.p_split_every.setRange(1, 1000)
        self.p_split_every.setValue(1)
        self.p_split_every.setSuffix(" pages")
        f.addRow("Pages per chunk:", self.p_split_every)
        self.param_stack.addWidget(p)

    # ---------- Handlers ----------
    def _on_op_changed(self, idx: int):
        key = self.op_combo.currentData()
        for i, (k, _label, desc) in enumerate(BATCH_OPS):
            if k == key:
                self.op_desc.setText(desc)
                self.param_stack.setCurrentIndex(i)
                break

    def _browse_out(self):
        path = QFileDialog.getExistingDirectory(self, "Select output folder")
        if path:
            self.out_dir.setText(path)

    def _refresh_table(self):
        self.tree.clear()
        for pdf in self._files:
            item = QTreeWidgetItem([
                pdf.name,
                str(pdf.page_count),
                self.STATUS_PENDING,
            ])
            item.setIcon(0, get_icon("pdf", PRIMARY, 16))
            item.setToolTip(0, str(pdf.path))
            item.setForeground(2, QBrush(QColor(TEXT_MUTED)))
            self.tree.addTopLevelItem(item)
        n = len(self._files)
        self.count_label.setText(f"{n} file{'s' if n != 1 else ''}")
        self.run_btn.setEnabled(n > 0 and not self._running)
        self.progress.setValue(0)
        self.progress.setMaximum(max(1, n))

    def _reset_statuses(self):
        for i in range(self.tree.topLevelItemCount()):
            it = self.tree.topLevelItem(i)
            it.setText(2, self.STATUS_PENDING)
            it.setToolTip(2, "")
            it.setForeground(2, QBrush(QColor(TEXT_MUTED)))
        self.progress.setValue(0)

    # ---------- Execution ----------
    def _run(self):
        if self._running or not self._files:
            return

        key = self.op_combo.currentData()
        try:
            jobs = self._prepare_jobs(key)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid parameters", str(e))
            return

        self._running = True
        self._results = []
        self.run_btn.setEnabled(False)
        self.run_btn.setText("Running…")
        self.progress.setMaximum(len(jobs))
        self.progress.setValue(0)
        for row, _ in jobs:
            item = self.tree.topLevelItem(row)
            item.setText(2, self.STATUS_PENDING)
            item.setToolTip(2, "")
            item.setForeground(2, QBrush(QColor(TEXT_MUTED)))

        if jobs:
            self.tree.topLevelItem(jobs[0][0]).setText(2, self.STATUS_RUNNING)
            self.tree.topLevelItem(jobs[0][0]).setForeground(2, QBrush(QColor(ACCENT)))

        self._pending_rows = [r for r, _ in jobs]
        runner = _BatchRunner(self._signals, jobs)
        QThreadPool.globalInstance().start(runner)
        self.status_message.emit(f"Running batch on {len(jobs)} files…", 0)

    def _prepare_jobs(self, key: str) -> list[tuple[int, callable]]:
        out_dir_text = self.out_dir.text().strip()
        out_dir = Path(out_dir_text) if out_dir_text else None
        if out_dir:
            out_dir.mkdir(parents=True, exist_ok=True)

        jobs = []
        for row, pdf in enumerate(self._files):
            jobs.append((row, self._make_job(key, pdf, out_dir)))
        return jobs

    def _make_job(self, key: str, pdf: PdfFile, out_dir: Path | None):
        def _out_path(suffix: str, ext: str = ".pdf") -> Path:
            base = out_dir if out_dir else pdf.path.parent
            return base / f"{pdf.path.stem}_{suffix}{ext}"

        if key == "compress":
            q = self.p_compress_quality.value()
            return lambda: PdfEngine.compress(pdf, output_path=_out_path("compressed"), quality=q)

        if key == "rotate":
            from src.ui.widgets.tool_panels import _parse_page_list
            deg = int(self.p_rotate_deg.currentText().replace("°", ""))
            pages_text = self.p_rotate_pages.text()
            return lambda: PdfEngine.rotate(
                pdf,
                page_indices=_parse_page_list(pages_text, pdf.page_count),
                degrees=deg,
                output_path=_out_path("rotated"),
            )

        if key == "watermark":
            text = self.p_wm_text.text()
            if not text.strip():
                raise ValueError("Watermark text cannot be empty.")
            op, size = self.p_wm_opacity.value(), self.p_wm_size.value()
            return lambda: PdfEngine.add_watermark(
                pdf, text=text, opacity=op, font_size=size, output_path=_out_path("watermarked"),
            )

        if key == "encrypt":
            user = self.p_enc_user.text()
            if not user:
                raise ValueError("User password is required for encryption.")
            owner = self.p_enc_owner.text() or None
            return lambda: PdfEngine.encrypt(
                pdf, user_password=user, owner_password=owner, output_path=_out_path("encrypted"),
            )

        if key == "decrypt":
            pw = self.p_dec_pw.text()
            return lambda: PdfEngine.decrypt(pdf, password=pw, output_path=_out_path("decrypted"))

        if key == "to_images":
            dpi = self.p_img_dpi.value()
            fmt = self.p_img_fmt.currentText().lower()
            d = out_dir if out_dir else pdf.path.parent
            return lambda: PdfEngine.to_images(pdf, output_dir=d, dpi=dpi, fmt=fmt)

        if key == "split":
            every = self.p_split_every.value()
            d = out_dir if out_dir else pdf.path.parent
            return lambda: PdfEngine.split_by_pages(pdf, every=every, output_dir=d)

        raise ValueError(f"Unknown operation: {key}")

    def _on_one_done(self, row: int, result):
        item = self.tree.topLevelItem(row)
        if item:
            item.setText(2, self.STATUS_DONE)
            item.setForeground(2, QBrush(QColor(SUCCESS)))
        if isinstance(result, PdfFile):
            self._results.append(result)
        elif isinstance(result, list):
            self._results.extend(r for r in result if isinstance(r, PdfFile))
        self._advance_progress(row)

    def _on_one_error(self, row: int, msg: str):
        item = self.tree.topLevelItem(row)
        if item:
            item.setText(2, self.STATUS_ERROR)
            item.setToolTip(2, msg)
            item.setForeground(2, QBrush(QColor(DANGER)))
        self._advance_progress(row)

    def _advance_progress(self, row: int):
        self.progress.setValue(self.progress.value() + 1)
        if self._pending_rows:
            try:
                self._pending_rows.remove(row)
            except ValueError:
                pass
            if self._pending_rows:
                nxt = self._pending_rows[0]
                nxt_item = self.tree.topLevelItem(nxt)
                if nxt_item and nxt_item.text(2) == self.STATUS_PENDING:
                    nxt_item.setText(2, self.STATUS_RUNNING)
                    nxt_item.setForeground(2, QBrush(QColor(ACCENT)))

    def _on_all_done(self):
        self._running = False
        self.run_btn.setEnabled(len(self._files) > 0)
        self.run_btn.setText("Run batch")
        ok = sum(1 for i in range(self.tree.topLevelItemCount())
                 if self.tree.topLevelItem(i).text(2) == self.STATUS_DONE)
        err = sum(1 for i in range(self.tree.topLevelItemCount())
                  if self.tree.topLevelItem(i).text(2) == self.STATUS_ERROR)
        self.status_message.emit(f"Batch finished — {ok} succeeded, {err} failed", 5000)
        if self._results:
            self.files_produced.emit(list(self._results))
            self._results = []
