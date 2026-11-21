# PDF Toolkit

Offline desktop application for all PDF operations. Built with Python, PySide6, and PyMuPDF.

## Features

- **Merge**: Combine multiple PDFs into one
- **Split**: Split by page ranges or every N pages
- **Rotate**: Rotate pages 90°, 180°, 270°
- **Reorder**: Drag-drop to reorder pages
- **Watermark**: Add text watermarks with opacity/size control
- **Encrypt/Decrypt**: AES-256 encryption with permissions
- **Compress**: Reduce file size (image downsampling, garbage collection)
- **Convert**: PDF ↔ Images (PNG/JPG), Images → PDF
- **OCR**: (Planned) Make scanned PDFs searchable

## Requirements

- Python 3.10+
- Windows 10/11 (primary target), also works on macOS/Linux

## Installation

```bash
cd pdf-toolkit
pip install -r requirements.txt
```

## Run

```bash
python src/main.py
```

## Build Standalone Executable

```bash
pip install pyinstaller
python build.py
```

Output: `dist/PDF Toolkit.exe` (~60 MB, no dependencies)

## Project Structure

```
pdf-toolkit/
├── src/
│   ├── main.py                 # Entry point
│   ├── core/
│   │   ├── models.py           # Data classes (PdfFile, PdfPage, Job)
│   │   └── pdf_engine.py       # PyMuPDF wrapper (all operations)
│   ├── ui/
│   │   ├── main_window.py      # Main window, tabs, menu, toolbar
│   │   └── widgets/
│   │       ├── file_list.py    # Draggable file/page list
│   │       ├── preview.py      # PDF.js viewer in QWebEngine
│   │       ├── tool_panels.py  # Per-tool parameter panels
│   │       └── progress.py     # Job queue + progress
│   └── resources/              # Icons, viewer.html
├── build.py                    # PyInstaller builder
├── requirements.txt
└── README.md
```

## Tech Stack

| Component | Library |
|-----------|---------|
| GUI Framework | PySide6 (Qt6) |
| PDF Engine | PyMuPDF (fitz) |
| Preview | PDF.js via QWebEngineView |
| Packaging | PyInstaller |

## License

MIT