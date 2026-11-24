"""First screen: grouped tool cards and a PDF drop strip."""
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QWidget
)

from src.ui.icons import get_pixmap
from src.ui.theme import TEXT_1, TEXT_2, TEXT_3
from src.ui.tool_registry import SECTION_ORDER, TOOLS
from src.ui.widgets.drop_zone import DropZone


class HomeView(QWidget):
    toolSelected = Signal(str)
    filesDropped = Signal(list)
    openRequested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("HomeView")
        self._columns = 0
        self._cards = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(18)

        brand = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(get_pixmap("pdf", TEXT_1, 28))
        title = QLabel("PDF Toolkit")
        title.setObjectName("HomeTitle")
        sub = QLabel("Everything you need for PDFs. Fast, private, offline.")
        sub.setObjectName("HomeSubtitle")
        sub.setWordWrap(True)
        badge = QLabel("OFFLINE")
        badge.setObjectName("Badge")
        brand.addWidget(icon)
        brand.addWidget(title)
        brand.addWidget(sub, 1)
        brand.addWidget(badge)
        outer.addLayout(brand)

        self.drop_strip = DropZone()
        self.drop_strip.setObjectName("HomeDropStrip")
        self.drop_strip.set_spec(None)
        self.drop_strip.browse_button.setObjectName("HomeBrowseButton")
        self.drop_strip.filesDropped.connect(lambda paths: self.filesDropped.emit(paths))
        self.drop_strip.browseRequested.connect(lambda: self.openRequested.emit())
        outer.addWidget(self.drop_strip)

        self.scroll = QScrollArea()
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("HomeScroll")
        content = QWidget()
        self.grid = QGridLayout(content)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(14)
        self.scroll.setWidget(content)
        outer.addWidget(self.scroll, 1)

        for section in SECTION_ORDER:
            header = QLabel(section)
            header.setObjectName("HomeSectionTitle")
            self._cards.append((header, section, None))
            for spec in (t for t in TOOLS if t.section == section):
                card = self._make_card(spec)
                self._cards.append((card, section, spec))
                card.clicked.connect(
                    lambda _checked=False, key=spec.key: self.toolSelected.emit(key)
                )

        self.recent_label = QLabel("Output Library: 0 files  •  Recent files: none")
        self.recent_label.setObjectName("HomeRecent")
        self.recent_label.setWordWrap(True)
        outer.addWidget(self.recent_label)

        self._rebuild_grid(3)

    def _make_card(self, spec) -> QPushButton:
        card = QPushButton()
        card.setObjectName("ToolCard")
        card.setMinimumHeight(112)
        card.setCursor(Qt.PointingHandCursor)
        v = QVBoxLayout(card)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(6)
        top = QHBoxLayout()
        chip = QLabel()
        chip.setPixmap(get_pixmap(spec.icon, TEXT_1, 22))
        chip.setObjectName("ToolCardIcon")
        arrow = QLabel("→")
        arrow.setObjectName("ToolCardArrow")
        top.addWidget(chip)
        top.addStretch()
        top.addWidget(arrow)
        v.addLayout(top)
        title = QLabel(spec.label)
        title.setObjectName("ToolCardTitle")
        v.addWidget(title)
        desc = QLabel(spec.description)
        desc.setObjectName("ToolCardDesc")
        desc.setWordWrap(True)
        v.addWidget(desc)
        return card

    def set_recent(self, paths: list[Path], file_count: int):
        names = ", ".join(p.name for p in paths[:5])
        self.recent_label.setText(
            f"Output Library: {file_count} file{'s' if file_count != 1 else ''}"
            + (f"  •  Recent: {names}" if names else "  •  Recent files: none")
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        columns = 3 if self.width() >= 1060 else 2 if self.width() >= 760 else 1
        if columns != self._columns:
            self._rebuild_grid(columns)

    def _rebuild_grid(self, columns: int):
        self._columns = columns
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                self.grid.removeWidget(widget)
        row = 0
        col = 0
        for widget, _section, spec in self._cards:
            if spec is None:
                if col:
                    row += 1
                    col = 0
                self.grid.addWidget(widget, row, 0, 1, columns)
                row += 1
                continue
            self.grid.addWidget(widget, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1
        self.grid.setRowStretch(row + 1, 1)
