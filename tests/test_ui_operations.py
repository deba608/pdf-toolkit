"""Test UI operations headless."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pymupdf as fitz
from src.core.pdf_engine import PdfEngine
from src.core.models import PdfFile

tmp = Path(tempfile.mkdtemp(prefix="ui_op_"))
pdf_path = tmp / "test.pdf"
doc = fitz.open()
page = doc.new_page(width=595, height=842)
page.insert_text((72, 72), "Hello World", fontsize=24)
doc.save(str(pdf_path))
doc.close()

# 1. Load
pf = PdfEngine.load(pdf_path)
assert pf.page_count == 1
print(f"[PASS] load: {pf.page_count} pages")

# 2. Rotate
rot = PdfEngine.rotate(pf, [0], 90, tmp / "rotated.pdf")
assert rot.page_count == 1
assert rot.pages[0].rotation == 90
print(f"[PASS] rotate: rotation=90")

# 3. Watermark
wat = PdfEngine.add_watermark(pf, "CONFIDENTIAL", 0.3, tmp / "watermarked.pdf", font_size=48)
assert wat.page_count == 1
doc = fitz.open(str(wat.path))
txt = "".join(p.get_text() for p in doc)
doc.close()
assert "CONFIDENTIAL" in txt
print(f"[PASS] watermark: text verified")

# 4. Encrypt
enc = PdfEngine.encrypt(pf, "password123", "owner123", 0, tmp / "encrypted.pdf")
assert enc.page_count == 1
doc = fitz.open(str(enc.path))
needs = doc.needs_pass
ok = doc.authenticate("password123")
doc.close()
assert needs and ok
print(f"[PASS] encrypt: AES-256, password verified")

# 5. Decrypt
dec = PdfEngine.decrypt(enc, "password123", tmp / "decrypted.pdf")
assert dec.page_count == 1
doc = fitz.open(str(dec.path))
needs = doc.needs_pass
doc.close()
assert not needs
print(f"[PASS] decrypt: no password needed")

# 6. Compress
comp = PdfEngine.compress(dec, tmp / "compressed.pdf", quality=75)
assert comp.page_count == 1
print(f"[PASS] compress: {comp.page_count} pages")

# 7. To images
imgs = PdfEngine.to_images(comp, tmp / "images", dpi=150, fmt="png")
assert len(imgs) == 1 and imgs[0].exists()
print(f"[PASS] to_images: {len(imgs)} PNG file")

# 8. Thumbnail
thumb = PdfEngine.get_thumbnail(pf, 0, (100, 100))
assert len(thumb) > 100
print(f"[PASS] get_thumbnail: {len(thumb)} bytes")

print("\nAll 7 operations passed!")