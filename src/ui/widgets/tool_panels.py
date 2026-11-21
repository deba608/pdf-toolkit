from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QLabel, QPushButton,
    QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox, QComboBox,
    QFileDialog, QHBoxLayout, QGroupBox, QFormLayout, QListWidget,
    QListWidgetItem, QAbstractItemView
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor

from src.core.models import PdfFile


class ToolPanelsStack(QWidget):
    operation_requested = Signal(str, dict)

    def __init__(self):
        super().__init__()
        self.current_file: PdfFile = None
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
        btn = QPushButton("Merge All Files")
        btn.clicked.connect(lambda: self.operation_requested.emit("merge", {}))
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
        layout.addLayout(form)
        btn = QPushButton("Rotate Selected Pages")
        btn.clicked.connect(lambda: self.operation_requested.emit("rotate", {
            "degrees": int(self.rotate_degrees.currentText().replace("°", ""))
        }))
        layout.addWidget(btn)
        layout.addStretch()
        return w

    def _create_reorder_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Reorder Pages"))
        layout.addWidget(QLabel("Drag to reorder in the Files tab"))
        btn = QPushButton("Apply Reorder")
        btn.clicked.connect(lambda: self.operation_requested.emit("reorder", {}))
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
            "permissions": self.enc_perms.currentIndex()
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
        layout.addLayout(form)
        btn = QPushButton("Convert")
        btn.clicked.connect(lambda: self.operation_requested.emit("to_images", {
            "dpi": self.img_dpi.value(),
            "fmt": self.img_format.currentText().lower()
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
        convert_btn = QPushButton("Create PDF")
        convert_btn.clicked.connect(lambda: self.operation_requested.emit("images_to_pdf", {
            "images": [self.img_list.item(i).text() for i in range(self.img_list.count())]
        }))
        layout.addWidget(convert_btn)
        layout.addStretch()
        return w

    def _add_images(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        for p in paths:
            self.img_list.addItem(p)