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
