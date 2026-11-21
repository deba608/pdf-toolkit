import pymupdf as fitz
from pathlib import Path
from typing import List, Optional, Tuple
from .models import PdfFile, PdfPage


class PdfEngine:
    @staticmethod
    def load(filepath: Path, password: Optional[str] = None) -> PdfFile:
        doc = fitz.open(str(filepath))
        if doc.needs_pass:
            if password:
                if not doc.authenticate(password):
                    raise ValueError("Incorrect password")
            else:
                raise ValueError("PDF is encrypted, password required")

        pages = []
        for i in range(doc.page_count):
            page = doc[i]
            pages.append(PdfPage(
                index=i,
                width=page.rect.width,
                height=page.rect.height,
                rotation=page.rotation
            ))

        pdf_file = PdfFile(
            path=filepath,
            name=filepath.name,
            page_count=doc.page_count,
            pages=pages,
            metadata=doc.metadata or {},
            is_encrypted=doc.needs_pass,
            password=password
        )
        doc.close()
        return pdf_file

    @staticmethod
    def merge(files: List[PdfFile], output_path: Path = None) -> PdfFile:
        if output_path is None:
            output_path = files[0].path.parent / "merged.pdf"
        merged = fitz.open()
        for pf in files:
            doc = fitz.open(str(pf.path))
            if pf.password:
                doc.authenticate(pf.password)
            merged.insert_pdf(doc)
            doc.close()
        merged.save(str(output_path))
        merged.close()
        return PdfEngine.load(output_path)

    @staticmethod
    def split(file: PdfFile, ranges: List[Tuple[int, int]], output_dir: Path = None) -> List[PdfFile]:
        if output_dir is None:
            output_dir = file.path.parent
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        results = []
        doc = fitz.open(str(file.path))
        if file.password:
            doc.authenticate(file.password)

        for i, (start, end) in enumerate(ranges):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start, to_page=end)
            out_path = output_dir / f"{file.path.stem}_part{i+1}.pdf"
            new_doc.save(str(out_path))
            new_doc.close()
            results.append(PdfEngine.load(out_path))

        doc.close()
        return results

    @staticmethod
    def extract_pages(file: PdfFile, page_indices: List[int], output_path: Path = None) -> PdfFile:
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_extracted.pdf")
        doc = fitz.open(str(file.path))
        if file.password:
            doc.authenticate(file.password)

        new_doc = fitz.open()
        for idx in page_indices:
            new_doc.insert_pdf(doc, from_page=idx, to_page=idx)
        new_doc.save(str(output_path))
        new_doc.close()
        doc.close()
        return PdfEngine.load(output_path)

    @staticmethod
    def rotate(file: PdfFile, page_indices: Optional[List[int]] = None, degrees: int = 90,
               output_path: Path = None) -> PdfFile:
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_rotated.pdf")
        doc = fitz.open(str(file.path))
        if file.password:
            doc.authenticate(file.password)

        if page_indices is None:
            page_indices = list(range(doc.page_count))

        for idx in page_indices:
            page = doc[idx]
            page.set_rotation((page.rotation + degrees) % 360)

        doc.save(str(output_path))
        doc.close()
        return PdfEngine.load(output_path)

    @staticmethod
    def reorder(file: PdfFile, new_order: Optional[List[int]] = None,
                output_path: Path = None) -> PdfFile:
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_reordered.pdf")
        doc = fitz.open(str(file.path))
        if file.password:
            doc.authenticate(file.password)

        if new_order is None:
            new_order = list(range(doc.page_count))
        invalid = [i for i in new_order if i < 0 or i >= doc.page_count]
        if invalid:
            raise ValueError(f"Page indices out of range 0-{doc.page_count - 1}: {invalid}")

        new_doc = fitz.open()
        for idx in new_order:
            new_doc.insert_pdf(doc, from_page=idx, to_page=idx)
        new_doc.save(str(output_path))
        new_doc.close()
        doc.close()
        return PdfEngine.load(output_path)

    @staticmethod
    def add_watermark(file: PdfFile, text: str, opacity: float = 0.3, output_path: Path = None,
                      font_size: int = 48, color: Tuple[float, float, float] = (0.5, 0.5, 0.5)) -> PdfFile:
        if not text.strip():
            raise ValueError("Watermark text cannot be empty")
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_watermarked.pdf")
        doc = fitz.open(str(file.path))
        if file.password:
            doc.authenticate(file.password)

        for page in doc:
            rect = page.rect
            fontsize = font_size
            tw = fitz.get_text_length(text, fontsize=fontsize, fontname="helv")
            x = (rect.width - tw) / 2
            y = (rect.height + fontsize) / 2

            page.insert_text(
                (x, y), text,
                fontsize=fontsize,
                fontname="helv",
                color=color,
                fill_opacity=opacity,
                overlay=True
            )

        doc.save(str(output_path))
        doc.close()
        return PdfEngine.load(output_path)

    @staticmethod
    def encrypt(file: PdfFile, user_password: str, owner_password: Optional[str] = None,
                permissions: int = 0, output_path: Path = None) -> PdfFile:
        if not user_password:
            raise ValueError("User password cannot be empty")
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_encrypted.pdf")
        doc = fitz.open(str(file.path))
        if file.password:
            doc.authenticate(file.password)

        if not owner_password:
            owner_password = user_password

        doc.save(
            str(output_path),
            encryption=fitz.PDF_ENCRYPT_AES_256,
            user_pw=user_password,
            owner_pw=owner_password,
            permissions=permissions
        )
        doc.close()
        return PdfEngine.load(output_path, user_password)

    @staticmethod
    def decrypt(file: PdfFile, password: str = "", output_path: Path = None) -> PdfFile:
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_decrypted.pdf")
        doc = fitz.open(str(file.path))
        if doc.needs_pass and not doc.authenticate(password or file.password or ""):
            raise ValueError("Incorrect password")

        doc.save(str(output_path), encryption=fitz.PDF_ENCRYPT_NONE)
        doc.close()
        return PdfEngine.load(output_path)

    @staticmethod
    def to_images(file: PdfFile, output_dir: Path = None, dpi: int = 200,
                  fmt: str = "png", page_indices: Optional[List[int]] = None) -> List[Path]:
        if output_dir is None:
            output_dir = file.path.parent
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        fmt = fmt.lower().lstrip(".")
        if fmt == "jpeg":
            fmt = "jpg"
        if fmt not in ("png", "jpg"):
            raise ValueError(f"Unsupported image format: {fmt}")
        doc = fitz.open(str(file.path))
        if file.password:
            doc.authenticate(file.password)

        paths = []
        pages = page_indices if page_indices else range(doc.page_count)
        mat = fitz.Matrix(dpi / 72, dpi / 72)

        for i in pages:
            page = doc[i]
            pix = page.get_pixmap(matrix=mat)
            out_path = output_dir / f"{file.path.stem}_page{i+1}.{fmt}"
            pix.save(str(out_path))
            paths.append(out_path)

        doc.close()
        return paths

    @staticmethod
    def images_to_pdf(image_paths: List[Path], output_path: Path = None) -> PdfFile:
        if output_path is None:
            output_path = image_paths[0].parent / "images.pdf"
        doc = fitz.open()
        for img_path in image_paths:
            img = fitz.open(str(img_path))
            rect = img[0].rect
            page = doc.new_page(width=rect.width, height=rect.height)
            page.insert_image(rect, filename=str(img_path))
            img.close()
        doc.save(str(output_path))
        doc.close()
        return PdfEngine.load(output_path)

    @staticmethod
    def compress(file: PdfFile, output_path: Path = None, quality: int = 75) -> PdfFile:
        if output_path is None:
            output_path = file.path.with_name(f"{file.path.stem}_compressed.pdf")
        doc = fitz.open(str(file.path))
        if file.password:
            doc.authenticate(file.password)

        # quality is kept for API symmetry; PyMuPDF losslessly cleans/compresses
        doc.save(str(output_path), garbage=4, deflate=True, clean=True)
        doc.close()
        return PdfEngine.load(output_path)

    @staticmethod
    def get_thumbnail(file: PdfFile, page_index: int, size: Tuple[int, int] = (200, 200)) -> bytes:
        doc = fitz.open(str(file.path))
        if file.password:
            doc.authenticate(file.password)

        page = doc[page_index]
        mat = fitz.Matrix(size[0] / page.rect.width, size[1] / page.rect.height)
        pix = page.get_pixmap(matrix=mat)
        thumb = pix.tobytes("png")
        doc.close()
        return thumb

    @staticmethod
    def split_by_pages(file: PdfFile, every: int, output_dir: Path = None) -> List[PdfFile]:
        """Split PDF into multiple files, each with 'every' pages."""
        if output_dir is None:
            output_dir = file.path.parent
        ranges = []
        for i in range(0, file.page_count, every):
            ranges.append((i, min(i + every - 1, file.page_count - 1)))
        return PdfEngine.split(file, ranges, output_dir)