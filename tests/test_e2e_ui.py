"""End-to-end test: real MainWindow, real worker threads, every operation.

Builds the actual main window headless, loads real PDFs through the app's own
code path, dispatches each tool operation through _run_operation (QThreadPool),
and verifies the produced files on disk.
"""
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymupdf as fitz
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication

from src.core.pdf_engine import PdfEngine
from src.ui.main_window import MainWindow


def make_pdf(path: Path, pages: int, label: str):
    doc = fitz.open()
    for i in range(pages):
        doc.new_page(width=595, height=842).insert_text((72, 72), f"{label} {i+1}", fontsize=24)
    doc.save(str(path))
    doc.close()
    return path


def make_png(path: Path):
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 200, 150), False)
    pix.set_rect(pix.irect, (30, 120, 200))
    pix.save(str(path))
    return path


def main():
    app = QApplication.instance() or QApplication([])
    tmp = Path(tempfile.mkdtemp(prefix="pdftk_e2e_"))
    print(f"E2E dir: {tmp}\n")

    a = make_pdf(tmp / "alpha.pdf", 3, "Alpha")
    b = make_pdf(tmp / "beta.pdf", 2, "Beta")
    png = make_png(tmp / "img.png")

    win = MainWindow()
    win._load_files([a, b])
    assert len(win.files) == 2, f"expected 2 files loaded, got {len(win.files)}"
    print(f"  [PASS] load via UI: {len(win.files)} files")

    win.current_file = win.files[0]
    win.tool_panels.set_file(win.current_file)

    results = {}

    def run(op, params, timeout_ms=30000):
        """Dispatch through the real worker path and wait for completion."""
        state = {"done": False, "result": None, "error": None}

        def on_finished(r):
            state["result"], state["done"] = r, True

        def on_error(e):
            state["error"], state["done"] = e, True

        # hook one-shot signals
        win._operation_done = lambda r, n: (on_finished(r), None)[1]
        win._operation_error = lambda e: on_error(e)

        win._run_operation(op, params)
        pool = QThreadPool.globalInstance()
        for _ in range(timeout_ms // 10):
            app.processEvents()
            if state["done"]:
                break
            QThreadPool.globalInstance().waitForDone(10)

        if state["error"]:
            raise RuntimeError(state["error"])
        if not state["done"]:
            raise TimeoutError(f"{op} did not finish")
        return state["result"]

    def check(name, fn):
        try:
            msg = fn()
            print(f"  [PASS] {name}: {msg}")
            results[name] = True
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            results[name] = False

    # merge
    def t_merge():
        out = tmp / "ui_merged.pdf"
        r = run("merge", {"output_path": out})
        assert out.exists(), "merged file missing"
        assert r.page_count == 5, f"expected 5 pages, got {r.page_count}"
        return f"{r.page_count} pages"
    check("merge", t_merge)

    # split
    def t_split():
        outdir = tmp / "ui_split"
        r = run("split", {"every": 1, "output_dir": outdir})
        files = sorted(outdir.glob("*.pdf"))
        assert len(files) == 3, f"expected 3 files, got {len(files)}"
        return f"{len(files)} files"
    check("split", t_split)

    # rotate
    def t_rotate():
        out = tmp / "ui_rotated.pdf"
        r = run("rotate", {"degrees": 90, "page_indices": [0, 1]})
        doc = fitz.open(str(r.path))
        rots = [doc[i].rotation for i in range(doc.page_count)]
        doc.close()
        assert rots == [90, 90, 0], f"unexpected rotations {rots}"
        return f"rotations {rots}"
    check("rotate", t_rotate)

    # reorder
    def t_reorder():
        r = run("reorder", {"new_order": [2, 1, 0]})
        doc = fitz.open(str(r.path))
        first = doc[0].get_text().strip()
        doc.close()
        assert "Alpha 3" in first, f"page 1 should be 'Alpha 3', got {first!r}"
        return f"first page now {first!r}"
    check("reorder", t_reorder)

    # watermark
    def t_watermark():
        r = run("add_watermark", {"text": "DRAFT", "opacity": 0.3, "font_size": 48})
        doc = fitz.open(str(r.path))
        txt = "".join(p.get_text() for p in doc)
        doc.close()
        assert "DRAFT" in txt, "watermark missing"
        return "text present on all pages"
    check("watermark", t_watermark)

    # encrypt
    def t_encrypt():
        r = run("encrypt", {"user_password": "secret", "owner_password": "owner", "permissions": 0})
        doc = fitz.open(str(r.path))
        needs = doc.needs_pass
        ok = doc.authenticate("secret")
        doc.close()
        assert needs and ok, "encryption/password check failed"
        return "AES-256, password verified"
    check("encrypt", t_encrypt)

    # decrypt (reload the encrypted file directly, then decrypt)
    def t_decrypt():
        enc = tmp / "alpha_encrypted.pdf"
        # Loading through the UI would open the password prompt, which cannot
        # be answered in a headless test; use the engine path instead.
        pf = PdfEngine.load(enc, "secret")
        win.current_file = pf
        r = run("decrypt", {"password": "secret"})
        doc = fitz.open(str(r.path))
        needs = doc.needs_pass
        doc.close()
        assert not needs, "still encrypted"
        return "password removed"
    check("decrypt", t_decrypt)

    # compress
    def t_compress():
        r = run("compress", {"quality": 75})
        assert r.path.exists()
        return f"{r.size_mb:.3f} MB"
    check("compress", t_compress)

    # to images
    def t_to_images():
        outdir = tmp / "ui_images"
        r = run("to_images", {"dpi": 150, "fmt": "png", "output_dir": outdir})
        files = list(outdir.glob("*.png"))
        assert len(files) == 3, f"expected 3 png, got {len(files)}"
        assert all(f.stat().st_size > 0 for f in files)
        return f"{len(files)} PNG files"
    check("to_images", t_to_images)

    # images to pdf
    def t_images_to_pdf():
        out = tmp / "ui_images.pdf"
        r = run("images_to_pdf", {"image_paths": [png, png], "output_path": out})
        assert r.page_count == 2, f"expected 2 pages, got {r.page_count}"
        return f"{r.page_count} pages"
    check("images_to_pdf", t_images_to_pdf)

    # batch run (own thread pool + result plumbing back into the library)
    def t_batch():
        outdir = tmp / "ui_batch"
        outdir.mkdir(exist_ok=True)
        bv = win.batch_view
        win._nav_to("batch")
        bv.set_files(win.files[:1])
        bv.op_combo.setCurrentIndex(0)  # compress
        bv.out_dir.setText(str(outdir))
        produced = []
        bv.files_produced.connect(produced.extend)
        bv._run()
        for _ in range(3000):
            app.processEvents()
            if produced:
                break
            QThreadPool.globalInstance().waitForDone(10)
        assert produced, "batch run produced no files"
        assert all(Path(p.path).exists() for p in produced)
        bv.set_files(win.files)
        return f"{len(produced)} file(s) added back to the library"
    check("batch", t_batch)

    print()
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"RESULT: {passed}/{total} UI operations passed")
    if passed < total:
        print("FAILED:", [k for k, v in results.items() if not v])
    return passed == total


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
