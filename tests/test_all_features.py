"""Comprehensive feature test for PDF Toolkit engine + UI wiring."""
import sys
import tempfile
import traceback
from pathlib import Path

import pymupdf as fitz

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.pdf_engine import PdfEngine
from src.core.models import PdfFile


def make_pdf(path: Path, pages: int, label: str = "Test"):
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page(width=595, height=842)  # A4
        page.insert_text((72, 72), f"{label} page {i+1}", fontsize=24)
    doc.save(str(path))
    doc.close()
    return path


def make_image(path: Path, color, size=(400, 300)):
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, size[0], size[1]), False)
    pix.set_rect(pix.irect, color)
    pix.save(str(path))
    return path


def check(name, fn):
    try:
        result = fn()
        print(f"  [PASS] {name}: {result}")
        return True
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        traceback.print_exc()
        return False


def main():
    tmp = Path(tempfile.mkdtemp(prefix="pdftk_test_"))
    print(f"Test dir: {tmp}\n")

    results = {}

    # Fixtures
    a = make_pdf(tmp / "a.pdf", 3, "Alpha")
    b = make_pdf(tmp / "b.pdf", 2, "Beta")
    print(f"Created: a.pdf (3 pages), b.pdf (2 pages)\n")

    # 1. LOAD
    def t_load():
        pf = PdfEngine.load(a)
        assert pf.page_count == 3, f"expected 3 pages, got {pf.page_count}"
        return f"{pf.page_count} pages, {pf.size_mb:.2f} MB"
    results["load"] = check("load", t_load)

    # 2. MERGE
    def t_merge():
        out = tmp / "merged.pdf"
        pf = PdfEngine.merge([PdfEngine.load(a), PdfEngine.load(b)], out)
        assert pf.page_count == 5, f"expected 5 pages, got {pf.page_count}"
        return f"{pf.page_count} pages"
    results["merge"] = check("merge", t_merge)

    # 3. SPLIT (by ranges)
    def t_split():
        pf = PdfEngine.load(a)
        outdir = tmp / "split"
        outdir.mkdir(exist_ok=True)
        parts = PdfEngine.split(pf, [(0, 0), (1, 2)], outdir)
        assert len(parts) == 2, f"expected 2 parts, got {len(parts)}"
        assert parts[0].page_count == 1 and parts[1].page_count == 2
        return f"{len(parts)} parts (1p, 2p)"
    results["split"] = check("split", t_split)

    # 4. SPLIT BY PAGES
    def t_split_by_pages():
        pf = PdfEngine.load(a)
        outdir = tmp / "split_every"
        outdir.mkdir(exist_ok=True)
        parts = PdfEngine.split_by_pages(pf, every=1, output_dir=outdir)
        assert len(parts) == 3, f"expected 3 parts, got {len(parts)}"
        return f"{len(parts)} single-page files"
    results["split_by_pages"] = check("split_by_pages", t_split_by_pages)

    # 5. EXTRACT PAGES
    def t_extract():
        pf = PdfEngine.load(a)
        out = tmp / "extracted.pdf"
        res = PdfEngine.extract_pages(pf, [0, 2], out)
        assert res.page_count == 2, f"expected 2 pages, got {res.page_count}"
        return f"{res.page_count} pages"
    results["extract_pages"] = check("extract_pages", t_extract)

    # 6. ROTATE
    def t_rotate():
        pf = PdfEngine.load(a)
        out = tmp / "rotated.pdf"
        res = PdfEngine.rotate(pf, [0, 1, 2], 90, out)
        doc = fitz.open(str(out))
        rot = doc[0].rotation
        doc.close()
        assert rot == 90, f"expected rotation 90, got {rot}"
        return f"rotation={rot}"
    results["rotate"] = check("rotate", t_rotate)

    # 7. REORDER
    def t_reorder():
        pf = PdfEngine.load(a)
        out = tmp / "reordered.pdf"
        res = PdfEngine.reorder(pf, [2, 1, 0], out)
        assert res.page_count == 3
        return "reversed page order"
    results["reorder"] = check("reorder", t_reorder)

    # 8. WATERMARK
    def t_watermark():
        pf = PdfEngine.load(a)
        out = tmp / "watermarked.pdf"
        res = PdfEngine.add_watermark(pf, "CONFIDENTIAL", 0.3, out, font_size=48)
        # verify text present
        doc = fitz.open(str(out))
        txt = doc[0].get_text()
        doc.close()
        assert "CONFIDENTIAL" in txt, f"watermark text not found in: {txt!r}"
        return "watermark text verified on page 1"
    results["watermark"] = check("watermark", t_watermark)

    # 9. ENCRYPT
    def t_encrypt():
        pf = PdfEngine.load(a)
        out = tmp / "encrypted.pdf"
        res = PdfEngine.encrypt(pf, "userpass", "ownerpass", output_path=out)
        doc = fitz.open(str(out))
        needs = doc.needs_pass
        doc.close()
        assert needs, "encrypted PDF should need password"
        # verify correct password opens
        doc2 = fitz.open(str(out))
        ok = doc2.authenticate("userpass")
        doc2.close()
        assert ok, "userpass should authenticate"
        return "AES-256 encrypted, password verified"
    results["encrypt"] = check("encrypt", t_encrypt)

    # 10. DECRYPT
    def t_decrypt():
        enc = tmp / "encrypted.pdf"
        out = tmp / "decrypted.pdf"
        pf = PdfEngine.load(enc, "userpass")
        res = PdfEngine.decrypt(pf, "userpass", out)
        doc = fitz.open(str(out))
        needs = doc.needs_pass
        doc.close()
        assert not needs, "decrypted PDF should not need password"
        return "decrypted (no password needed)"
    results["decrypt"] = check("decrypt", t_decrypt)

    # 11. COMPRESS
    def t_compress():
        pf = PdfEngine.load(a)
        out = tmp / "compressed.pdf"
        res = PdfEngine.compress(pf, out, quality=75)
        assert out.exists()
        return f"{res.size_mb:.3f} MB"
    results["compress"] = check("compress", t_compress)

    # 12. TO IMAGES
    def t_to_images():
        pf = PdfEngine.load(b)
        outdir = tmp / "images"
        outdir.mkdir(exist_ok=True)
        paths = PdfEngine.to_images(pf, outdir, dpi=150, fmt="png")
        assert len(paths) == 2, f"expected 2 images, got {len(paths)}"
        for p in paths:
            assert p.exists() and p.stat().st_size > 0
        return f"{len(paths)} PNG files"
    results["to_images"] = check("to_images", t_to_images)

    # 13. IMAGES TO PDF
    def t_images_to_pdf():
        imgdir = tmp / "src_images"
        imgdir.mkdir(exist_ok=True)
        i1 = make_image(imgdir / "red.png", (255, 0, 0))
        i2 = make_image(imgdir / "green.png", (0, 255, 0))
        out = tmp / "from_images.pdf"
        res = PdfEngine.images_to_pdf([i1, i2], out)
        assert res.page_count == 2, f"expected 2 pages, got {res.page_count}"
        return f"{res.page_count} pages"
    results["images_to_pdf"] = check("images_to_pdf", t_images_to_pdf)

    # 14. THUMBNAIL
    def t_thumbnail():
        pf = PdfEngine.load(a)
        thumb = PdfEngine.get_thumbnail(pf, 0, (100, 100))
        assert len(thumb) > 100, "thumbnail too small"
        return f"{len(thumb)} bytes PNG"
    results["thumbnail"] = check("get_thumbnail", t_thumbnail)

    # Summary
    print("\n" + "=" * 50)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"RESULT: {passed}/{total} features passed")
    if passed < total:
        print("FAILED:", [k for k, v in results.items() if not v])
    print("=" * 50)
    return passed == total


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
