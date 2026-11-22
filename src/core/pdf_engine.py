"""PDF operations built on PyMuPDF.

Every method follows the same contract:

* inputs are never modified — output always goes to a different path
  (:func:`PdfEngine._guard_output` enforces this),
* encrypted inputs are opened with the password stored on the ``PdfFile``
  (or an explicit one), and a clear ``ValueError`` is raised when it is
  missing or wrong,
* documents are always closed, even when an operation fails.
"""
from pathlib import Path
from typing import List, Optional, Tuple

import pymupdf as fitz

from .models import PdfFile, PdfPage

# Permission bits accepted by PyMuPDF's ``save(permissions=...)``.
PERM_PRINT = fitz.PDF_PERM_PRINT | fitz.PDF_PERM_PRINT_HQ
PERM_MODIFY = fitz.PDF_PERM_MODIFY
PERM_COPY = fitz.PDF_PERM_COPY
PERM_ANNOTATE = fitz.PDF_PERM_ANNOTATE
PERM_FORM = fitz.PDF_PERM_FORM
PERM_ACCESSIBILITY = fitz.PDF_PERM_ACCESSIBILITY
PERM_ASSEMBLE = fitz.PDF_PERM_ASSEMBLE
PERM_ALL = (
    PERM_PRINT | PERM_MODIFY | PERM_COPY | PERM_ANNOTATE
    | PERM_FORM | PERM_ACCESSIBILITY | PERM_ASSEMBLE
)


class PdfEngine:
    # ---------- internals ----------
    @staticmethod
    def _open(file: PdfFile, password: Optional[str] = None) -> "fitz.Document":
        """Open ``file`` and authenticate it, closing it again on failure."""
        doc = fitz.open(str(file.path))
        pw = password if password is not None else file.password
        if doc.needs_pass:
            if not pw:
                doc.close()
                raise ValueError(f"{file.name} is encrypted — a password is required")
            if not doc.authenticate(pw):
                doc.close()
                raise ValueError("Incorrect password")
        return doc

    @staticmethod
    def _guard_output(output_path: Path, sources) -> Path:
        """Refuse to write over an input file and make sure the folder exists."""
        out = Path(output_path).expanduser()
        resolved = out.resolve()
        for src in sources:
            if Path(src).resolve() == resolved:
                raise ValueError(
                    f"Refusing to overwrite the source file “{out.name}”. "
                    "Choose a different output name."
                )
        out.parent.mkdir(parents=True, exist_ok=True)
        return out

    # ---------- load ----------
    @staticmethod
    def load(filepath: Path, password: Optional[str] = None) -> PdfFile:
        filepath = Path(filepath)
        if not filepath.exists():
            raise ValueError(f"File not found: {filepath}")
        doc = fitz.open(str(filepath))
        try:
            if doc.needs_pass:
                if not password:
                    raise ValueError("PDF is encrypted, password required")
                if not doc.authenticate(password):
                    raise ValueError("Incorrect password")

            pages = [
                PdfPage(
                    index=i,
                    width=doc[i].rect.width,
                    height=doc[i].rect.height,
                    rotation=doc[i].rotation,
                )
                for i in range(doc.page_count)
            ]

            return PdfFile(
                path=filepath,
                name=filepath.name,
                page_count=doc.page_count,
                pages=pages,
                metadata=doc.metadata or {},
                # ``needs_pass`` stays True after authenticating, so use
                # ``is_encrypted`` (does the file carry encryption at all).
                is_encrypted=bool(doc.is_encrypted),
                password=password,
            )
        finally:
            doc.close()

    # ---------- combine / split ----------
    @staticmethod
    def merge(files: List[PdfFile], output_path: Path = None) -> PdfFile:
        if not files:
            raise ValueError("No files to merge")
        if output_path is None:
            output_path = files[0].path.parent / "merged.pdf"
        output_path = PdfEngine._guard_output(output_path, [f.path for f in files])

        merged = fitz.open()
        try:
            for pf in files:
                src = PdfEngine._open(pf)
                try:
                    merged.insert_pdf(src)
                finally:
                    src.close()
            merged.save(str(output_path), garbage=4, deflate=True)
        finally:
            merged.close()
        return PdfEngine.load(output_path)

    @staticmethod
    def split(file: PdfFile, ranges: List[Tuple[int, int]],
              output_dir: Path = None) -> List[PdfFile]:
        if not ranges:
            raise ValueError("No page ranges to split")
        output_dir = Path(output_dir or file.path.parent)
        output_dir.mkdir(parents=True, exist_ok=True)

        doc = PdfEngine._open(file)
        results: List[PdfFile] = []
        try:
            for i, (start, end) in enumerate(ranges):
                if start < 0 or end >= doc.page_count or end < start:
                    raise ValueError(
                        f"Invalid page range {start + 1}-{end + 1} "
                        f"for a {doc.page_count}-page document"
                    )
                new_doc = fitz.open()
                try:
                    new_doc.insert_pdf(doc, from_page=start, to_page=end)
                    out_path = output_dir / f"{file.path.stem}_part{i + 1}.pdf"
                    new_doc.save(str(out_path), garbage=4, deflate=True)
                finally:
                    new_doc.close()
                results.append(PdfEngine.load(out_path))
        finally:
            doc.close()
        return results

    @staticmethod
    def split_by_pages(file: PdfFile, every: int, output_dir: Path = None) -> List[PdfFile]:
        """Split into files of at most ``every`` pages."""
        if every < 1:
            raise ValueError("Pages per file must be at least 1")
        ranges = [
            (i, min(i + every - 1, file.page_count - 1))
            for i in range(0, file.page_count, every)
        ]
        return PdfEngine.split(file, ranges, output_dir)

    @staticmethod
    def extract_pages(file: PdfFile, page_indices: List[int],
                      output_path: Path = None) -> PdfFile:
        if not page_indices:
            raise ValueError("No pages selected")
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_extracted.pdf")
        output_path = PdfEngine._guard_output(output_path, [file.path])

        doc = PdfEngine._open(file)
        new_doc = fitz.open()
        try:
            for idx in page_indices:
                if idx < 0 or idx >= doc.page_count:
                    raise ValueError(
                        f"Page {idx + 1} is out of range 1-{doc.page_count}"
                    )
                new_doc.insert_pdf(doc, from_page=idx, to_page=idx)
            new_doc.save(str(output_path), garbage=4, deflate=True)
        finally:
            new_doc.close()
            doc.close()
        return PdfEngine.load(output_path)

    # ---------- page layout ----------
    @staticmethod
    def rotate(file: PdfFile, page_indices: Optional[List[int]] = None, degrees: int = 90,
               output_path: Path = None) -> PdfFile:
        if degrees % 90 != 0:
            raise ValueError("Rotation must be a multiple of 90 degrees")
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_rotated.pdf")
        output_path = PdfEngine._guard_output(output_path, [file.path])

        doc = PdfEngine._open(file)
        try:
            pages = list(range(doc.page_count)) if page_indices is None else page_indices
            for idx in pages:
                if idx < 0 or idx >= doc.page_count:
                    raise ValueError(f"Page {idx + 1} is out of range 1-{doc.page_count}")
                page = doc[idx]
                page.set_rotation((page.rotation + degrees) % 360)
            doc.save(str(output_path), garbage=4, deflate=True)
        finally:
            doc.close()
        return PdfEngine.load(output_path)

    @staticmethod
    def reorder(file: PdfFile, new_order: Optional[List[int]] = None,
                output_path: Path = None) -> PdfFile:
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_reordered.pdf")
        output_path = PdfEngine._guard_output(output_path, [file.path])

        doc = PdfEngine._open(file)
        try:
            order = list(range(doc.page_count)) if new_order is None else new_order
            if not order:
                raise ValueError("New page order cannot be empty")
            invalid = [i for i in order if i < 0 or i >= doc.page_count]
            if invalid:
                raise ValueError(
                    f"Page indices out of range 1-{doc.page_count}: "
                    + ", ".join(str(i + 1) for i in invalid)
                )

            new_doc = fitz.open()
            try:
                for idx in order:
                    new_doc.insert_pdf(doc, from_page=idx, to_page=idx)
                new_doc.save(str(output_path), garbage=4, deflate=True)
            finally:
                new_doc.close()
        finally:
            doc.close()
        return PdfEngine.load(output_path)

    # ---------- content ----------
    @staticmethod
    def add_watermark(file: PdfFile, text: str, opacity: float = 0.3,
                      output_path: Path = None, font_size: int = 48,
                      color: Tuple[float, float, float] = (0.5, 0.5, 0.5)) -> PdfFile:
        if not text.strip():
            raise ValueError("Watermark text cannot be empty")
        if not 0.0 < opacity <= 1.0:
            raise ValueError("Opacity must be between 0 and 1")
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_watermarked.pdf")
        output_path = PdfEngine._guard_output(output_path, [file.path])

        doc = PdfEngine._open(file)
        try:
            for page in doc:
                rect = page.rect
                tw = fitz.get_text_length(text, fontsize=font_size, fontname="helv")
                page.insert_text(
                    ((rect.width - tw) / 2, (rect.height + font_size) / 2),
                    text,
                    fontsize=font_size,
                    fontname="helv",
                    color=color,
                    fill_opacity=opacity,
                    overlay=True,
                )
            doc.save(str(output_path), garbage=4, deflate=True)
        finally:
            doc.close()
        return PdfEngine.load(output_path)

    # ---------- security ----------
    @staticmethod
    def encrypt(file: PdfFile, user_password: str, owner_password: Optional[str] = None,
                permissions: int = PERM_ALL, output_path: Path = None) -> PdfFile:
        if not user_password:
            raise ValueError("User password cannot be empty")
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_encrypted.pdf")
        output_path = PdfEngine._guard_output(output_path, [file.path])

        doc = PdfEngine._open(file)
        try:
            doc.save(
                str(output_path),
                encryption=fitz.PDF_ENCRYPT_AES_256,
                user_pw=user_password,
                owner_pw=owner_password or user_password,
                permissions=permissions,
                garbage=4,
                deflate=True,
            )
        finally:
            doc.close()
        return PdfEngine.load(output_path, user_password)

    @staticmethod
    def decrypt(file: PdfFile, password: str = "", output_path: Path = None) -> PdfFile:
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_decrypted.pdf")
        output_path = PdfEngine._guard_output(output_path, [file.path])

        doc = PdfEngine._open(file, password or file.password)
        try:
            doc.save(str(output_path), encryption=fitz.PDF_ENCRYPT_NONE,
                     garbage=4, deflate=True)
        finally:
            doc.close()
        return PdfEngine.load(output_path)

    # ---------- conversion ----------
    @staticmethod
    def to_images(file: PdfFile, output_dir: Path = None, dpi: int = 200,
                  fmt: str = "png", page_indices: Optional[List[int]] = None) -> List[Path]:
        if dpi < 36 or dpi > 1200:
            raise ValueError("DPI must be between 36 and 1200")
        fmt = fmt.lower().lstrip(".")
        if fmt == "jpeg":
            fmt = "jpg"
        if fmt not in ("png", "jpg"):
            raise ValueError(f"Unsupported image format: {fmt}")

        output_dir = Path(output_dir or file.path.parent)
        output_dir.mkdir(parents=True, exist_ok=True)

        doc = PdfEngine._open(file)
        paths: List[Path] = []
        try:
            pages = list(range(doc.page_count)) if page_indices is None else page_indices
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            for i in pages:
                if i < 0 or i >= doc.page_count:
                    raise ValueError(f"Page {i + 1} is out of range 1-{doc.page_count}")
                pix = doc[i].get_pixmap(matrix=mat)
                out_path = output_dir / f"{file.path.stem}_page{i + 1}.{fmt}"
                if fmt == "jpg":
                    pix.save(str(out_path), jpg_quality=90)
                else:
                    pix.save(str(out_path))
                paths.append(out_path)
        finally:
            doc.close()
        return paths

    @staticmethod
    def images_to_pdf(image_paths: List[Path], output_path: Path = None) -> PdfFile:
        if not image_paths:
            raise ValueError("Add at least one image")
        missing = [str(p) for p in image_paths if not Path(p).exists()]
        if missing:
            raise ValueError("Image not found: " + ", ".join(missing))
        if output_path is None:
            output_path = Path(image_paths[0]).parent / "images.pdf"
        output_path = PdfEngine._guard_output(output_path, image_paths)

        doc = fitz.open()
        try:
            for img_path in image_paths:
                img = fitz.open(str(img_path))
                try:
                    rect = img[0].rect
                finally:
                    img.close()
                page = doc.new_page(width=rect.width, height=rect.height)
                page.insert_image(rect, filename=str(img_path))
            doc.save(str(output_path), garbage=4, deflate=True)
        finally:
            doc.close()
        return PdfEngine.load(output_path)

    # ---------- optimization ----------
    @staticmethod
    def _analyze_pdf(file: PdfFile) -> dict:
        """Inspect content so ``compress(quality=-1)`` can pick a sensible level."""
        doc = PdfEngine._open(file)
        try:
            analysis = {
                "has_images": False,
                "has_text": False,
                "image_count": 0,
                "page_count": doc.page_count,
                "recommended_quality": 75,
            }
            for page in doc:
                if page.get_text().strip():
                    analysis["has_text"] = True
                imgs = page.get_images()
                if imgs:
                    analysis["has_images"] = True
                    analysis["image_count"] += len(imgs)

            if analysis["has_images"] and not analysis["has_text"]:
                # Scanned document: aggressive downsampling is safe.
                analysis["recommended_quality"] = 50
            elif analysis["has_text"] and not analysis["has_images"]:
                analysis["recommended_quality"] = 85
            elif analysis["has_images"] and analysis["has_text"]:
                analysis["recommended_quality"] = 70
            else:
                analysis["recommended_quality"] = 90
            return analysis
        finally:
            doc.close()

    @staticmethod
    def compress(file: PdfFile, output_path: Path = None, quality: int = 75) -> PdfFile:
        """Downsample/re-encode images and clean the file structure.

        ``quality`` is the JPEG quality used for re-encoded images (1-100).
        Pass ``-1`` to let the content analysis choose.
        """
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_compressed.pdf")
        output_path = PdfEngine._guard_output(output_path, [file.path])

        if quality is not None and quality < 0:
            quality = PdfEngine._analyze_pdf(file)["recommended_quality"]
        quality = max(1, min(100, int(quality or 75)))

        doc = PdfEngine._open(file)
        try:
            # 150 dpi keeps print quality while removing camera/scanner excess.
            target_dpi = 150 if quality >= 60 else 110
            try:
                doc.rewrite_images(
                    dpi_threshold=target_dpi,
                    dpi_target=target_dpi,
                    quality=quality,
                    lossy=True,
                    lossless=True,
                )
            except Exception:
                # Some malformed images cannot be rewritten; still ship the
                # lossless cleanup rather than failing the whole operation.
                pass
            try:
                doc.subset_fonts()
            except Exception:
                pass
            doc.save(str(output_path), garbage=4, deflate=True, clean=True)
        finally:
            doc.close()
        return PdfEngine.load(output_path)

    @staticmethod
    def linearize(file: PdfFile, output_path: Path = None) -> PdfFile:
        """Save a linearized ("fast web view") copy of the PDF."""
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_linearized.pdf")
        output_path = PdfEngine._guard_output(output_path, [file.path])

        doc = PdfEngine._open(file)
        try:
            doc.save(str(output_path), linear=True, garbage=4, deflate=True)
        finally:
            doc.close()
        return PdfEngine.load(output_path)

    @staticmethod
    def get_thumbnail(file: PdfFile, page_index: int,
                      size: Tuple[int, int] = (200, 200)) -> bytes:
        doc = PdfEngine._open(file)
        try:
            if page_index < 0 or page_index >= doc.page_count:
                raise ValueError(f"Page {page_index + 1} is out of range")
            page = doc[page_index]
            mat = fitz.Matrix(size[0] / page.rect.width, size[1] / page.rect.height)
            return page.get_pixmap(matrix=mat).tobytes("png")
        finally:
            doc.close()
