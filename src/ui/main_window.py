import shutil
from pathlib import Path

from PySide6.QtCore import (
    QObject, QPoint, QRect, QRunnable, QSettings, Qt, QThreadPool, Signal
)
from PySide6.QtGui import (
    QAction, QCursor, QDragEnterEvent, QDropEvent, QGuiApplication, QIcon
)
from PySide6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QInputDialog, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QProgressBar, QPushButton, QStackedWidget,
    QStatusBar, QVBoxLayout, QWidget
)

from src.core.models import PdfFile
from src.core.pdf_engine import PdfEngine
from src.paths import resource_path
from src.ui.icons import get_icon
from src.ui.theme import DANGER, TEXT_MUTED
from src.ui.tool_registry import TOOLS, get_tool, pdf_tools
from src.ui.widgets.file_list import FileListWidget
from src.ui.widgets.home_view import HomeView
from src.ui.widgets.tool_session import ToolSession
from src.ui.widgets.tool_workspace import ToolWorkspace


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
            self.signals.finished.emit(self.fn(*self.args, **self.kwargs))
        except Exception as e:  # noqa: BLE001 - surfaced to user as dialog
            self.signals.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Toolkit")
        self.setAcceptDrops(True)

        icon_path = resource_path("icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.thread_pool = QThreadPool.globalInstance()
        self.files: list[PdfFile] = []
        self._current_file: PdfFile | None = None
        self.session: ToolSession | None = None
        self._busy = False
        self._active_workers: set = set()

        # Hidden compatibility library: outputs and legacy open path still live here.
        self.file_list = FileListWidget()

        self._build_ui()
        self._setup_menu()
        self._setup_statusbar()
        self._setup_geometry()
        self._update_header()
        self._go_home()

    # ---------- Responsive, screen-bounded geometry ----------
    def _setup_geometry(self):
        """Ensure window is centered and fits 100% inside the visible desktop area."""
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1280, 800)

        target_w = min(1200, max(860, int(avail.width() * 0.85)))
        target_h = min(760, max(560, int(avail.height() * 0.88)))

        self.setMinimumSize(min(760, avail.width() - 40), min(500, avail.height() - 40))
        self.resize(target_w, target_h)

        settings = QSettings("PDFToolkit", "PDFToolkit")
        saved_geom = settings.value("geometry")
        restored = False
        if saved_geom:
            self.restoreGeometry(saved_geom)
            w_rect = self.frameGeometry()
            target_screen = None
            max_inter_area = 0
            for s in QGuiApplication.screens():
                s_avail = s.availableGeometry()
                inter = s_avail.intersected(w_rect)
                area = max(0, inter.width()) * max(0, inter.height())
                if area > max_inter_area:
                    max_inter_area = area
                    target_screen = s

            w_area = max(1, w_rect.width() * w_rect.height())
            if target_screen and (max_inter_area / w_area) >= 0.90:
                avail = target_screen.availableGeometry()
                restored = True
            else:
                restored = False

        if not restored:
            self.resize(target_w, target_h)
            geo = self.frameGeometry()
            geo.moveCenter(avail.center())
            self.move(geo.topLeft())

        cur_x = self.x()
        cur_y = self.y()
        clamped_x = max(avail.left(), min(cur_x, avail.right() - self.width()))
        clamped_y = max(avail.top(), min(cur_y, avail.bottom() - self.height()))
        self.move(clamped_x, clamped_y)

    def closeEvent(self, event):
        if not self.isMaximized() and not self.isMinimized():
            settings = QSettings("PDFToolkit", "PDFToolkit")
            settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    # ---------- Layout ----------
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addWidget(self._build_header())
        v.addWidget(self._build_content(), 1)

    def _build_header(self):
        h = QFrame()
        h.setObjectName("Header")
        layout = QHBoxLayout(h)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(14)

        self.back_button = QPushButton(" Home")
        self.back_button.setObjectName("Secondary")
        self.back_button.setIcon(get_icon("home", TEXT_MUTED, 14))
        self.back_button.clicked.connect(self._go_home)

        self.header_title = QLabel("Home")
        self.header_title.setObjectName("HeaderTitle")
        self.header_sub = QLabel("Everything you need for PDFs. Fast, private, offline.")
        self.header_sub.setObjectName("HeaderSubtitle")

        layout.addWidget(self.back_button)
        layout.addWidget(self.header_title)
        layout.addWidget(self.header_sub)
        layout.addStretch()

        self.save_btn = QPushButton("Save Copy…")
        self.save_btn.clicked.connect(self._save_current)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)

        self.help_btn = QPushButton("?")
        self.help_btn.setObjectName("HelpBtn")
        self.help_btn.setFixedSize(30, 30)
        self.help_btn.setToolTip("Keyboard Shortcuts & Help (F1)")
        self.help_btn.clicked.connect(self._show_shortcuts)
        layout.addWidget(self.help_btn)

        self.back_button.setVisible(False)
        return h

    def _build_content(self):
        self.content_stack = QStackedWidget()
        self.home_view = HomeView()
        self.workspace = ToolWorkspace()

        self.home_view.toolSelected.connect(self._nav_to)
        self.home_view.filesDropped.connect(self._on_home_drop)
        self.home_view.openRequested.connect(self._open_home_files)

        self.workspace.filesAddedRequested.connect(self._on_workspace_paths)
        self.workspace.browseRequested.connect(self._open_workspace_files)
        self.workspace.activeChanged.connect(self._on_session_active_changed)
        self.workspace.operationRequested.connect(self._run_operation)
        self.workspace.validationFailed.connect(self._show_validation_error)
        self.workspace.statusMessage.connect(
            lambda msg, ms: self.status.showMessage(msg, ms)
        )
        self.workspace.filesProduced.connect(self._add_outputs)

        self.workspace.file_queue.moveRequested.connect(self._on_queue_move)
        self.workspace.file_queue.removeRequested.connect(self._on_queue_remove)
        self.workspace.file_queue.clearRequested.connect(self._on_queue_clear)

        self.content_stack.addWidget(self.home_view)    # 0
        self.content_stack.addWidget(self.workspace)    # 1
        return self.content_stack

    # ---------- Compatibility aliases used by the test suite ----------
    @property
    def current_file(self):
        return self.session.active_file if self.session else self._current_file

    @current_file.setter
    def current_file(self, pdf):
        self._current_file = pdf
        if self.session is not None:
            self.session.active_file = pdf
        self.workspace.panels.set_file(pdf)

    @property
    def tool_panels(self):
        return self.workspace.panels

    @property
    def batch_view(self):
        return self.workspace.batch_view

    # ---------- Navigation ----------
    def _go_home(self):
        self.content_stack.setCurrentIndex(0)
        self.back_button.setVisible(False)
        self.header_title.setText("Home")
        self.header_sub.setText("Everything you need for PDFs. Fast, private, offline.")
        self.home_view.set_recent(self._recent_paths(), len(self.files))
        self._update_header()

    def _nav_to(self, key):
        if key == "home":
            self._go_home()
            return
        if key == "library":
            self._open_files()
            return
        spec = get_tool(key)
        if spec is None:
            return

        self.session = ToolSession(spec)
        self.workspace.show_tool(spec)
        self.workspace.set_files([], None, [])
        self.content_stack.setCurrentIndex(1)
        self.back_button.setVisible(True)
        self.header_title.setText(spec.label)
        self.header_sub.setText(spec.description)
        self._update_header()
        self.status.showMessage(f"{spec.label} — add files to begin", 3000)

    def _current_nav_key(self):
        return self.session.spec.key if self.session else None

    def _update_tool_banner(self, _key):
        return

    def _recent_paths(self):
        settings = QSettings("PDFToolkit", "PDFToolkit")
        recent = settings.value("recent_files", []) or []
        if isinstance(recent, str):
            recent = [recent]
        return [Path(p) for p in recent if Path(p).exists()]

    def _update_header(self):
        self.save_btn.setEnabled(self.current_file is not None)

    # ---------- File intake ----------
    def _open_home_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Open PDF Files", "", "PDF Files (*.pdf)"
        )
        if paths:
            self._on_home_drop([Path(p) for p in paths])

    def _on_home_drop(self, paths):
        choices = list(pdf_tools())
        if not choices:
            return
        count = len(paths)
        labels = [
            f"{tool.label} ({count} PDF{'s' if count != 1 else ''})"
            for tool in choices
        ]
        label, ok = QInputDialog.getItem(
            self,
            "Choose a tool",
            f"Dropped {count} PDF{'s' if count != 1 else ''} — choose a tool:",
            labels,
            0,
            False,
        )
        if not ok:
            return
        spec = choices[labels.index(label)]
        self._nav_to(spec.key)
        self._on_workspace_paths(paths)

    def _open_workspace_files(self):
        if self.session and self.session.spec.input_mode == "multi_image":
            paths, _ = QFileDialog.getOpenFileNames(
                self, "Open Images", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.tif)"
            )
        else:
            paths, _ = QFileDialog.getOpenFileNames(
                self, "Open PDF Files", "", "PDF Files (*.pdf)"
            )
        if paths:
            self._on_workspace_paths([Path(p) for p in paths])

    def _on_workspace_paths(self, paths):
        if not self.session:
            return
        mode = self.session.spec.input_mode
        if mode == "multi_image":
            accepted = self.session.add_images(paths)
            rejected = len(paths) - len(accepted)
            self.workspace.set_files([], None, self.session.image_paths)
        elif mode in ("single_pdf", "multi_pdf"):
            non_pdf = [p for p in paths if p.suffix.lower() != ".pdf"]
            pdf_paths = [p for p in paths if p.suffix.lower() == ".pdf"]
            loaded = [
                pdf for p in pdf_paths
                if (pdf := self._load_with_password(p)) is not None
            ]
            accepted = self.session.add_pdfs(loaded)
            rejected = len(non_pdf) + (len(pdf_paths) - len(loaded)) + (len(loaded) - len(accepted))
            self.workspace.set_files(self.session.files, self.session.active_file)
        else:
            return

        if accepted:
            self.workspace.tabs.setCurrentIndex(0)
            self.status.showMessage(
                f"Added {len(accepted)} item{'s' if len(accepted) != 1 else ''} "
                f"for {self.session.spec.label}",
                3000,
            )
        if rejected:
            self.status.showMessage(
                f"{rejected} file{'s' if rejected != 1 else ''} skipped", 4000
            )
        self._update_recent_files([p for p in paths if p.exists()])

    def _on_session_active_changed(self, pdf):
        if not self.session:
            return
        if pdf is not None and self.session.active_file is pdf:
            self.workspace.show_preview()
            self._update_header()
            return
        self.session.set_active(pdf)
        self.workspace.set_files(
            self.session.files, self.session.active_file, self.session.image_paths
        )
        if pdf:
            self.workspace.show_preview()
            self._update_header()

    def _on_queue_move(self, row, delta):
        if not self.session or self.session.move(row, delta):
            self.workspace.set_files(
                self.session.files, self.session.active_file, self.session.image_paths
            )

    def _on_queue_remove(self, row):
        if not self.session or self.session.remove_at(row):
            self.workspace.set_files(
                self.session.files, self.session.active_file, self.session.image_paths
            )

    def _on_queue_clear(self):
        if not self.session:
            return
        self.session.clear()
        self.workspace.set_files(
            self.session.files, self.session.active_file, self.session.image_paths
        )

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
            except Exception as e:  # noqa: BLE001
                QMessageBox.warning(self, "Error", f"Failed to load {path.name}: {e}")
                return None
        QMessageBox.warning(self, "Error", f"Too many incorrect passwords for {path.name}")
        return None

    # ---------- Menu & status ----------
    def _setup_menu(self):
        mb = self.menuBar()
        mb.setVisible(False)  # Hidden to eliminate redundant top bar; shortcuts bound to window
        file_menu = mb.addMenu("&File")
        open_a = QAction("&Open PDF(s)…", self)
        open_a.setIcon(get_icon("add", TEXT_MUTED, 14))
        open_a.setShortcut("Ctrl+O")
        open_a.triggered.connect(self._open_files)
        file_menu.addAction(open_a)
        self.addAction(open_a)

        self.recent_menu = file_menu.addMenu("Recent &Files")
        self._refresh_recent_menu()

        file_menu.addSeparator()
        save_a = QAction("&Save As…", self)
        save_a.setIcon(get_icon("to_images", TEXT_MUTED, 14))
        save_a.setShortcut("Ctrl+S")
        save_a.triggered.connect(self._save_current)
        file_menu.addAction(save_a)
        self.addAction(save_a)
        save_as_a = QAction("Save &Copy As…", self)
        save_as_a.setShortcut("Ctrl+Shift+S")
        save_as_a.triggered.connect(self._save_current)
        file_menu.addAction(save_as_a)
        self.addAction(save_as_a)
        file_menu.addSeparator()
        remove_a = QAction("&Remove Selected", self)
        remove_a.setIcon(get_icon("trash", DANGER, 14))
        remove_a.setShortcut("Del")
        remove_a.triggered.connect(self._clear_files)
        file_menu.addAction(remove_a)
        self.addAction(remove_a)
        clear_a = QAction("&Clear Library", self)
        clear_a.triggered.connect(self._clear_files)
        file_menu.addAction(clear_a)
        file_menu.addSeparator()
        exit_a = QAction("E&xit", self)
        exit_a.setShortcut("Ctrl+Q")
        exit_a.triggered.connect(self.close)
        file_menu.addAction(exit_a)
        self.addAction(exit_a)

        tools_menu = mb.addMenu("&Tools")
        for spec in TOOLS:
            if spec.key in {"home", "library"}:
                continue
            a = QAction(spec.label, self)
            a.setIcon(get_icon(spec.icon, TEXT_MUTED, 14))
            a.triggered.connect(lambda _checked=False, key=spec.key: self._nav_to(key))
            tools_menu.addAction(a)
        tools_menu.addSeparator()
        batch_a = QAction("Batch run…", self)
        batch_a.setIcon(get_icon("batch", TEXT_MUTED, 14))
        batch_a.setShortcut("Ctrl+B")
        batch_a.triggered.connect(lambda: self._nav_to("batch"))
        tools_menu.addAction(batch_a)
        self.addAction(batch_a)

        view_menu = mb.addMenu("&View")
        zoom_in = QAction("Zoom &In", self)
        zoom_in.setIcon(get_icon("zoom_in", TEXT_MUTED, 14))
        zoom_in.setShortcuts(["Ctrl++", "Ctrl+="])
        zoom_in.triggered.connect(lambda: self._preview_action("zoom_in"))
        view_menu.addAction(zoom_in)
        self.addAction(zoom_in)
        zoom_out = QAction("Zoom &Out", self)
        zoom_out.setIcon(get_icon("zoom_out", TEXT_MUTED, 14))
        zoom_out.setShortcut("Ctrl+-")
        zoom_out.triggered.connect(lambda: self._preview_action("zoom_out"))
        view_menu.addAction(zoom_out)
        self.addAction(zoom_out)
        zoom_reset = QAction("&Reset Zoom", self)
        zoom_reset.setIcon(get_icon("fit_width", TEXT_MUTED, 14))
        zoom_reset.setShortcut("Ctrl+0")
        zoom_reset.triggered.connect(lambda: self._preview_action("reset_zoom"))
        view_menu.addAction(zoom_reset)
        self.addAction(zoom_reset)

        help_menu = mb.addMenu("&Help")
        sc = QAction("Keyboard &Shortcuts…", self)
        sc.setShortcut("F1")
        sc.triggered.connect(self._show_shortcuts)
        help_menu.addAction(sc)
        self.addAction(sc)
        about = QAction("&About", self)
        about.triggered.connect(self._show_about)
        help_menu.addAction(about)
        self.addAction(about)

    def _refresh_recent_menu(self):
        if not hasattr(self, "recent_menu"):
            return
        self.recent_menu.clear()
        settings = QSettings("PDFToolkit", "PDFToolkit")
        recent = settings.value("recent_files", []) or []
        if isinstance(recent, str):
            recent = [recent]

        existing_recent = [p for p in recent if Path(p).exists()]
        if not existing_recent:
            no_act = self.recent_menu.addAction("No recent files")
            no_act.setEnabled(False)
            return

        for p_str in existing_recent[:10]:
            p = Path(p_str)
            act = self.recent_menu.addAction(get_icon("pdf", DANGER, 14), p.name)
            act.setToolTip(p_str)
            act.triggered.connect(lambda _checked=False, path=p: self._load_files([path]))

        self.recent_menu.addSeparator()
        clear_act = self.recent_menu.addAction("Clear Recent Files")
        clear_act.triggered.connect(self._clear_recent_files)

    def _clear_recent_files(self):
        settings = QSettings("PDFToolkit", "PDFToolkit")
        settings.setValue("recent_files", [])
        self._refresh_recent_menu()

    def _update_recent_files(self, paths: list[Path]):
        settings = QSettings("PDFToolkit", "PDFToolkit")
        recent = settings.value("recent_files", []) or []
        if isinstance(recent, str):
            recent = [recent]
        for p in paths:
            sp = str(p.resolve())
            if sp in recent:
                recent.remove(sp)
            recent.insert(0, sp)
        settings.setValue("recent_files", recent[:15])
        self._refresh_recent_menu()

    def _setup_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

        self.status_file_count = QLabel("0 files loaded")
        self.status_file_count.setStyleSheet(f"color:{TEXT_MUTED};font-size:12px;padding:0 8px;")
        self.status.addPermanentWidget(self.status_file_count)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(180)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self.status.addPermanentWidget(self.progress_bar)

    def _preview_action(self, method: str):
        getattr(self.workspace.preview, method)()

    # ---------- Drag & drop ----------
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = [Path(u.toLocalFile()) for u in event.mimeData().urls() if u.toLocalFile()]
        if not paths:
            return
        if self.content_stack.currentIndex() == 0:
            self._on_home_drop(paths)
        else:
            self._on_workspace_paths(paths)

    # ---------- Output library ----------
    def _open_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Open PDF Files", "", "PDF Files (*.pdf)"
        )
        if paths:
            self._load_files([Path(p) for p in paths])

    def _load_files(self, paths: list[Path]):
        added = 0
        skipped = 0
        for path in paths:
            if any(f.path.resolve() == path.resolve() for f in self.files):
                skipped += 1
                continue
            pdf = self._load_with_password(path)
            if pdf:
                self.file_list.add_file(pdf)
                added += 1

        self._sync_files()
        if paths:
            self._update_recent_files(paths)
        self._go_home()

        if added:
            self.status.showMessage(f"Added {added} PDF{'s' if added != 1 else ''}", 4000)
        if skipped:
            self.status.showMessage(
                f"{skipped} file{'s' if skipped != 1 else ''} already in the library",
                4000,
            )

    def _clear_files(self):
        self.file_list.clear()
        self.files = []
        self._current_file = None
        if self.session:
            self.session.clear()
        self.workspace.set_files([], None, [])
        self._update_header()

    def _sync_files(self):
        self.files = self.file_list.files
        if self.session:
            self.workspace.set_files(
                self.session.files, self.session.active_file, self.session.image_paths
            )
        else:
            self.workspace.batch_view.set_files(self.files)
        count = len(self.files)
        self.status_file_count.setText(f"{count} file{'s' if count != 1 else ''} loaded")

    # ---------- Operations ----------
    def _run_operation(self, op_name: str, params: dict):
        if self._busy:
            self.status.showMessage("Please wait for the current operation to finish", 3000)
            return

        session = self.session
        if op_name == "merge":
            sources = list(session.files) if session and session.files else list(self.files)
            if len(sources) < 2:
                QMessageBox.information(
                    self, "Not enough files", "Add at least two PDFs to merge."
                )
                return
            worker = PdfWorker(PdfEngine.merge, sources, **params)
        elif op_name == "images_to_pdf":
            params = dict(params)
            if not params.get("image_paths") and session:
                params["image_paths"] = list(session.image_paths)
            worker = PdfWorker(PdfEngine.images_to_pdf, **params)
        else:
            source = session.active_file if session and session.active_file else self.current_file
            if not source:
                self._no_file()
                return
            if op_name == "split":
                worker = PdfWorker(PdfEngine.split_by_pages, source, **params)
            else:
                fn = getattr(PdfEngine, op_name, None)
                if fn is None:
                    QMessageBox.critical(self, "Unsupported operation", op_name)
                    return
                worker = PdfWorker(fn, source, **params)

        self._set_busy(True)
        worker.setAutoDelete(False)
        self._active_workers.add(worker)

        def _retire(w=worker):
            self._active_workers.discard(w)

        worker.signals.finished.connect(
            lambda r: (self._worker_finished(r, op_name), _retire())
        )
        worker.signals.error.connect(
            lambda m: (self._worker_finished(m, op_name, True), _retire())
        )
        self.thread_pool.start(worker)
        self.status.showMessage(f"Running {op_name.replace('_', ' ')}…")

    def _worker_finished(self, payload, op_name: str, failed: bool = False):
        self._set_busy(False)
        if failed:
            self._operation_error(payload)
        else:
            self._operation_done(payload, op_name)

    def _no_file(self):
        QMessageBox.information(self, "No file", "Please open a PDF first.")

    def _set_busy(self, busy: bool):
        self._busy = busy
        self.progress_bar.setVisible(busy)
        if busy:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, 100)

    def _operation_done(self, result, op_name: str):
        self._set_busy(False)

        if isinstance(result, list):
            if op_name == "split":
                self._add_outputs(result)
                self.status.showMessage(f"Split into {len(result)} files", 5000)
            elif op_name == "to_images":
                folder = result[0].parent if result else ""
                self.status.showMessage(
                    f"Exported {len(result)} image{'s' if len(result) != 1 else ''} to {folder}",
                    6000,
                )
            else:
                self._add_outputs([r for r in result if isinstance(r, PdfFile)])
        elif isinstance(result, PdfFile):
            self._add_outputs([result])
            self.status.showMessage(
                f"✔  {op_name.replace('_', ' ').title()} saved to {result.path.name}", 5000
            )
        else:
            self.status.showMessage(f"✔  {op_name.replace('_', ' ').title()} finished", 5000)

        self._update_header()

    def _add_outputs(self, pdfs: list[PdfFile]):
        """Add/replace produced files in the output library."""
        for pdf in pdfs:
            existing = next(
                (f for f in self.files if f.path.resolve() == pdf.path.resolve()), None
            )
            if existing is None:
                self.file_list.add_file(pdf)
            else:
                self.file_list.update_file(pdf)
        self._sync_files()

    def _operation_error(self, msg: str):
        self._set_busy(False)
        QMessageBox.critical(self, "Operation failed", msg)
        self.status.showMessage(f"Error: {msg[:80]}", 5000)

    def _show_validation_error(self, msg: str):
        self.status.showMessage(msg, 5000)
        QMessageBox.warning(self, "Check the values", msg)

    def _save_current(self):
        if not self.current_file:
            return
        suggested = str(self.current_file.path)
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Copy", suggested, "PDF Files (*.pdf)"
        )
        if not path:
            return
        target = Path(path)
        if target.suffix.lower() != ".pdf":
            target = target.with_suffix(".pdf")
        try:
            if target.resolve() != self.current_file.path.resolve():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.current_file.path, target)
                self.status.showMessage(f"Saved copy to {target}", 5000)
            else:
                self.status.showMessage("File is already at that location", 4000)
        except OSError as e:
            QMessageBox.warning(self, "Could not save", str(e))

    # ---------- Help dialogs ----------
    def _show_about(self):
        from src.__version__ import __version__
        QMessageBox.about(
            self,
            "About PDF Toolkit",
            f"<h3>PDF Toolkit {__version__}</h3>"
            "<p>A fast, private, offline PDF toolkit.</p>"
            "<p>Built with PySide6 and PyMuPDF.</p>"
        )

    def _show_shortcuts(self):
        rows = [
            ("Ctrl+O", "Open PDF files"),
            ("Ctrl+S", "Save a copy of the selected PDF"),
            ("Ctrl+Shift+S", "Save a copy (same dialog)"),
            ("Ctrl+B", "Open batch processing"),
            ("Ctrl++ / Ctrl+-", "Zoom preview in/out"),
            ("Ctrl+0", "Reset preview zoom"),
            ("Del", "Clear the output library"),
            ("F1", "Show this dialog"),
            ("Ctrl+Q", "Quit"),
            ("Drag & drop", "Add PDFs to the current tool (or choose one on Home)"),
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
