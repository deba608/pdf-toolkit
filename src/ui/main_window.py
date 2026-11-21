from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QProgressBar, QListWidget, QListWidgetItem,
    QSplitter, QStatusBar, QInputDialog, QLineEdit, QStackedWidget,
    QFrame, QSizePolicy, QScrollArea
)
from PySide6.QtGui import QAction, QIcon, QDragEnterEvent, QDropEvent, QPixmap
from PySide6.QtCore import Qt, QThreadPool, QRunnable, Signal, QObject, QSize

from src.core.models import PdfFile
from src.core.pdf_engine import PdfEngine
from src.ui.widgets.file_list import FileListWidget
from src.ui.widgets.preview import PreviewWidget
from src.ui.widgets.tool_panels import ToolPanelsStack
from src.ui.widgets.batch_view import BatchView


class WorkerSignals(QObject):
    progress = Signal(int)
    finished = Signal(object)
    error = Signal(str)


class PdfWorker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))


# Sidebar nav items: (key, label, icon-text, section, description)
# key "home" = file manager; "images to pdf" has no selected file requirement
NAV_ITEMS = [
    ("home",          "Home",           "⌂",  "Library",   "Open and manage PDFs"),
    # Tools
    ("merge",         "Merge",          "☰",  "Tools",     "Combine multiple PDFs"),
    ("split",         "Split",          "✂",  "Tools",     "Split a PDF into parts"),
    ("rotate",        "Rotate",         "↻",  "Tools",     "Rotate pages 90/180/270"),
    ("reorder",       "Reorder",        "⇅",  "Tools",     "Rearrange page order"),
    ("watermark",     "Watermark",      "❖",  "Tools",     "Add text watermark"),
    ("compress",      "Compress",       "↓",  "Tools",     "Reduce file size"),
    # Security
    ("encrypt",       "Encrypt",        "\U0001F512", "Security", "Password-protect a PDF"),
    ("decrypt",       "Decrypt",        "\U0001F513", "Security", "Remove password"),
    # Convert
    ("to images",     "PDF → Images", "⇒", "Convert",  "Export pages as PNG/JPG"),
    ("images to pdf", "Images → PDF", "⇐", "Convert",  "Build PDF from images"),
    # Batch
    ("batch",         "Batch run",      "⧉",  "Automation", "Apply one operation to all loaded PDFs"),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Toolkit")
        self.resize(1280, 820)
        self.setMinimumSize(1024, 680)
        self.setAcceptDrops(True)

        icon_path = Path(__file__).parent.parent / "resources" / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.thread_pool = QThreadPool.globalInstance()
        self.current_file: PdfFile | None = None
        self.files: list[PdfFile] = []
        # Hold PdfWorker instances alive until their signals have been dispatched.
        # QRunnable auto-deletes after run() returns, which can destroy the
        # WorkerSignals QObject before Qt delivers the queued finished signal
        # for fast operations — the callback then silently never fires.
        self._active_workers: set = set()

        self._build_ui()
        self._setup_menu()
        self._setup_statusbar()
        self._update_header()

        # Default to Home
        self.sidebar.setCurrentRow(0)

    # ---------- Layout ----------
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        hroot = QHBoxLayout(root)
        hroot.setContentsMargins(0, 0, 0, 0)
        hroot.setSpacing(0)

        # Sidebar
        hroot.addWidget(self._build_sidebar())

        # Main pane: header + content
        main = QWidget()
        mv = QVBoxLayout(main)
        mv.setContentsMargins(0, 0, 0, 0)
        mv.setSpacing(0)
        mv.addWidget(self._build_header())
        mv.addWidget(self._build_content(), 1)
        hroot.addWidget(main, 1)

    def _build_sidebar(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(240)
        v = QVBoxLayout(panel)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        title = QLabel("PDF Toolkit")
        title.setObjectName("SidebarTitle")
        v.addWidget(title)

        sub = QLabel("Offline · Private · Fast")
        sub.setObjectName("SidebarSubtitle")
        v.addWidget(sub)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFrameShape(QFrame.NoFrame)
        self.sidebar.setSpacing(0)
        self.sidebar.setIconSize(QSize(16, 16))
        self.sidebar.currentRowChanged.connect(self._on_nav_changed)

        current_section = None
        self._nav_row_to_key: list[str] = []
        for key, label, glyph, section, desc in NAV_ITEMS:
            if section != current_section:
                header_item = QListWidgetItem(section)
                header_item.setFlags(Qt.NoItemFlags)
                header_item.setData(Qt.UserRole, "__section__")
                font = header_item.font()
                font.setBold(True)
                font.setPointSize(8)
                header_item.setFont(font)
                header_item.setForeground(Qt.gray)
                header_item.setText(f"   {section.upper()}")
                header_item.setSizeHint(QSize(0, 26))
                self.sidebar.addItem(header_item)
                self._nav_row_to_key.append("__section__")
                current_section = section

            item = QListWidgetItem(f" {glyph}   {label}")
            item.setData(Qt.UserRole, key)
            item.setToolTip(desc)
            item.setSizeHint(QSize(0, 38))
            self.sidebar.addItem(item)
            self._nav_row_to_key.append(key)

        v.addWidget(self.sidebar, 1)

        # Footer: open button
        footer = QWidget()
        fv = QVBoxLayout(footer)
        fv.setContentsMargins(12, 8, 12, 14)
        open_btn = QPushButton("  +  Open PDFs")
        open_btn.setObjectName("Primary")
        open_btn.setMinimumHeight(36)
        open_btn.clicked.connect(self._open_files)
        fv.addWidget(open_btn)
        v.addWidget(footer)

        return panel

    def _build_header(self) -> QWidget:
        h = QFrame()
        h.setObjectName("Header")
        layout = QHBoxLayout(h)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(12)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self.header_title = QLabel("Home")
        self.header_title.setObjectName("HeaderTitle")
        self.header_sub = QLabel("Open PDFs to get started")
        self.header_sub.setObjectName("HeaderSubtitle")
        text_col.addWidget(self.header_title)
        text_col.addWidget(self.header_sub)
        layout.addLayout(text_col)

        layout.addStretch()

        self.save_btn = QPushButton("Save As…")
        self.save_btn.setShortcut("Ctrl+S")
        self.save_btn.clicked.connect(self._save_current)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)

        return h

    def _build_content(self) -> QWidget:
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self._build_home_view())        # index 0
        self.content_stack.addWidget(self._build_tools_view())       # index 1
        self.content_stack.addWidget(self._build_batch_view())       # index 2
        return self.content_stack

    def _build_batch_view(self) -> QWidget:
        wrap = QWidget()
        v = QVBoxLayout(wrap)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(0)
        self.batch_view = BatchView()
        self.batch_view.status_message.connect(
            lambda msg, ms: self.status.showMessage(msg, ms)
        )
        v.addWidget(self.batch_view, 1)
        return wrap

    # ---------- Home ----------
    def _build_home_view(self) -> QWidget:
        wrap = QWidget()
        outer = QVBoxLayout(wrap)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(16)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Left: files card
        left = self._make_card()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(16, 14, 16, 16)
        lv.setSpacing(10)

        header_row = QHBoxLayout()
        title = QLabel("PDF Files")
        title.setProperty("class", "CardTitle")
        title.setStyleSheet("font-size:15px;font-weight:600;")
        header_row.addWidget(title)
        header_row.addStretch()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._open_files)
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("Ghost")
        clear_btn.clicked.connect(self._clear_files)
        header_row.addWidget(add_btn)
        header_row.addWidget(clear_btn)
        lv.addLayout(header_row)

        self.file_list = FileListWidget()
        self.file_list.file_selected.connect(self._on_file_selected)
        self.file_list.files_reordered.connect(self._on_files_reordered)
        lv.addWidget(self.file_list, 1)

        splitter.addWidget(left)

        # Right: preview card with empty state
        right = self._make_card()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(16, 14, 16, 16)
        rv.setSpacing(10)

        pv_title = QLabel("Preview")
        pv_title.setStyleSheet("font-size:15px;font-weight:600;")
        rv.addWidget(pv_title)

        self.preview_stack = QStackedWidget()
        self.preview_empty = self._build_empty_state(
            "No PDF selected",
            "Drag & drop a PDF here, or use ‘Open PDFs’ on the left."
        )
        self.preview = PreviewWidget()
        self.preview_stack.addWidget(self.preview_empty)  # 0
        self.preview_stack.addWidget(self.preview)        # 1
        rv.addWidget(self.preview_stack, 1)

        splitter.addWidget(right)
        splitter.setSizes([380, 820])
        outer.addWidget(splitter, 1)
        return wrap

    # ---------- Tools ----------
    def _build_tools_view(self) -> QWidget:
        wrap = QWidget()
        outer = QVBoxLayout(wrap)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(16)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Left: tool form in a card
        left = self._make_card()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.setSpacing(0)

        self.tool_header_title = QLabel("Tool")
        self.tool_header_title.setStyleSheet("font-size:16px;font-weight:600;padding:16px 18px 2px 18px;")
        self.tool_header_desc = QLabel("")
        self.tool_header_desc.setStyleSheet("color:#9aa1b2;font-size:12px;padding:0 18px 14px 18px;")
        self.tool_header_desc.setWordWrap(True)
        lv.addWidget(self.tool_header_title)
        lv.addWidget(self.tool_header_desc)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:#2a2f42;max-height:1px;border:none;")
        lv.addWidget(sep)

        # No-file banner
        self.no_file_banner = QLabel("No PDF loaded. Open a PDF from the Home view to use this tool.")
        self.no_file_banner.setStyleSheet(
            "color:#e5a23d;background:rgba(229,162,61,0.1);"
            "border-top:1px solid rgba(229,162,61,0.3);"
            "border-bottom:1px solid rgba(229,162,61,0.3);"
            "padding:10px 18px;"
        )
        self.no_file_banner.setVisible(False)
        lv.addWidget(self.no_file_banner)

        self.tool_panels = ToolPanelsStack()
        self.tool_panels.operation_requested.connect(self._run_operation)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(self.tool_panels)
        lv.addWidget(scroll, 1)

        splitter.addWidget(left)

        # Right: preview card
        right = self._make_card()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(16, 14, 16, 16)
        rv.setSpacing(10)

        rv.addWidget(self._section_label("Preview"))

        self.tool_preview_stack = QStackedWidget()
        self.tool_preview_empty = self._build_empty_state(
            "No PDF selected",
            "Load a PDF from the Home view to preview it here."
        )
        self.tool_preview = PreviewWidget()
        self.tool_preview_stack.addWidget(self.tool_preview_empty)
        self.tool_preview_stack.addWidget(self.tool_preview)
        rv.addWidget(self.tool_preview_stack, 1)

        splitter.addWidget(right)
        splitter.setSizes([460, 740])
        outer.addWidget(splitter, 1)
        return wrap

    # ---------- Helpers ----------
    def _make_card(self) -> QFrame:
        f = QFrame()
        f.setProperty("class", "Card")
        f.setStyleSheet("QFrame{background:#161922;border:1px solid #2a2f42;border-radius:8px;}")
        return f

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size:15px;font-weight:600;")
        return lbl

    def _build_empty_state(self, title: str, subtitle: str) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setAlignment(Qt.AlignCenter)
        v.setSpacing(8)
        icon = QLabel("□")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size:48px;color:#363c52;")
        t = QLabel(title)
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("font-size:15px;font-weight:600;color:#9aa1b2;")
        s = QLabel(subtitle)
        s.setAlignment(Qt.AlignCenter)
        s.setStyleSheet("font-size:12px;color:#6b7284;")
        s.setWordWrap(True)
        v.addStretch()
        v.addWidget(icon)
        v.addWidget(t)
        v.addWidget(s)
        v.addStretch()
        return w

    def _update_header(self):
        if not self.current_file:
            self.save_btn.setEnabled(False)
        else:
            self.save_btn.setEnabled(True)

    # ---------- Navigation ----------
    def _on_nav_changed(self, row: int):
        if row < 0 or row >= len(self._nav_row_to_key):
            return
        key = self._nav_row_to_key[row]
        if key == "__section__":
            # Skip to next non-section row
            next_row = row + 1
            if next_row < self.sidebar.count():
                self.sidebar.setCurrentRow(next_row)
            return

        label, desc = self._lookup_nav(key)
        self.header_title.setText(label)
        self.header_sub.setText(desc)

        if key == "home":
            self.content_stack.setCurrentIndex(0)
            self._refresh_preview_empty_state()
        elif key == "batch":
            self.content_stack.setCurrentIndex(2)
            self.batch_view.set_files(self.files)
        else:
            self.content_stack.setCurrentIndex(1)
            self.tool_header_title.setText(label)
            self.tool_header_desc.setText(desc)
            self.tool_panels.show_tool(key)
            self._update_tool_banner(key)
            self._refresh_tool_preview_empty_state()

    def _lookup_nav(self, key: str) -> tuple[str, str]:
        for k, label, _g, _s, desc in NAV_ITEMS:
            if k == key:
                return label, desc
        return key.title(), ""

    def _update_tool_banner(self, key: str):
        needs_file = key not in {"images to pdf"}
        self.no_file_banner.setVisible(needs_file and self.current_file is None)

    def _refresh_preview_empty_state(self):
        self.preview_stack.setCurrentIndex(1 if self.current_file else 0)

    def _refresh_tool_preview_empty_state(self):
        self.tool_preview_stack.setCurrentIndex(1 if self.current_file else 0)

    # ---------- Menu & status ----------
    def _setup_menu(self):
        mb = self.menuBar()
        file_menu = mb.addMenu("&File")
        open_a = QAction("&Open PDF(s)…", self)
        open_a.setShortcut("Ctrl+O")
        open_a.triggered.connect(self._open_files)
        file_menu.addAction(open_a)
        save_a = QAction("&Save As…", self)
        save_a.setShortcut("Ctrl+S")
        save_a.triggered.connect(self._save_current)
        file_menu.addAction(save_a)
        file_menu.addSeparator()
        exit_a = QAction("E&xit", self)
        exit_a.setShortcut("Ctrl+Q")
        exit_a.triggered.connect(self.close)
        file_menu.addAction(exit_a)

        tools_menu = mb.addMenu("&Tools")
        for key, label, *_rest in NAV_ITEMS:
            if key in {"home", "batch"}:
                continue
            a = QAction(label, self)
            a.triggered.connect(lambda _, k=key: self._nav_to(k))
            tools_menu.addAction(a)
        tools_menu.addSeparator()
        batch_a = QAction("Batch run…", self)
        batch_a.setShortcut("Ctrl+B")
        batch_a.triggered.connect(lambda: self._nav_to("batch"))
        tools_menu.addAction(batch_a)

        help_menu = mb.addMenu("&Help")
        sc = QAction("Keyboard &Shortcuts…", self)
        sc.setShortcut("F1")
        sc.triggered.connect(self._show_shortcuts)
        help_menu.addAction(sc)
        about = QAction("&About", self)
        about.triggered.connect(self._show_about)
        help_menu.addAction(about)

    def _nav_to(self, key: str):
        for row, k in enumerate(self._nav_row_to_key):
            if k == key:
                self.sidebar.setCurrentRow(row)
                return

    def _setup_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(180)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self.status.addPermanentWidget(self.progress_bar)

    # ---------- Drag & drop ----------
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = [Path(u.toLocalFile()) for u in event.mimeData().urls()
                 if u.toLocalFile().lower().endswith('.pdf')]
        if paths:
            self._load_files(paths)

    # ---------- File ops ----------
    def _open_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Open PDF Files", "", "PDF Files (*.pdf)"
        )
        if paths:
            self._load_files([Path(p) for p in paths])

    def _load_files(self, paths: list[Path]):
        first_added_row = None
        for path in paths:
            pdf = self._load_with_password(path)
            if pdf:
                if first_added_row is None:
                    first_added_row = self.file_list.list.count()
                self.files.append(pdf)
                self.file_list.add_file(pdf)
        self.batch_view.set_files(self.files)
        self._nav_to("home")
        # Auto-select the first newly added file if nothing is selected yet.
        if self.current_file is None and first_added_row is not None:
            self.file_list.list.setCurrentRow(first_added_row)

    def _load_with_password(self, path: Path):
        password = None
        for attempt in range(3):
            try:
                return PdfEngine.load(path, password)
            except ValueError as e:
                if "password" not in str(e).lower():
                    QMessageBox.warning(self, "Error", f"Failed to load {path.name}: {e}")
                    return None
                prompt = "Password required:" if attempt == 0 else "Incorrect password, try again:"
                password, ok = QInputDialog.getText(
                    self, f"Encrypted PDF — {path.name}", prompt, QLineEdit.Password
                )
                if not ok:
                    self.status.showMessage(f"Cancelled loading {path.name}", 3000)
                    return None
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load {path.name}: {e}")
                return None
        QMessageBox.warning(self, "Error", f"Too many incorrect passwords for {path.name}")
        return None

    def _clear_files(self):
        self.files.clear()
        self.file_list._clear_all()
        self.current_file = None
        self.batch_view.set_files(self.files)
        self._refresh_preview_empty_state()
        self._refresh_tool_preview_empty_state()
        self._update_header()

    def _on_file_selected(self, pdf: PdfFile):
        self.current_file = pdf
        self.preview.load_pdf(pdf)
        self.tool_preview.load_pdf(pdf)
        self.tool_panels.set_file(pdf)
        self._refresh_preview_empty_state()
        self._refresh_tool_preview_empty_state()
        # Hide no-file banner if we're on a tool
        current_key = self._current_nav_key()
        if current_key:
            self._update_tool_banner(current_key)
        self._update_header()
        self.status.showMessage(f"Loaded {pdf.name} — {pdf.page_count} pages, {pdf.size_mb:.1f} MB", 4000)

    def _on_files_reordered(self, files: list[PdfFile]):
        self.files = files
        self.batch_view.set_files(self.files)

    def _current_nav_key(self) -> str | None:
        row = self.sidebar.currentRow()
        if 0 <= row < len(self._nav_row_to_key):
            k = self._nav_row_to_key[row]
            return None if k == "__section__" else k
        return None

    # ---------- Operations ----------
    def _run_operation(self, op_name: str, params: dict):
        # Operations that act on the whole library (or need no library at all).
        multi_or_fileless = {"images_to_pdf", "merge"}
        if op_name == "merge" and not self.files:
            QMessageBox.information(self, "No files", "Add at least one PDF to merge.")
            return
        if op_name not in multi_or_fileless and not self.current_file:
            QMessageBox.information(self, "No file", "Please open a PDF first.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # busy indicator

        if op_name == "merge":
            worker = PdfWorker(PdfEngine.merge, self.files, **params)
        elif op_name == "split":
            worker = PdfWorker(PdfEngine.split_by_pages, self.current_file, **params)
        elif op_name == "images_to_pdf":
            worker = PdfWorker(PdfEngine.images_to_pdf, **params)
        else:
            worker = PdfWorker(getattr(PdfEngine, op_name), self.current_file, **params)

        worker.setAutoDelete(False)
        self._active_workers.add(worker)

        def _retire(w=worker):
            self._active_workers.discard(w)

        worker.signals.finished.connect(lambda r: (self._operation_done(r, op_name), _retire()))
        worker.signals.error.connect(lambda m: (self._operation_error(m), _retire()))
        self.thread_pool.start(worker)
        self.status.showMessage(f"Running {op_name}…")

    def _operation_done(self, result, op_name: str):
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)

        if isinstance(result, list):
            if op_name == "split":
                for pdf in result:
                    self.files.append(pdf)
                    self.file_list.add_file(pdf)
                self.batch_view.set_files(self.files)
                self.status.showMessage(f"Split into {len(result)} files", 4000)
            elif op_name == "to_images":
                self.status.showMessage(f"Exported {len(result)} images", 4000)
        else:
            # Single-file ops (compress/rotate/watermark/encrypt/decrypt/reorder/merge)
            # produce a NEW file. Add it to the library if we don't already track it,
            # then select it so the preview and next op target the fresh output.
            existing = next((f for f in self.files if f.path == result.path), None)
            if existing is None:
                self.files.append(result)
                self.file_list.add_file(result)
                self.batch_view.set_files(self.files)
            else:
                self.file_list.update_file(result)
            self.current_file = result
            # Select the output in the list (triggers _on_file_selected -> preview updates)
            for i in range(self.file_list.list.count()):
                item = self.file_list.list.item(i)
                if item.data(Qt.UserRole).path == result.path:
                    self.file_list.list.setCurrentRow(i)
                    break
            self.status.showMessage(
                f"✔  {op_name.replace('_',' ').title()} saved to {result.path.name}", 5000
            )

        self._update_header()
        self._refresh_preview_empty_state()
        self._refresh_tool_preview_empty_state()

    def _operation_error(self, msg: str):
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        QMessageBox.critical(self, "Operation failed", msg)
        self.status.showMessage(f"Error: {msg[:80]}", 5000)

    def _save_current(self):
        if not self.current_file:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", self.current_file.name, "PDF Files (*.pdf)"
        )
        if path:
            import shutil
            shutil.copy2(self.current_file.path, path)
            self.status.showMessage(f"Saved to {path}", 4000)

    # ---------- Help dialogs ----------
    def _show_about(self):
        QMessageBox.about(
            self,
            "About PDF Toolkit",
            "<h3>PDF Toolkit 1.0</h3>"
            "<p>A fast, private, offline PDF toolkit for Windows.</p>"
            "<p>Built with PySide6 and PyMuPDF.</p>"
        )

    def _show_shortcuts(self):
        rows = [
            ("Ctrl+O", "Open PDF files"),
            ("Ctrl+S", "Save current PDF"),
            ("Ctrl+Q", "Quit"),
            ("F1",     "Show this dialog"),
            ("Del",    "Remove selected file"),
            ("Drag & drop", "Add PDFs to the library"),
        ]
        html = "<table cellpadding='6'>"
        for k, d in rows:
            html += f"<tr><td><b>{k}</b></td><td>{d}</td></tr>"
        html += "</table>"
        box = QMessageBox(self)
        box.setWindowTitle("Keyboard Shortcuts")
        box.setTextFormat(Qt.RichText)
        box.setText(html)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec()
