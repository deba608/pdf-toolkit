"""UI wiring test: every tool panel's emitted params must bind to the engine call.

Runs headless (QT_QPA_PLATFORM=offscreen), clicks each panel's action button and
checks the payload against the real engine signature - catches the class of bug
where a panel emits keys the engine does not accept.
"""
import inspect
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymupdf as fitz
from PySide6.QtWidgets import QApplication, QPushButton

from src.core.pdf_engine import PdfEngine
from src.ui.widgets.tool_panels import ToolPanelsStack

# tool panel name -> (operation signal name, engine attribute name)
ENGINE_FOR_TOOL = {
    "merge": ("merge", "merge"),
    "split": ("split", "split_by_pages"),
    "rotate": ("rotate", "rotate"),
    "reorder": ("reorder", "reorder"),
    "watermark": ("add_watermark", "add_watermark"),
    "encrypt": ("encrypt", "encrypt"),
    "decrypt": ("decrypt", "decrypt"),
    "compress": ("compress", "compress"),
    "to images": ("to_images", "to_images"),
    "images to pdf": ("images_to_pdf", "images_to_pdf"),
}


def make_pdf(path: Path, pages: int = 3):
    doc = fitz.open()
    for i in range(pages):
        doc.new_page(width=595, height=842).insert_text((72, 72), f"page {i+1}", fontsize=20)
    doc.save(str(path))
    doc.close()
    return path


def make_png(path: Path):
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 120, 90), False)
    pix.set_rect(pix.irect, (200, 60, 60))
    pix.save(str(path))
    return path


def main():
    app = QApplication.instance() or QApplication([])
    tmp = Path(tempfile.mkdtemp(prefix="pdftk_ui_"))
    pdf_path = make_pdf(tmp / "doc.pdf", 3)
    png_path = make_png(tmp / "img.png")

    stack = ToolPanelsStack()
    stack.set_file(PdfEngine.load(pdf_path))

    captured = {}
    stack.operation_requested.connect(lambda name, params: captured.__setitem__(name, params))

    failures = []
    for tool, (op_name, engine_name) in ENGINE_FOR_TOOL.items():
        stack.show_tool(tool)
        panel = stack.stack.currentWidget()

        buttons = [b for b in panel.findChildren(QPushButton) if b.isEnabled()]
        if not buttons:
            failures.append(f"{tool}: no button found")
            continue

        # Fill required inputs so the payload is realistic
        if tool == "watermark":
            stack.wm_text.setText("CONFIDENTIAL")
        if tool == "encrypt":
            stack.enc_user_pw.setText("pw123")
        if tool == "rotate":
            stack.rotate_pages.setText("1-2")
        if tool == "reorder":
            stack.reorder_order.setText("3,1,2")
        if tool == "images to pdf":
            stack.img_list.addItem(str(png_path))

        target = buttons[-1] if tool not in ("images to pdf",) else buttons[-1]
        target.click()
        app.processEvents()

        if op_name not in captured:
            failures.append(f"{tool}: no operation_requested emitted")
            continue

        params = captured[op_name]
        fn = getattr(PdfEngine, engine_name)

        if tool == "merge":
            args = ([stack.current_file, stack.current_file],)
        elif tool == "images to pdf":
            args = ()
        else:
            args = (stack.current_file,)

        try:
            sig = inspect.signature(fn)
            sig.bind(*args, **params)
            print(f"  [PASS] {tool:14s} -> {engine_name}{_fmt(params)}")
        except TypeError as e:
            failures.append(f"{tool} -> {engine_name}: {e}")
            print(f"  [FAIL] {tool:14s} -> {engine_name}: {e}")

    print()
    if failures:
        print(f"RESULT: {len(failures)} wiring failure(s)")
        for f in failures:
            print("  -", f)
        return False
    print(f"RESULT: all {len(ENGINE_FOR_TOOL)} tool panels wire to engine correctly")
    return True


def _fmt(params):
    return "(" + ", ".join(f"{k}={v!r}" for k, v in params.items()) + ")"


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
