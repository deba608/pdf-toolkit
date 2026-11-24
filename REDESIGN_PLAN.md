# PDF Toolkit UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the sidebar-based shell with a full-screen Home Grid, per-tool workspaces with drag-and-drop file queues, and a right-side tabbed Options/Preview panel, without changing PDF engine behavior.

**Architecture:** Add a `ToolRegistry` and `ToolSession` as the navigation/state contracts, then build reusable `DropZone`, `FileQueue`, `HomeView`, and `ToolWorkspace` widgets. `MainWindow` becomes a thin shell that creates a fresh session per tool and dispatches existing `PdfEngine` calls using session files. Existing tool panels, batch view, preview widget, and engine stay intact.

**Tech Stack:** Python 3.10+, PySide6/Qt 6, PyMuPDF, QSS styling, existing headless test scripts (`QT_QPA_PLATFORM=offscreen`).

**Spec:** `docs/superpowers/specs/2026-11-24-ui-redesign-design.md`

---

## File structure

| File | Responsibility |
|---|---|
| `src/ui/tool_registry.py` | New. `ToolSpec` and `TOOLS` registry; single source for cards, menus, and titles. |
| `src/ui/widgets/tool_session.py` | New. Per-tool files/images/active file and input-mode rules. |
| `src/ui/widgets/drop_zone.py` | New. Dashed drop target with browse button, MIME filtering, drag highlight. |
| `src/ui/widgets/file_queue.py` | New. Ordered file list with select/move/remove/clear. |
| `src/ui/widgets/home_view.py` | New. Home header, drop strip, responsive card grid, recent files. |
| `src/ui/widgets/tool_workspace.py` | New. Left drop/queue + right tabbed Options/Preview. Hosts existing panels. |
| `src/ui/main_window.py` | Modify. Shell, header back button, tool routing, legacy compatibility aliases. |
| `src/ui/theme.py` | Modify. Append QSS for the new widgets; preserve existing tokens and audit fixes. |
| `src/ui/widgets/tool_panels.py` | Modify. Add `set_external_queue()` to hide the in-panel merge queue in the new UI. |
| `tests/test_redesign_ui.py` | New. Headless acceptance checks for the redesign. |
| `docs/USER_GUIDE.md` | Modify. Replace old sidebar wireframe and workflow text. |

## Assumptions (discharge before code)

- `PdfEngine` signatures are unchanged; verified in `src/core/pdf_engine.py` and `tests/test_ui_wiring.py`.
- Existing tests import `MainWindow.file_list`, `MainWindow.tool_panels`, `MainWindow.batch_view`, `MainWindow.current_file`, `MainWindow.files`, `MainWindow._nav_to()`, `MainWindow._load_files()`, `MainWindow._run_operation()`. Compatibility aliases are required (`tests/test_ui_check.py:21-28`, `tests/test_e2e_ui.py:48-54,199-215`).
- User's uncommitted changes in `src/ui/theme.py` and `src/ui/widgets/tool_panels.py` are intentional audit fixes. Do not revert them; add to them.
- Home drop uses the tool picker dialog confirmed by the user.

---

### Task 1: Design docs and glossary

**Files:**
- Create: `CONTEXT.md`
- Create: `docs/superpowers/specs/2026-11-24-ui-redesign-design.md`
- Create: `REDESIGN_PLAN.md`
- Create: `docs/superpowers/plans/2026-11-24-ui-redesign.md`

- [x] **Step 1:** Write canonical terms to `CONTEXT.md`: Home Grid, Tool Spec, Tool Workspace, Drop Zone, File Queue, Tool Session, Settings Panel, Preview Panel, Output Library.
- [x] **Step 2:** Write approved design spec to `docs/superpowers/specs/2026-11-24-ui-redesign-design.md`.
- [x] **Step 3:** Write this plan to `REDESIGN_PLAN.md`.
- [ ] **Step 4:** Create pointer file `docs/superpowers/plans/2026-11-24-ui-redesign.md` with a single line: `See [REDESIGN_PLAN.md](../../REDESIGN_PLAN.md) for the full implementation plan.`

---

### Task 2: Define ToolRegistry contract

**Files:**
- Create: `src/ui/tool_registry.py`
- Test: `tests/test_redesign_ui.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_redesign_ui.py`:

```python
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_registry():
    from src.ui.tool_registry import TOOLS, get_tool, pdf_tools, tools_for_section

    assert len(TOOLS) == 12
    assert [s for s in ("Tools", "Converter", "Security", "Automation", "Library")
            if tools_for_section(s)] == ["Tools", "Converter", "Security", "Automation", "Library"]
    assert get_tool("merge").input_mode == "multi_pdf"
    assert get_tool("images to pdf").input_mode == "multi_image"
    assert get_tool("batch").panel_key is None
    assert all(t.key in {p.key for p in pdf_tools()} for t in (get_tool("merge"), get_tool("compress")))
    assert get_tool("does-not-exist") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_redesign_ui.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.ui.tool_registry'`.

- [ ] **Step 3: Write the contract implementation**

Create `src/ui/tool_registry.py` with exactly:

```python
"""Single source of truth for tools shown in Home Grid and menus."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolSpec:
    key: str
    label: str
    icon: str
    section: str
    description: str
    input_mode: str          # single_pdf | multi_pdf | multi_image | none
    panel_key: str | None    # key in ToolPanelsStack; None for batch/library


TOOLS: tuple[ToolSpec, ...] = (
    ToolSpec("merge", "Merge", "merge", "Tools",
             "Combine multiple PDFs into one", "multi_pdf", "merge"),
    ToolSpec("split", "Split", "split", "Tools",
             "Split a PDF into smaller files", "single_pdf", "split"),
    ToolSpec("rotate", "Rotate", "rotate", "Tools",
             "Rotate pages 90°, 180°, or 270°", "single_pdf", "rotate"),
    ToolSpec("reorder", "Reorder", "reorder", "Tools",
             "Rearrange or drop specific pages", "single_pdf", "reorder"),
    ToolSpec("watermark", "Watermark", "watermark", "Tools",
             "Stamp a text watermark on pages", "single_pdf", "watermark"),
    ToolSpec("compress", "Compress", "compress", "Tools",
             "Reduce file size with lossless optimization", "single_pdf", "compress"),
    ToolSpec("encrypt", "Encrypt", "encrypt", "Security",
             "Password-protect with AES-256", "single_pdf", "encrypt"),
    ToolSpec("decrypt", "Decrypt", "decrypt", "Security",
             "Remove password protection", "single_pdf", "decrypt"),
    ToolSpec("to images", "PDF → Images", "to_images", "Converter",
             "Export PDF pages to PNG/JPG", "single_pdf", "to images"),
    ToolSpec("images to pdf", "Images → PDF", "images_to_pdf", "Converter",
             "Create a PDF from images", "multi_image", "images to pdf"),
    ToolSpec("batch", "Batch run", "batch", "Automation",
             "Apply an operation to many PDFs at once", "multi_pdf", None),
    ToolSpec("library", "Open PDFs", "pdf", "Library",
             "Browse PDFs and view recent files", "none", None),
)

SECTION_ORDER = ("Tools", "Converter", "Security", "Automation", "Library")
PDF_INPUT_MODES = ("single_pdf", "multi_pdf")


def get_tool(key: str) -> ToolSpec | None:
    return next((tool for tool in TOOLS if tool.key == key), None)


def tools_for_section(section: str) -> tuple[ToolSpec, ...]:
    return tuple(tool for tool in TOOLS if tool.section == section)


def pdf_tools() -> tuple[ToolSpec, ...]:
    return tuple(tool for tool in TOOLS if tool.input_mode in PDF_INPUT_MODES)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_redesign_ui.py`
Expected: PASS for `test_registry`.

- [ ] **Step 5: Commit**

```bash
git add src/ui/tool_registry.py tests/test_redesign_ui.py CONTEXT.md docs/superpowers/specs/2026-11-24-ui-redesign-design.md REDESIGN_PLAN.md docs/superpowers/plans/2026-11-24-ui-redesign.md
git commit -m "docs: spec and contracts for UI redesign"
```

---

### Task 3: Define ToolSession contract

**Files:**
- Create: `src/ui/widgets/tool_session.py`
- Test: `tests/test_redesign_ui.py`

- [ ] **Step 1: Add failing session tests**

Append to `tests/test_redesign_ui.py`:

```python
def test_session_rules():
    from pathlib import Path
    from src.core.models import PdfFile
    from src.ui.tool_registry import get_tool
    from src.ui.widgets.tool_session import ToolSession

    def pdf(name):
        return PdfFile(path=Path(name), name=name, page_count=3)

    single = ToolSession(get_tool("compress"))
    assert single.add_pdfs([pdf("a.pdf"), pdf("b.pdf")]) == [single.files[0]]
    assert len(single.files) == 1
    assert single.add_pdfs([pdf("c.pdf")]) == []

    multi = ToolSession(get_tool("merge"))
    assert len(multi.add_pdfs([pdf("a.pdf"), pdf("b.pdf"), pdf("c.pdf")])) == 3
    multi.move(2, -1)
    assert [p.name for p in multi.files] == ["a.pdf", "c.pdf", "b.pdf"]
    multi.remove_at(0)
    assert [p.name for p in multi.files] == ["c.pdf", "b.pdf"]

    images = ToolSession(get_tool("images to pdf"))
    assert images.add_pdfs([pdf("a.pdf")]) == []
    assert images.add_images([Path("x.png"), Path("bad.txt")]) == [Path("x.png")]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_redesign_ui.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.ui.widgets.tool_session'`.

- [ ] **Step 3: Implement ToolSession**

Create `src/ui/widgets/tool_session.py` with exactly:

```python
"""Per-tool file state. A new session is created every time a tool is opened."""
from pathlib import Path

from src.core.models import PdfFile
from src.ui.tool_registry import ToolSpec

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}


class ToolSession:
    def __init__(self, spec: ToolSpec):
        self.spec = spec
        self.files: list[PdfFile] = []
        self.image_paths: list[Path] = []
        self.active_file: PdfFile | None = None

    @property
    def can_reorder(self) -> bool:
        return self.spec.input_mode == "multi_pdf"

    def add_pdfs(self, pdfs: list[PdfFile]) -> list[PdfFile]:
        if self.spec.input_mode != "single_pdf" and self.spec.input_mode != "multi_pdf":
            return []
        if self.spec.input_mode == "single_pdf":
            if self.files:
                return []
            if not pdfs:
                return []
            self.files = [pdfs[0]]
            self.active_file = pdfs[0]
            return [pdfs[0]]

        existing = {f.path.resolve() for f in self.files}
        added = [f for f in pdfs if f.path.resolve() not in existing]
        self.files.extend(added)
        if self.active_file is None and self.files:
            self.active_file = self.files[0]
        return added

    def add_images(self, paths: list[Path]) -> list[Path]:
        if self.spec.input_mode != "multi_image":
            return []
        existing = {p.resolve() for p in self.image_paths}
        added = [p for p in paths if p.suffix.lower() in IMAGE_SUFFIXES
                 and p.resolve() not in existing]
        self.image_paths.extend(added)
        return added

    def set_active(self, pdf: PdfFile) -> None:
        if pdf in self.files:
            self.active_file = pdf

    def move(self, index: int, delta: int) -> bool:
        target = index + delta
        if not self.can_reorder or not (0 <= index < len(self.files)):
            return False
        if not (0 <= target < len(self.files)):
            return False
        self.files.insert(target, self.files.pop(index))
        return True

    def remove_at(self, index: int) -> bool:
        if not (0 <= index < len(self.files)):
            return False
        removed = self.files.pop(index)
        if self.active_file is removed:
            self.active_file = self.files[0] if self.files else None
        return True

    def clear(self) -> None:
        self.files.clear()
        self.image_paths.clear()
        self.active_file = None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_redesign_ui.py`
Expected: PASS for `test_session_rules`.

- [ ] **Step 5: Commit**

```bash
git add src/ui/widgets/tool_session.py tests/test_redesign_ui.py
git commit -m "feat: add per-tool session state"
```

---

### Task 4: Build DropZone and FileQueue widgets

**Files:**
- Create: `src/ui/widgets/drop_zone.py`
- Create: `src/ui/widgets/file_queue.py`
- Test: `tests/test_redesign_ui.py`

- [ ] **Step 1: Add failing widget tests**

Append to `tests/test_redesign_ui.py`:

```python
def test_drop_zone_and_file_queue():
    from PySide6.QtWidgets import QApplication
    from src.ui.tool_registry import get_tool
    from src.ui.widgets.drop_zone import DropZone
    from src.ui.widgets.file_queue import FileQueue

    app = QApplication.instance() or QApplication([])
    zone = DropZone()
    zone.set_spec(get_tool("merge"))
    assert zone.accepts_suffix(".pdf")
    assert not zone.accepts_suffix(".png")
    assert "Merge" in zone.title_label.text()

    zone.set_spec(get_tool("images to pdf"))
    assert zone.accepts_suffix(".png")
    assert not zone.accepts_suffix(".pdf")

    queue = FileQueue()
    queue.set_can_reorder(False)
    assert not queue.up_button.isEnabled()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_redesign_ui.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.ui.widgets.drop_zone'`.

- [ ] **Step 3: Implement DropZone**

Create `src/ui/widgets/drop_zone.py` with exactly:

```python
"""Reusable dashed drag-and-drop target."""
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
)

from src.ui.icons import get_icon, get_pixmap
from src.ui.theme import TEXT_1, TEXT_2, TEXT_3
from src.ui.widgets.tool_session import IMAGE_SUFFIXES


class DropZone(QFrame):
    filesDropped = Signal(list)
    browseRequested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.spec = None

        v = QVBoxLayout(self)
        v.setAlignment(Qt.AlignCenter)
        v.setSpacing(8)
        v.setContentsMargins(24, 28, 24, 28)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(get_pixmap("pdf", TEXT_3, 40))
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel("Drop files here")
        self.title_label.setObjectName("DropZoneTitle")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.subtitle_label = QLabel("or browse from your computer")
        self.subtitle_label.setObjectName("DropZoneSubtitle")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)

        self.browse_button = QPushButton("  Browse files…")
        self.browse_button.setObjectName("Secondary")
        self.browse_button.clicked.connect(lambda: self.browseRequested.emit())

        v.addWidget(self.icon_label)
        v.addWidget(self.title_label)
        v.addWidget(self.subtitle_label)
        v.addWidget(self.browse_button, 0, Qt.AlignCenter)

    def set_spec(self, spec):
        self.spec = spec
        if spec is None:
            self.title_label.setText("Drop PDFs here to get started")
            self.subtitle_label.setText("or choose files from your computer")
            return
        label = "PDFs" if spec.input_mode != "multi_image" else "images"
        verb = "Merge" if spec.key == "merge" else spec.label
        self.title_label.setText(f"Drop {label} here for {verb}")
        self.subtitle_label.setText(f"{spec.description}. Drag files in or browse.")

    def accepts_suffix(self, suffix: str) -> bool:
        suffix = suffix.lower()
        if self.spec is None or self.spec.input_mode == "multi_image":
            return suffix in IMAGE_SUFFIXES or suffix == ".pdf"
        return suffix in IMAGE_SUFFIXES if self.spec.input_mode == "multi_image" else suffix == ".pdf"

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dropActive", True)
            self._repolish()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.setProperty("dropActive", False)
        self._repolish()

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dropActive", False)
        self._repolish()
        paths = [Path(u.toLocalFile()) for u in event.mimeData().urls() if u.toLocalFile()]
        if paths:
            self.filesDropped.emit(paths)

    def _repolish(self):
        self.style().unpolish(self)
        self.style().polish(self)
```

Replace the import line `from PySide6.QtCore import Signal` with `from PySide6.QtCore import Qt, Signal` in the same file.

- [ ] **Step 4: Implement FileQueue**

Create `src/ui/widgets/file_queue.py` with exactly:

```python
"""Ordered file list for the active tool session."""
from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QVBoxLayout, QWidget
)

from src.core.models import PdfFile
from src.ui.icons import get_icon
from src.ui.theme import PRIMARY, TEXT_MUTED


class FileQueue(QWidget):
    activeChanged = Signal(object)
    removeRequested = Signal(int)
    moveRequested = Signal(int, int)
    clearRequested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("FileQueue")
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(8)

        header = QHBoxLayout()
        self.count_label = QLabel("0 files")
        self.count_label.setObjectName("SectionLabel")
        header.addWidget(self.count_label)
        header.addStretch()
        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("Ghost")
        self.clear_button.clicked.connect(lambda: self.clearRequested.emit())
        header.addWidget(self.clear_button)
        v.addLayout(header)

        self.list = QListWidget()
        self.list.setObjectName("FileQueueList")
        self.list.setFrameShape(QFrame.NoFrame)
        self.list.setIconSize(QSize(20, 20))
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.currentItemChanged.connect(
            lambda current, _: self.activeChanged.emit(
                current.data(Qt.UserRole) if current else None
            )
        )
        v.addWidget(self.list, 1)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        self.up_button = QPushButton("▲ Up")
        self.up_button.setObjectName("Secondary")
        self.down_button = QPushButton("▼ Down")
        self.down_button.setObjectName("Secondary")
        self.remove_button = QPushButton("✕ Remove")
        self.remove_button.setObjectName("Secondary")
        buttons.addWidget(self.up_button)
        buttons.addWidget(self.down_button)
        buttons.addWidget(self.remove_button)
        buttons.addStretch()
        v.addLayout(buttons)

        self.up_button.clicked.connect(lambda: self._emit_move(-1))
        self.down_button.clicked.connect(lambda: self._emit_move(1))
        self.remove_button.clicked.connect(
            lambda: self.removeRequested.emit(self.list.currentRow())
        )
        self.set_can_reorder(False)

    def set_can_reorder(self, enabled: bool):
        self.up_button.setVisible(enabled)
        self.down_button.setVisible(enabled)
        self.up_button.setEnabled(False)
        self.down_button.setEnabled(False)

    def set_files(self, files: list[PdfFile], active: PdfFile | None = None):
        self.list.blockSignals(True)
        self.list.clear()
        for pdf in files:
            item = QListWidgetItem(f"  {pdf.name}   ({pdf.page_count}p • {pdf.size_mb:.2f} MB)")
            item.setIcon(get_icon("pdf", PRIMARY, 18))
            item.setData(Qt.UserRole, pdf)
            item.setSizeHint(QSize(0, 36))
            self.list.addItem(item)
        self.list.blockSignals(False)
        self.count_label.setText(f"{len(files)} file{'s' if len(files) != 1 else ''}")
        self.remove_button.setEnabled(len(files) > 0)
        self.clear_button.setEnabled(len(files) > 0)
        if active is not None:
            self._select(active)

    def _select(self, pdf: PdfFile):
        for i in range(self.list.count()):
            if self.list.item(i).data(Qt.UserRole) is pdf:
                self.list.setCurrentRow(i)
                return

    def _emit_move(self, delta: int):
        row = self.list.currentRow()
        if row >= 0:
            self.moveRequested.emit(row, delta)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python tests/test_redesign_ui.py`
Expected: PASS for `test_drop_zone_and_file_queue`.

- [ ] **Step 6: Commit**

```bash
git add src/ui/widgets/drop_zone.py src/ui/widgets/file_queue.py tests/test_redesign_ui.py
git commit -m "feat: add drop zone and file queue widgets"
```

---

### Task 5: Build HomeView with responsive card grid

**Files:**
- Create: `src/ui/widgets/home_view.py`
- Test: `tests/test_redesign_ui.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_redesign_ui.py`:

```python
def test_home_view():
    from PySide6.QtWidgets import QApplication, QLabel, QPushButton
    from src.ui.widgets.home_view import HomeView

    app = QApplication.instance() or QApplication([])
    home = HomeView()
    cards = [b for b in home.findChildren(QPushButton) if b.objectName() == "ToolCard"]
    assert len(cards) == 12
    labels = [l.text() for b in cards for l in b.findChildren(QLabel)
              if l.objectName() == "ToolCardTitle"]
    assert any("Merge" in t for t in labels)
    assert any("Batch run" in t for t in labels)
    assert home.findChild(QPushButton, "HomeBrowseButton") is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_redesign_ui.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.ui.widgets.home_view'`.

- [ ] **Step 3: Implement HomeView**

Create `src/ui/widgets/home_view.py` with exactly:

```python
"""First screen: grouped tool cards and a PDF drop strip."""
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QWidget
)

from src.ui.icons import get_icon, get_pixmap
from src.ui.theme import PRIMARY_SOFT, TEXT_1, TEXT_2, TEXT_3
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
            header_index = len(self._cards)
            self._cards.append((header, section, None))
            for spec in (t for t in TOOLS if t.section == section):
                card = self._make_card(spec)
                self._cards.append((card, section, spec))
                card.clicked.connect(lambda _=False, key=spec.key: self.toolSelected.emit(key))

        self.recent_label = QLabel("Recent files: none")
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
        for widget, _section, _spec in self._cards:
            if isinstance(widget, QLabel) and widget.objectName() == "HomeSectionTitle":
                self.grid.addWidget(widget, row, 0, 1, columns)
                row += 1
                continue
            if isinstance(widget, QPushButton):
                index = sum(1 for w, _, _ in self._cards[:self._cards.index((widget, _section, _spec))]
                            if isinstance(w, QPushButton))
                self.grid.addWidget(widget, row + index // columns, index % columns)
        self.grid.setRowStretch(row + 8, 1)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_redesign_ui.py`
Expected: PASS for `test_home_view`.

- [ ] **Step 5: Commit**

```bash
git add src/ui/widgets/home_view.py tests/test_redesign_ui.py
git commit -m "feat: build responsive home tool grid"
```

---

### Task 6: Build ToolWorkspace with right tabbed panel

**Files:**
- Create: `src/ui/widgets/tool_workspace.py`
- Modify: `src/ui/widgets/tool_panels.py`
- Test: `tests/test_redesign_ui.py`

- [ ] **Step 1: Add failing workspace tests**

Append to `tests/test_redesign_ui.py`:

```python
def test_tool_workspace():
    from PySide6.QtWidgets import QApplication, QTabWidget
    from src.ui.tool_registry import get_tool
    from src.ui.widgets.tool_workspace import ToolWorkspace

    app = QApplication.instance() or QApplication([])
    ws = ToolWorkspace()
    tabs = ws.findChild(QTabWidget, "ToolTabs")
    assert tabs is not None
    assert [tabs.tabText(i) for i in range(tabs.count())] == ["Options", "Preview"]
    ws.show_tool(get_tool("merge"))
    assert "Merge" in ws.requirement_label.text() or "PDF" in ws.requirement_label.text()
    assert ws.file_queue.up_button.isVisible()
    ws.show_tool(get_tool("compress"))
    assert not ws.file_queue.up_button.isVisible()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_redesign_ui.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.ui.widgets.tool_workspace'`.

- [ ] **Step 3: Add external-queue support to ToolPanelsStack**

In `src/ui/widgets/tool_panels.py`, add `self._external_queue = False` in `__init__` after `self._actions = []`. Then append this method after `set_files()`:

```python
    def set_external_queue(self, enabled: bool):
        """Hide the in-panel merge queue when ToolWorkspace supplies one."""
        self._external_queue = enabled
        for widget in getattr(self, "merge_queue_widgets", []):
            widget.setVisible(not enabled)
        self._update_panel_state()
```

In `_create_merge_panel()`, wrap the queue widgets into a container and set the widget list. Replace the section where `sec_header`, `btn_bar`, `merge_file_list`, and `merge_hint_label` are added with:

```python
        queue_box = QWidget()
        ql = QVBoxLayout(queue_box)
        ql.setContentsMargins(0, 0, 0, 0)
        ql.setSpacing(8)

        sec_header = QHBoxLayout()
        title_lbl = QLabel("Documents to Merge")
        title_lbl.setObjectName("SectionHeader")
        sec_header.addWidget(title_lbl)
        sec_header.addStretch()
        self.merge_count_label = QLabel("0 documents")
        self.merge_count_label.setObjectName("SectionLabel")
        sec_header.addWidget(self.merge_count_label)
        ql.addLayout(sec_header)

        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(8)
        add_btn = QPushButton("  Add PDFs…")
        add_btn.setObjectName("Secondary")
        add_btn.setIcon(get_icon("add", TEXT_1, 13))
        add_btn.clicked.connect(lambda: self.add_files_requested.emit())
        btn_bar.addWidget(add_btn)
        self.btn_merge_up = QPushButton("▲ Up")
        self.btn_merge_up.setObjectName("Secondary")
        self.btn_merge_up.clicked.connect(lambda: self._move_merge_item(-1))
        btn_bar.addWidget(self.btn_merge_up)
        self.btn_merge_down = QPushButton("▼ Down")
        self.btn_merge_down.setObjectName("Secondary")
        self.btn_merge_down.clicked.connect(lambda: self._move_merge_item(1))
        btn_bar.addWidget(self.btn_merge_down)
        self.btn_merge_remove = QPushButton("✕ Remove")
        self.btn_merge_remove.setObjectName("Secondary")
        self.btn_merge_remove.clicked.connect(self._remove_merge_item)
        btn_bar.addWidget(self.btn_merge_remove)
        self.btn_merge_clear = QPushButton("Clear")
        self.btn_merge_clear.setObjectName("Ghost")
        self.btn_merge_clear.clicked.connect(self._clear_merge_items)
        btn_bar.addWidget(self.btn_merge_clear)
        ql.addLayout(btn_bar)

        self.merge_file_list = QListWidget()
        self.merge_file_list.setObjectName("MergeFileList")
        self.merge_file_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.merge_file_list.setDefaultDropAction(Qt.MoveAction)
        self.merge_file_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.merge_file_list.setFrameShape(QFrame.NoFrame)
        self.merge_file_list.setMinimumHeight(130)
        self.merge_file_list.setMaximumHeight(210)
        self.merge_file_list.currentItemChanged.connect(
            lambda *_: self._update_merge_buttons_state()
        )
        self.merge_file_list.model().rowsMoved.connect(self._on_merge_rows_moved)
        ql.addWidget(self.merge_file_list)

        self.merge_hint_label = QLabel(
            "Add at least 2 PDF documents to merge. Drag items or use ▲ / ▼ to adjust merge sequence."
        )
        self.merge_hint_label.setObjectName("Hint")
        self.merge_hint_label.setWordWrap(True)
        ql.addWidget(self.merge_hint_label)

        self.merge_queue_widgets = [queue_box]
        layout.addWidget(queue_box)
```

In `_update_panel_state()`, change:

```python
        can_merge = len(self._files) >= 2 or has_file
```

to:

```python
        can_merge = len(self._files) >= 2 if self._external_queue else (len(self._files) >= 2 or has_file)
```

- [ ] **Step 4: Implement ToolWorkspace**

Create `src/ui/widgets/tool_workspace.py` with exactly:

```python
"""Task screen: file pickup on the left, options and preview on the right."""
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QScrollArea, QSplitter, QStackedWidget,
    QTabWidget, QVBoxLayout, QWidget
)

from src.ui.theme import TEXT_1, TEXT_2
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

        self.panels.operation_requested.connect(lambda op, params: self.operationRequested.emit(op, params))
        self.panels.validation_failed.connect(lambda msg: self.validationFailed.emit(msg))
        self.panels.add_files_requested.connect(lambda: self.browseRequested.emit())
        self.batch_view.status_message.connect(lambda msg, ms: self.statusMessage.emit(msg, ms))
        self.batch_view.files_produced.connect(lambda files: self.filesProduced.emit(files))

    def show_tool(self, spec):
        self.spec = spec
        self.drop_zone.set_spec(spec)
        self.file_queue.set_can_reorder(spec.key == "batch" or spec.input_mode == "multi_pdf")
        self.requirement_label.setText(self._requirement_text(spec))
        if spec.key == "batch":
            self.options_stack.setCurrentWidget(self.batch_view)
        else:
            self.panels.set_external_queue(spec.key == "merge")
            self.panels.show_tool(spec.panel_key or "")
            self.options_stack.setCurrentWidget(self.panels)
        self.tabs.setCurrentIndex(0)

    def set_files(self, files, active, image_paths=None):
        self.file_queue.set_files(files, active)
        self.panels.set_file(active)
        self.panels.set_files(files)
        if spec_key := (self.spec.key if self.spec else None):
            if spec_key != "batch":
                self.batch_view.set_files(files)
        self.preview_stack.setCurrentIndex(1 if active else 0)
        if active:
            self.preview.load_pdf(active)
        else:
            self.preview.load_pdf(None)
            return
        if image_paths is not None and self.spec and self.spec.input_mode == "multi_image":
            self.panels.img_list.clear()
            self.panels.img_list.addItems([str(p) for p in image_paths])

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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python tests/test_redesign_ui.py`
Expected: PASS for `test_tool_workspace`.

- [ ] **Step 6: Commit**

```bash
git add src/ui/widgets/tool_workspace.py src/ui/widgets/tool_panels.py tests/test_redesign_ui.py
git commit -m "feat: build tool workspace with options and preview tabs"
```

---

### Task 7: Rewire MainWindow shell

**Files:**
- Modify: `src/ui/main_window.py`
- Test: `tests/test_redesign_ui.py`, `tests/test_e2e_ui.py`, `tests/test_ui_check.py`

- [ ] **Step 1: Add failing shell tests**

Append to `tests/test_redesign_ui.py`:

```python
def test_main_window_shell():
    from PySide6.QtWidgets import QApplication, QPushButton
    from src.ui.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    win = MainWindow()
    assert win.findChild(QPushButton, "Sidebar") is None
    assert not hasattr(win, "sidebar")
    assert win.home_view is not None
    assert win.workspace is not None
    win._nav_to("merge")
    assert win.session.spec.key == "merge"
    assert win.content_stack.currentIndex() == 1
    win._nav_to("home")
    assert win.content_stack.currentIndex() == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_redesign_ui.py`
Expected: FAIL with `AssertionError` because `MainWindow` still has `sidebar`.

- [ ] **Step 3: Rewrite shell sections in MainWindow**

In `src/ui/main_window.py`:

1. Replace imports of `FileListWidget` with `HomeView`, `ToolWorkspace`, `ToolSession`, `get_tool`, `pdf_tools`.
2. Replace `NAV_ITEMS` block with nothing; `ToolRegistry` is the source.
3. In `__init__`, initialize `self.session = None`, `self._current_file = None`, `self.file_list = FileListWidget()` (hidden compatibility library), `self._build_ui()`, then `_go_home()`.
4. Replace `_build_ui()`, delete `_build_sidebar()`, replace `_build_header()`, replace `_build_content()`, delete `_build_home_view()`, delete `_build_tools_view()`, delete `_build_batch_view()`.
5. Add these methods with exactly this behavior:

```python
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
        self.back_button = QPushButton("← Home")
        self.back_button.setObjectName("Secondary")
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
        self.home_view.openRequested.connect(self._open_files)
        self.workspace.filesAddedRequested.connect(self._on_workspace_paths)
        self.workspace.browseRequested.connect(self._open_workspace_files)
        self.workspace.activeChanged.connect(self._on_session_active_changed)
        self.workspace.operationRequested.connect(self._run_operation)
        self.workspace.validationFailed.connect(self._show_validation_error)
        self.workspace.statusMessage.connect(
            lambda msg, ms: self.status.showMessage(msg, ms)
        )
        self.workspace.filesProduced.connect(self._add_outputs)
        self.content_stack.addWidget(self.home_view)     # 0
        self.content_stack.addWidget(self.workspace)     # 1
        return self.content_stack

    @property
    def current_file(self):
        return self.session.active_file if self.session else self._current_file

    @current_file.setter
    def current_file(self, pdf):
        self._current_file = pdf
        if self.session:
            self.session.active_file = pdf
        self.workspace.panels.set_file(pdf)

    # Compatibility aliases used by the existing test suite.
    @property
    def tool_panels(self):
        return self.workspace.panels

    @property
    def batch_view(self):
        return self.workspace.batch_view

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
        spec = get_tool(key)
        if spec is None or spec.key == "library":
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

    def _recent_paths(self):
        settings = QSettings("PDFToolkit", "PDFToolkit")
        recent = settings.value("recent_files", []) or []
        if isinstance(recent, str):
            recent = [recent]
        return [Path(p) for p in recent if Path(p).exists()]

    def _on_home_drop(self, paths):
        choices = [t for t in pdf_tools()]
        labels = [f"{t.label} ({len(paths)} PDF{'s' if len(paths) != 1 else ''})" for t in choices]
        label, ok = QInputDialog.getItem(
            self, "Choose a tool", f"Drop {len(paths)} PDF{'s' if len(paths) != 1 else ''} — choose a tool:",
            labels, 0, False
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
        else:
            loaded = [pdf for p in paths if p.suffix.lower() == ".pdf"
                      if (pdf := self._load_with_password(p)) is not None]
            accepted = self.session.add_pdfs(loaded)
            rejected = len(paths) - len(loaded) + len(loaded) - len(accepted)
            self.workspace.set_files(self.session.files, self.session.active_file)
        if accepted:
            self.tabs_settled()
        if rejected:
            self.status.showMessage(f"{rejected} file{'s' if rejected != 1 else ''} skipped", 4000)
        self._update_recent_files([p for p in paths if p.exists()])

    def tabs_settled(self):
        self.workspace.tabs.setCurrentIndex(0 if self.session.spec.input_mode != "none" else 0)
        self.status.showMessage(f"Added files for {self.session.spec.label}", 3000)

    def _on_session_active_changed(self, pdf):
        if not self.session:
            return
        self.session.set_active(pdf)
        self.workspace.set_files(self.session.files, self.session.active_file,
                                 self.session.image_paths)
        if pdf:
            self.workspace.show_preview()
            self._update_header()

    def _update_header(self):
        self.save_btn.setEnabled(self.current_file is not None)
```

6. Replace `_current_nav_key()` and `_update_tool_banner()` bodies to return `self.session.spec.key if self.session else None` and no-op respectively.
7. Replace the drop handlers at `dragEnterEvent`/`dropEvent` to delegate to the Home view: accept URLs and call `_on_home_drop(paths)` when Home is visible, otherwise `_on_workspace_paths(paths)`.
8. In `_run_operation()`, replace source selection with session-first logic:

```python
        session = self.session
        if op_name == "merge":
            sources = list(session.files) if session and session.files else list(self.files)
            if len(sources) < 2:
                QMessageBox.information(self, "Not enough files",
                                        "Add at least two PDFs to merge.")
                return
            worker = PdfWorker(PdfEngine.merge, sources, **params)
        elif op_name == "images_to_pdf":
            params = dict(params)
            if not params.get("image_paths") and session:
                params["image_paths"] = list(session.image_paths)
            worker = PdfWorker(PdfEngine.images_to_pdf, **params)
        else:
            source = (session.active_file if session and session.active_file else self.current_file)
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
```

Keep everything from `self._set_busy(True)` onward unchanged.
9. In `_setup_menu()`, change tools-menu triggers from `self._nav_to(k)` to `self._nav_to(k)` (unchanged) and keep `Ctrl+B` bound to `_nav_to("batch")`.
10. Delete `_deselect_current_file`, `_refresh_preview_empty_state`, `_refresh_tool_preview_empty_state`, `_on_nav_changed`, `_lookup_nav`, `_update_tool_banner`, `_sync_files`, `_on_files_reordered`, `_preview_action` if unreferenced; keep `_load_files()` legacy behavior (load into hidden `file_list`, sync `self.files`, call `_go_home()`).
11. Keep `_load_with_password`, `_clear_files`, worker methods, `_operation_done`, `_add_outputs`, `_operation_error`, `_save_current`, recents, help dialogs, and geometry methods unchanged.

- [ ] **Step 4: Run redesign tests**

Run: `python tests/test_redesign_ui.py`
Expected: PASS for `test_main_window_shell`.

- [ ] **Step 5: Run existing UI checks**

Run:
```bash
python tests/test_ui_check.py
python tests/test_ui_wiring.py
python tests/test_e2e_ui.py
python tests/test_flow_fixes.py
python tests/test_ui_operations.py
python tests/test_all_features.py
```
Expected: all scripts exit 0. Fix regressions before commit.

- [ ] **Step 6: Commit**

```bash
git add src/ui/main_window.py tests/test_redesign_ui.py
git commit -m "feat: replace sidebar shell with home grid and tool workspaces"
```

---

### Task 8: Add QSS for new widgets

**Files:**
- Modify: `src/ui/theme.py`

- [ ] **Step 1: Append new styles**

Before the final `"""` of `STYLESHEET` in `src/ui/theme.py`, append exactly:

```css
/* ---------- Redesign: Home Grid ---------- */
QFrame#HomeDropStrip[dropActive="true"], QFrame#DropZone[dropActive="true"] {{
    background: {PRIMARY_SOFT};
    border: 2px dashed {PRIMARY};
}}
QLabel#HomeTitle {{
    font-size: 26px;
    font-weight: 700;
    color: {TEXT_1};
}}
QLabel#HomeSubtitle {{
    font-size: 13px;
    color: {TEXT_2};
}}
QLabel#HomeSectionTitle {{
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: {TEXT_2};
    padding-top: 8px;
}}
QLabel#HomeRecent {{
    font-size: 12px;
    color: {TEXT_3};
}}
QPushButton#ToolCard {{
    background: {CANVAS_ELV};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: {RADIUS_LG}px;
    text-align: left;
    padding: 10px;
}}
QPushButton#ToolCard:hover {{
    background: {CANVAS_SOFT};
    border: 1px solid {PRIMARY};
}}
QPushButton#ToolCard:focus {{
    border: 1px solid {PRIMARY};
}}
QLabel#ToolCardIcon {{
    background: {PRIMARY_SOFT};
    border-radius: {RADIUS_MD}px;
    padding: 6px;
}}
QLabel#ToolCardArrow {{
    color: {TEXT_3};
    font-size: 16px;
}}
QLabel#ToolCardTitle {{
    font-size: 14px;
    font-weight: 600;
    color: {TEXT_1};
}}
QLabel#ToolCardDesc {{
    font-size: 12px;
    color: {TEXT_2};
}}

/* ---------- Redesign: Workspace ---------- */
QLabel#WorkspaceHint {{
    font-size: 13px;
    color: {TEXT_2};
    padding: 2px 0;
}}
QFrame#DropZone {{
    background: {CANVAS_ALT};
    border: 2px dashed {BORDER};
    border-radius: {RADIUS_LG}px;
}}
QLabel#DropZoneTitle {{
    font-size: 15px;
    font-weight: 600;
    color: {TEXT_1};
}}
QLabel#DropZoneSubtitle {{
    font-size: 12px;
    color: {TEXT_2};
}}
QWidget#FileQueue, QFrame#WorkspaceLeft {{
    background: transparent;
}}
QListWidget#FileQueueList {{
    background: {CANVAS_ALT};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: {RADIUS_MD}px;
    padding: 4px;
    outline: 0;
}}
QListWidget#FileQueueList::item {{
    background: {CANVAS_ELV};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: {RADIUS_SM}px;
    padding: 6px 10px;
    margin: 2px;
}}
QListWidget#FileQueueList::item:selected {{
    background: {PRIMARY_SOFT};
    border: 1px solid {PRIMARY};
}}
QFrame#SettingsPanel {{
    background: {CANVAS_ELV};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: {RADIUS_LG}px;
}}
QTabWidget#ToolTabs::tab {{
    padding: 8px 18px;
    color: {TEXT_2};
    font-weight: 600;
}}
QTabWidget#ToolTabs::tab:selected {{
    color: {TEXT_1};
    border-bottom: 2px solid {PRIMARY};
}}
```

- [ ] **Step 2: Verify theme loads**

Run: `python tests/test_redesign_ui.py`
Expected: PASS; no QSS parse errors printed to stderr.

- [ ] **Step 3: Commit**

```bash
git add src/ui/theme.py
git commit -m "style: add home grid, drop zone, and workspace styles"
```

---

### Task 9: Update docs and final verification

**Files:**
- Modify: `docs/USER_GUIDE.md`
- Test: all test scripts

- [ ] **Step 1: Replace wireframe in `docs/USER_GUIDE.md`**

Find the ASCII wireframe under "Interface Overview" (around lines 57–91) and replace it with:

```text
┌──────────────────────────────────────────────────────────────┐
│ PDF Toolkit   Everything you need for PDFs...      OFFLINE   │
├──────────────────────────────────────────────────────────────┤
│  Drop PDFs here to get started            [Browse files...]  │
│                                                              │
│  TOOLS                                                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                      │
│  │ Merge    │ │ Split    │ │ Rotate   │                      │
│  └──────────┘ └──────────┘ └──────────┘                      │
│  SECURITY / CONVERTER / AUTOMATION / LIBRARY                   │
└──────────────────────────────────────────────────────────────┘

After choosing a tool:

┌──────────────────────────────────────────────────────────────┐
│ ← Home   Merge   Combine multiple PDFs into one       ?      │
├───────────────────────────────┬──────────────────────────────┤
│ Add at least two PDFs         │ [ Options ] [ Preview ]      │
│ ┌───────────────────────────┐ │                              │
│ │ Drop PDFs here for Merge  │ │  Output destination          │
│ └───────────────────────────┘ │  ...                         │
│ 2 files        [Clear]        │                              │
│ 1. alpha.pdf                  │                              │
│ 2. beta.pdf                   │                              │
│ [▲ Up] [▼ Down] [✕ Remove]    │                              │
└───────────────────────────────┴──────────────────────────────┘
```

- [ ] **Step 2: Update workflow text**

Replace any sentence saying "select a tool from the sidebar" or "load PDFs in the Home library first" with: "Open a tool card on Home, then drop files into that tool's workspace."

- [ ] **Step 3: Run full verification**

Run:
```bash
python tests/test_redesign_ui.py
python tests/test_ui_check.py
python tests/test_ui_wiring.py
python tests/test_e2e_ui.py
python tests/test_flow_fixes.py
python tests/test_ui_operations.py
python tests/test_all_features.py
python -m compileall -q src
```
Expected: all exit 0.

- [ ] **Step 4: Manual smoke check**

Run `python src/main.py`. Verify: Home opens with no sidebar; grid shows sections; open Merge; drop two PDFs; Options tab active; reorder; merge; output appears in Output Library; Preview tab renders active file; Back returns Home.

- [ ] **Step 5: Commit**

```bash
git add docs/USER_GUIDE.md
git commit -m "docs: update user guide for home grid workflow"
```

---

## Self-review checklist

- [ ] Every spec requirement maps to a task: Home Grid (T5/T7), no sidebar (T7), fresh session (T3/T7), dropzone (T4/T6), right tabs (T6), session-based execute (T7), engine unchanged (all), tests pass (T7/T9).
- [ ] No placeholders (`TBD`, `TODO`, "fill in") remain in plan.
- [ ] Names consistent: `ToolSpec`, `ToolSession`, `DropZone`, `FileQueue`, `HomeView`, `ToolWorkspace`, `session`, `filesAddedRequested`, `activeChanged`.
