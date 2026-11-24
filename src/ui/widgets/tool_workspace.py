"""Task screen: file pickup on the left, options and preview on the right."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QLabel, QScrollArea, QSplitter, QStackedWidget,
    QTabWidget, QVBoxLayout, QWidget
)

from src.ui.widgets.batch_view import BatchView
from src.ui.widgets.drop_zone import DropZone
from src.ui.widgets.file_queue import FileQueue
from src.ui.widgets.preview import PreviewWidget
from src.ui.widgets.tool_panels import ToolPanelsStack


class ToolWorkspace(QWidget):
    operationRequested = Signal(str, dict)
    validationFailed = Signal(str)
    filesAddedRequested = Signal(list)
    browseRequested = Signal()
    activeChanged = Signal(object)
    statusMessage = Signal(str, int)
    filesProduced = Signal(list)

    def __init__(self):
        super().__init__()
        self.setObjectName("ToolWorkspace")
        self.spec = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(12)

        self.requirement_label = QLabel("Add files to get started")
        self.requirement_label.setObjectName("WorkspaceHint")
        self.requirement_label.setWordWrap(True)
        outer.addWidget(self.requirement_label)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        left = QFrame()
        left.setObjectName("WorkspaceLeft")
        lv = QVBoxLayout(left)
        lv.setContentsMargins(14, 14, 14, 14)
        lv.setSpacing(12)
        self.drop_zone = DropZone()
        self.drop_zone.filesDropped.connect(lambda paths: self.filesAddedRequested.emit(paths))
        self.drop_zone.browseRequested.connect(lambda: self.browseRequested.emit())
        self.file_queue = FileQueue()
        self.file_queue.activeChanged.connect(lambda pdf: self.activeChanged.emit(pdf))
        lv.addWidget(self.drop_zone, 0)
        lv.addWidget(self.file_queue, 1)
        splitter.addWidget(left)

        right = QFrame()
        right.setObjectName("SettingsPanel")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(12, 12, 12, 12)
        rv.setSpacing(8)
        self.tabs = QTabWidget()
        self.tabs.setObjectName("ToolTabs")
        self.options_stack = QStackedWidget()
        self.panels = ToolPanelsStack()
        self.batch_view = BatchView()
        self.options_stack.addWidget(self.panels)
        self.options_stack.addWidget(self.batch_view)
        options_scroll = QScrollArea()
        options_scroll.setFrameShape(QFrame.NoFrame)
        options_scroll.setWidgetResizable(True)
        options_scroll.setWidget(self.options_stack)
        self.tabs.addTab(options_scroll, "Options")
        self.preview_stack = QStackedWidget()
        self.preview_empty = QLabel("No PDF selected. Choose a file in the queue to preview it.")
        self.preview_empty.setObjectName("EmptyState")
        self.preview_empty.setAlignment(Qt.AlignCenter)
        self.preview_empty.setWordWrap(True)
        self.preview = PreviewWidget()
        self.preview_stack.addWidget(self.preview_empty)
        self.preview_stack.addWidget(self.preview)
        self.tabs.addTab(self.preview_stack, "Preview")
        rv.addWidget(self.tabs, 1)
        splitter.addWidget(right)

        splitter.setSizes([560, 640])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        outer.addWidget(splitter, 1)

        self.panels.operation_requested.connect(
            lambda op, params: self.operationRequested.emit(op, params)
        )
        self.panels.validation_failed.connect(lambda msg: self.validationFailed.emit(msg))
        self.panels.add_files_requested.connect(lambda: self.browseRequested.emit())
        self.batch_view.status_message.connect(
            lambda msg, ms: self.statusMessage.emit(msg, ms)
        )
        self.batch_view.files_produced.connect(lambda files: self.filesProduced.emit(files))

    def show_tool(self, spec):
        self.spec = spec
        self.drop_zone.set_spec(spec)
        self.file_queue.set_can_reorder(spec.input_mode == "multi_pdf")
        self.requirement_label.setText(self._requirement_text(spec))
        if spec.key == "batch":
            self.options_stack.setCurrentWidget(self.batch_view)
        else:
            self.panels.set_external_queue(spec.key == "merge")
            self.panels.show_tool(spec.panel_key or "")
            self.options_stack.setCurrentWidget(self.panels)
        self.batch_view.set_files([])
        self.tabs.setCurrentIndex(0)

    def set_files(self, files, active, image_paths=None):
        self.file_queue.set_files(files, active)
        self.panels.set_file(active)
        self.panels.set_files(files)
        self.batch_view.set_files(files)
        self.preview_stack.setCurrentIndex(1 if active else 0)
        if active:
            self.preview.load_pdf(active)
        else:
            self.preview.load_pdf(None)
        if image_paths is not None and self.spec and self.spec.input_mode == "multi_image":
            self.panels.img_list.clear()
            self.panels.img_list.addItems([str(p) for p in image_paths])
            self.panels.set_file(active)

    def show_preview(self):
        self.tabs.setCurrentIndex(1)

    def _requirement_text(self, spec) -> str:
        if spec.input_mode == "multi_image":
            return "Add two or more images. PNG, JPG, BMP, and TIFF are supported."
        if spec.key == "merge":
            return "Add at least two PDFs. Drag to reorder before merging."
        if spec.input_mode == "multi_pdf":
            return "Add one or more PDFs. Batch run processes each file separately."
        return f"Add one PDF to {spec.label.lower()}. Extra files will be rejected."
