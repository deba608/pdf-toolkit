from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QProgressBar,
    QListWidget, QListWidgetItem, QSplitter, QToolBar, QStatusBar,
    QMenu, QInputDialog, QComboBox, QLineEdit
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QThreadPool, QRunnable, Signal, QObject, QSize
from PySide6.QtGui import QAction, QIcon, QDragEnterEvent, QDropEvent

from src.core.models import PdfFile, Job, JobStatus
from src.core.pdf_engine import PdfEngine
from src.ui.widgets.file_list import FileListWidget
from src.ui.widgets.preview import PreviewWidget
from src.ui.widgets.tool_panels import ToolPanelsStack
from src.ui.widgets.progress import ProgressWidget


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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Toolkit")
        self.resize(1200, 800)
        self.setAcceptDrops(True)

        self.thread_pool = QThreadPool.globalInstance()
        self.current_file: PdfFile = None
        self.files: list[PdfFile] = []

        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab bar for modes
        self.mode_tabs = QTabWidget()
        self.mode_tabs.addTab(self._create_files_tab(), "Files")
        self.mode_tabs.addTab(self._create_tools_tab(), "Tools")
        self.mode_tabs.addTab(self._create_batch_tab(), "Batch")
        self.mode_tabs.addTab(self._create_settings_tab(), "Settings")
        layout.addWidget(self.mode_tabs)

    def _create_files_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)

        splitter = QSplitter(Qt.Horizontal)

        # Left: file list
        self.file_list = FileListWidget()
        self.file_list.file_selected.connect(self._on_file_selected)
        self.file_list.files_reordered.connect(self._on_files_reordered)
        splitter.addWidget(self.file_list)

        # Right: preview
        self.preview = PreviewWidget()
        splitter.addWidget(self.preview)

        splitter.setSizes([350, 850])
        layout.addWidget(splitter)
        return widget

    def _create_tools_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)

        splitter = QSplitter(Qt.Horizontal)

        # Tool panels
        self.tool_panels = ToolPanelsStack()
        self.tool_panels.operation_requested.connect(self._run_operation)
        splitter.addWidget(self.tool_panels)

        # Preview
        self.tool_preview = PreviewWidget()
        splitter.addWidget(self.tool_preview)

        splitter.setSizes([400, 800])
        layout.addWidget(splitter)
        return widget

    def _create_batch_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Batch Processing — coming soon"))
        return widget

    def _create_settings_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Settings — coming soon"))
        return widget

    def _setup_menu(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        open_action = QAction("&Open PDF(s)...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_files)
        file_menu.addAction(open_action)

        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        for name in ["Merge", "Split", "Rotate", "Reorder", "Watermark",
                     "Encrypt", "Decrypt", "Compress", "To Images", "Images to PDF"]:
            action = QAction(name, self)
            action.triggered.connect(lambda _, n=name: self._show_tool(n))
            tools_menu.addAction(action)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        shortcuts_action = QAction("Keyboard &Shortcuts...", self)
        shortcuts_action.setShortcut("F1")
        shortcuts_action.triggered.connect(self._show_shortcuts)
        help_menu.addAction(shortcuts_action)

    def _setup_toolbar(self):
        tb = QToolBar("Main")
        tb.setIconSize(QSize(24, 24))
        self.addToolBar(tb)

        open_btn = QAction("Open", self)
        open_btn.triggered.connect(self._open_files)
        tb.addAction(open_btn)

        tb.addSeparator()

        save_btn = QAction("Save As...", self)
        save_btn.setShortcut("Ctrl+S")
        save_btn.triggered.connect(self._save_current)
        tb.addAction(save_btn)

    def _setup_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status.addPermanentWidget(self.progress_bar)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = [Path(u.toLocalFile()) for u in event.mimeData().urls()
                 if u.toLocalFile().lower().endswith('.pdf')]
        self._load_files(paths)

    def _open_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Open PDF Files", "", "PDF Files (*.pdf)"
        )
        if paths:
            self._load_files([Path(p) for p in paths])

    def _load_files(self, paths: list[Path]):
        for path in paths:
            pdf = self._load_with_password(path)
            if pdf:
                self.files.append(pdf)
                self.file_list.add_file(pdf)

    def _load_with_password(self, path: Path) -> PdfFile | None:
        """Load a PDF, asking for a password up to 3 times if it is encrypted."""
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
                    self, f"Encrypted PDF - {path.name}", prompt, QLineEdit.Password
                )
                if not ok:
                    self.status.showMessage(f"Cancelled loading {path.name}", 3000)
                    return None
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load {path.name}: {e}")
                return None
        QMessageBox.warning(self, "Error", f"Too many incorrect passwords for {path.name}")
        return None

    def _on_file_selected(self, pdf: PdfFile):
        self.current_file = pdf
        self.preview.load_pdf(pdf)
        self.tool_preview.load_pdf(pdf)
        self.tool_panels.set_file(pdf)

    def _on_files_reordered(self, files: list[PdfFile]):
        self.files = files

    def _show_tool(self, name: str):
        self.mode_tabs.setCurrentIndex(1)  # Tools tab
        self.tool_panels.show_tool(name.lower())

    def _run_operation(self, op_name: str, params: dict):
        if not self.current_file and op_name != "images_to_pdf":
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        if op_name == "merge":
            worker = PdfWorker(PdfEngine.merge, self.files, **params)
        elif op_name == "split":
            worker = PdfWorker(PdfEngine.split_by_pages, self.current_file, **params)
        elif op_name == "images_to_pdf":
            worker = PdfWorker(PdfEngine.images_to_pdf, **params)
        else:
            worker = PdfWorker(getattr(PdfEngine, op_name), self.current_file, **params)

        worker.signals.progress.connect(self.progress_bar.setValue)
        worker.signals.finished.connect(lambda r: self._operation_done(r, op_name))
        worker.signals.error.connect(self._operation_error)
        self.thread_pool.start(worker)

    def _operation_done(self, result, op_name: str):
        self.progress_bar.setVisible(False)

        if isinstance(result, list):
            # Multiple results (split, to_images)
            if op_name == "split":
                for pdf in result:
                    self.files.append(pdf)
                    self.file_list.add_file(pdf)
                count = len(result)
                self.status.showMessage(f"Split into {count} file{'s' if count > 1 else ''}", 3000)
            elif op_name == "to_images":
                count = len(result)
                self.status.showMessage(f"Exported {count} image{'s' if count > 1 else ''}", 3000)
        else:
            # Single result
            self.current_file = result
            self.preview.load_pdf(result)
            self.tool_preview.load_pdf(result)
            self.file_list.update_file(result)
            self.status.showMessage(f"{op_name} completed", 3000)

    def _operation_error(self, msg: str):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", msg)
        self.status.showMessage(f"Error: {msg[:50]}...", 3000)

    def _save_current(self):
        if not self.current_file:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", self.current_file.name, "PDF Files (*.pdf)"
        )
        if path:
            # For now, just copy - in real impl, save the modified doc
            import shutil
            shutil.copy2(self.current_file.path, path)
            self.status.showMessage(f"Saved to {path}", 3000)

    def _show_about(self):
        QMessageBox.about(
            self,
            "PDF Toolkit",
            "<h3>PDF Toolkit v1.0.0</h3>"
            "<p>Offline PDF manipulation desktop application</p>"
            "<p>Built with PySide6 and PyMuPDF</p>"
            "<p>Copyright &copy; 2026</p>"
        )

    def _show_shortcuts(self):
        shortcuts = [
            ("Ctrl+O", "Open PDF files"),
            ("F1", "Show keyboard shortcuts"),
            ("Ctrl+S", "Save current PDF"),
            ("Del", "Delete selected file"),
            ("Arrow Up/Down", "Move file up/down in list"),
            ("Ctrl+Left Click", "Select multiple files"),
            ("Esc", "Clear selection/cancel operation"),
            ("Shift+Arrow", "Extend selection"),
        ]

        lines = []
        for key, desc in shortcuts:
            lines.append(f"<b>{key}</b>: {desc}")
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Keyboard Shortcuts")
        dialog.setText("\n".join(lines))
        dialog.setInformativeText("Press Esc or OK to close")
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec()