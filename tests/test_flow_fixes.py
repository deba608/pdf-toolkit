"""Regression tests for the end-to-end flow fixes.

Covers the bugs that made the UI and engine disagree:

* 1-based page input mapped to the wrong (off-by-one) page indices,
* invalid page text raising an uncaught exception inside a Qt slot,
* an operation silently overwriting its own source file,
* ``PdfFile.is_encrypted`` reporting False for encrypted files opened with
  a password,
* ``quality`` being ignored by compression,
* duplicate files being added to the library twice.
"""
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymupdf as fitz
from PySide6.QtWidgets import QApplication, QPushButton

from src.core.models import PdfFile
from src.core.pdf_engine import PdfEngine
from src.ui.widgets.tool_panels import ToolPanelsStack, _parse_page_list


def make_pdf(path: Path, pages: int = 3) -> Path:
    doc = fitz.open()
    for i in range(pages):
        doc.new_page(width=595, height=842).insert_text(
            (72, 72), f"page {i + 1}", fontsize=20
        )
    doc.save(str(path))
    doc.close()
    return path


def make_noisy_pdf(path: Path) -> Path:
    """A PDF with a large high-DPI noise image, so compression has work to do."""
    width = height = 900
    samples = os.urandom(width * height * 3)
    pix = fitz.Pixmap(fitz.csRGB, width, height, samples, 0)
    doc = fitz.open()
    page = doc.new_page(width=150, height=150)  # 900px over 150pt = 432 dpi
    page.insert_image(page.rect, pixmap=pix)
    doc.save(str(path))
    doc.close()
    return path


def main() -> bool:
    app = QApplication.instance() or QApplication([])
    tmp = Path(tempfile.mkdtemp(prefix="pdftk_fixes_"))
    results: dict[str, bool] = {}

    def check(name, fn):
        try:
            msg = fn()
            print(f"  [PASS] {name}: {msg}")
            results[name] = True
        except Exception as exc:  # noqa: BLE001
            print(f"  [FAIL] {name}: {exc}")
            results[name] = False

    # ---------- page list parsing ----------
    def t_parse_basic():
        assert _parse_page_list("1,3-4", 4) == [0, 2, 3]
        assert _parse_page_list("", 4) is None
        assert _parse_page_list("2", 4, zero_based=True) == [2]
        return "1-based input converts to 0-based indices"

    def t_parse_invalid():
        for bad in ("abc", "5-2", "1-", "-3", "1,,x"):
            try:
                _parse_page_list(bad, 4)
            except ValueError:
                continue
            raise AssertionError(f"{bad!r} should have been rejected")
        try:
            _parse_page_list("9", 4)
        except ValueError:
            return "bad text and out-of-range pages raise ValueError"
        raise AssertionError("out-of-range page should have been rejected")

    # ---------- reorder panel wiring ----------
    def t_reorder_panel():
        pdf = PdfEngine.load(make_pdf(tmp / "reorder.pdf", 3))
        stack = ToolPanelsStack()
        stack.set_file(pdf)
        stack.show_tool("reorder")
        stack.reorder_order.setText("3,1,2")
        captured = {}
        stack.operation_requested.connect(
            lambda name, params: captured.update(name=name, params=params)
        )
        buttons = stack.panels["reorder"].findChildren(QPushButton)
        buttons[-1].click()
        app.processEvents()
        assert captured.get("name") == "reorder", captured
        order = captured["params"]["new_order"]
        assert order == [2, 0, 1], f"expected [2, 0, 1], got {order}"
        return f"new_order={order}"

    def t_reorder_validation():
        pdf = PdfEngine.load(make_pdf(tmp / "reorder_bad.pdf", 3))
        stack = ToolPanelsStack()
        stack.set_file(pdf)
        stack.show_tool("reorder")
        stack.reorder_order.setText("5-2")
        errors, ops = [], []
        stack.validation_failed.connect(errors.append)
        stack.operation_requested.connect(lambda n, p: ops.append(n))
        stack.panels["reorder"].findChildren(QPushButton)[-1].click()
        app.processEvents()
        assert errors, "invalid input should emit validation_failed"
        assert not ops, "invalid input must not start an operation"
        return f"message: {errors[0]}"

    # ---------- engine safety ----------
    def t_no_overwrite_source():
        src = make_pdf(tmp / "keep.pdf", 2)
        pdf = PdfEngine.load(src)
        try:
            PdfEngine.compress(pdf, output_path=src)
        except ValueError as exc:
            assert "overwrite" in str(exc).lower(), exc
            assert src.exists() and PdfEngine.load(src).page_count == 2
            return "refused to overwrite the input file"
        raise AssertionError("compress overwrote its own source")

    def t_encrypted_flag():
        src = make_pdf(tmp / "flag.pdf", 1)
        out = tmp / "flag_encrypted.pdf"
        PdfEngine.encrypt(PdfEngine.load(src), "pw", output_path=out)
        opened = PdfEngine.load(out, "pw")
        assert opened.is_encrypted, "encrypted file must report is_encrypted"
        assert opened.password == "pw"
        try:
            PdfEngine.load(out, "wrong")
        except ValueError as exc:
            assert "incorrect password" in str(exc).lower()
            return "is_encrypted=True; wrong password rejected"
        raise AssertionError("wrong password was accepted")

    def t_compress_quality():
        src = make_noisy_pdf(tmp / "noisy.pdf")
        pdf = PdfEngine.load(src)
        low = PdfEngine.compress(pdf, tmp / "low.pdf", quality=20)
        high = PdfEngine.compress(pdf, tmp / "high.pdf", quality=90)
        assert low.path.stat().st_size < src.stat().st_size, "no size reduction"
        assert low.path.stat().st_size < high.path.stat().st_size, (
            f"quality=20 ({low.path.stat().st_size}) should be smaller than "
            f"quality=90 ({high.path.stat().st_size})"
        )
        return (
            f"{src.stat().st_size // 1024} KB -> "
            f"q20 {low.path.stat().st_size // 1024} KB, "
            f"q90 {high.path.stat().st_size // 1024} KB"
        )

    def t_size_mb_missing():
        pdf = PdfEngine.load(make_pdf(tmp / "gone.pdf", 1))
        pdf.path.unlink()
        assert pdf.size_mb == 0.0
        return "missing file reports 0.0 MB instead of raising"

    # ---------- library de-duplication ----------
    def t_dedupe():
        from src.ui.main_window import MainWindow
        a = make_pdf(tmp / "dedupe.pdf", 1)
        win = MainWindow()
        win._load_files([a])
        win._load_files([a])
        assert len(win.files) == 1, f"expected 1 file, got {len(win.files)}"
        win.close()
        return "same path added once"

    check("parse_page_list", t_parse_basic)
    check("parse_page_list invalid", t_parse_invalid)
    check("reorder panel mapping", t_reorder_panel)
    check("reorder validation", t_reorder_validation)
    check("no source overwrite", t_no_overwrite_source)
    check("encrypted flag", t_encrypted_flag)
    check("compress quality", t_compress_quality)
    check("size_mb missing file", t_size_mb_missing)
    check("library dedupe", t_dedupe)

    passed = sum(results.values())
    print(f"\nRESULT: {passed}/{len(results)} flow checks passed")
    if passed != len(results):
        print("FAILED:", [k for k, v in results.items() if not v])
    return passed == len(results)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
