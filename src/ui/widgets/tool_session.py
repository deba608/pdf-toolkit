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
        if self.spec.input_mode not in ("single_pdf", "multi_pdf"):
            return []
        if self.spec.input_mode == "single_pdf":
            if self.files or not pdfs:
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
