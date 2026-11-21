# PDF Toolkit

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-6.12-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.28-FF6B35?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-0078D4?style=for-the-badge&logo=windows&logoColor=white)
![Build](https://img.shields.io/badge/Build-PyInstaller-FF69B4?style=for-the-badge)

**A powerful, offline-first desktop application for all your PDF needs.**

[Features](#-features) • [Screenshots](#-screenshots) • [Installation](#-installation) • [Usage](#-usage) • [Building](#-building-standalone-executable) • [Architecture](#-architecture) • [Contributing](#-contributing) • [License](#-license)

</div>

---

## 🎯 Overview

PDF Toolkit is a **completely offline** desktop application built with Python, Qt6 (PySide6), and PyMuPDF. It provides a comprehensive suite of PDF manipulation tools without ever sending your documents to the cloud. Perfect for handling sensitive documents, working in air-gapped environments, or simply avoiding upload limits.

### Why PDF Toolkit?

| ❌ **Online Tools** | ✅ **PDF Toolkit** |
|---------------------|-------------------|
| Upload sensitive docs to unknown servers | 100% local processing — never leaves your machine |
| File size limits (often 10-50 MB) | No limits — limited only by your RAM/disk |
| Requires internet connection | Works fully offline / air-gapped |
| Privacy concerns | Zero telemetry, zero tracking, zero accounts |
| Paywalls for advanced features | Completely free, open source (MIT) |

---

## ✨ Features

### 📄 Core Operations
| Feature | Description |
|---------|-------------|
| **Merge** | Combine multiple PDFs into a single document with drag-drop reordering |
| **Split** | Split by page ranges, every N pages, or extract specific pages |
| **Rotate** | Rotate pages 90°, 180°, or 270° (individual or batch) |
| **Reorder** | Drag-and-drop page reordering with live preview |

### 🎨 Content & Appearance
| Feature | Description |
|---------|-------------|
| **Watermark** | Add customizable text watermarks (opacity, font size, color, position) |
| **Page Numbers** | Add Bates-style numbering with prefixes/suffixes |
| **Headers/Footers** | Custom text, dates, page numbers on every page |

### 🔒 Security
| Feature | Description |
|---------|-------------|
| **Encrypt** | AES-256 encryption with user/owner passwords |
| **Permissions** | Granular control: print, copy, modify, annotate, form filling, accessibility |
| **Decrypt** | Remove passwords and restrictions (with valid password) |

### 📦 Optimization & Conversion
| Feature | Description |
|---------|-------------|
| **Compress** | Reduce file size via image downsampling, deduplication, garbage collection |
| **Linearize** | Fast web view (byte-serving) for large PDFs |
| **PDF → Images** | Export pages as PNG/JPG at configurable DPI (72–600) |
| **Images → PDF** | Combine multiple images (PNG, JPG, BMP, TIFF) into a PDF |
| **OCR** *(planned)* | Make scanned PDFs searchable with Tesseract |

### 🖥️ User Experience
- **Dark/Light themes** with system preference detection
- **Drag & drop** files directly into the window
- **Keyboard shortcuts** for power users
- **Progress tracking** for long-running operations
- **Recent files** with quick access
- **Multi-language** support (extensible i18n)

---

## 📸 Screenshots

> **Note**: Screenshots will be added after first release. The UI follows modern Qt Material design principles.

| Files Tab | Tools Tab | Merge Panel | Split Panel |
|-----------|-----------|-------------|-------------|
| ![Files](docs/screenshots/files-tab.png) | ![Tools](docs/screenshots/tools-tab.png) | ![Merge](docs/screenshots/merge.png) | ![Split](docs/screenshots/split.png) |

| Encrypt Panel | Compress Panel | Preview | Dark Mode |
|---------------|----------------|---------|-----------|
| ![Encrypt](docs/screenshots/encrypt.png) | ![Compress](docs/screenshots/compress.png) | ![Preview](docs/screenshots/preview.png) | ![Dark](docs/screenshots/dark.png) |

---

## 🚀 Installation

### Prerequisites
- **Python 3.10+** (3.11+ recommended)
- **Windows 10/11**, **macOS 11+**, or **Linux** (Ubuntu 22.04+, Fedora 38+, Arch)

### From Source (Development)
```bash
# Clone the repository
git clone https://github.com/deba608/pdf-toolkit.git
cd pdf-toolkit

# Create virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run the application
python -m src.main
```

### Standalone Executable (No Python Required)
Download the latest release from the [Releases page](https://github.com/deba608/pdf-toolkit/releases):

| Platform | File | Size |
|----------|------|------|
| Windows x64 | `PDF_Toolkit_Windows_x64.exe` | ~65 MB |
| macOS (Apple Silicon) | `PDF_Toolkit_macOS_arm64.dmg` | ~70 MB |
| Linux x64 | `PDF_Toolkit_Linux_x64.AppImage` | ~75 MB |

> **Windows SmartScreen**: Since the app isn't code-signed, you may see "Windows protected your PC". Click "More info" → "Run anyway". This is normal for open-source unsigned binaries.

---

## 📖 Usage

### Quick Start
1. **Launch** the application
2. **Drag & drop** one or more PDF files into the window (or use `Ctrl+O`)
3. **Select** a tool from the **Tools** tab or **Tools** menu
4. **Configure** parameters in the left panel
5. **Click** the action button (Merge, Split, Encrypt, etc.)
6. **Save** the result via `Ctrl+S` or the toolbar

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open PDF(s) |
| `Ctrl+S` | Save current document |
| `Ctrl+Shift+S` | Save As... |
| `Ctrl+W` | Close current tab |
| `Ctrl+Q` / `Ctrl+F4` | Quit application |
| `F11` | Toggle fullscreen |
| `Ctrl++` / `Ctrl+-` | Zoom in/out (preview) |
| `Ctrl+0` | Reset zoom |
| `Delete` | Remove selected file from list |

### Common Workflows

#### Merge Multiple PDFs
```
Files tab → Drag 3+ PDFs → Reorder by dragging → Tools tab → Merge → Set output path → Merge
```

#### Split a Large PDF
```
Files tab → Open large.pdf → Tools tab → Split → "Every 10 pages" → Choose output folder → Split
```

#### Add Confidential Watermark
```
Files tab → Open document → Tools tab → Watermark → Text: "CONFIDENTIAL" → Opacity: 30% → Size: 60 → Add Watermark
```

#### Encrypt for Secure Sharing
```
Files tab → Open document → Tools tab → Encrypt → User Password: [strong] → Owner Password: [different] → Permissions: "Allow printing only" → Encrypt
```

---

## 🔨 Building Standalone Executable

### Requirements
```bash
pip install pyinstaller
```

### Build Command
```bash
# Windows
python build.py

# macOS (creates .app bundle)
python build.py --macos

# Linux (creates AppImage)
python build.py --linux
```

### Build Output
```
dist/
├── PDF Toolkit.exe          # Windows (~65 MB)
├── PDF Toolkit.app/         # macOS (~70 MB)
└── PDF Toolkit/             # Linux (~75 MB)
```

### Customization
Edit `build.py` to:
- Change app name, version, icon
- Add/remove hidden imports
- Configure code signing (Windows/macOS)
- Create installers (NSIS, DMG, DEB/RPM)

---

## 🏗️ Architecture

```
pdf-toolkit/
├── src/
│   ├── main.py                    # Application entry point
│   ├── core/
│   │   ├── models.py              # Data models (PdfFile, PdfPage, Job)
│   │   ├── pdf_engine.py          # PyMuPDF wrapper — all PDF operations
│   │   └── commands.py            # Command pattern for undo/redo
│   ├── ui/
│   │   ├── main_window.py         # MainWindow, tabs, menus, toolbar
│   │   ├── theme.py               # Dark/light theme management
│   │   ├── shortcuts.py           # Keyboard shortcut registry
│   │   └── widgets/
│   │       ├── file_list.py       # Draggable file/page list widget
│   │       ├── preview.py         # PDF.js viewer in QWebEngineView
│   │       ├── tool_panels.py     # Parameter panels for each tool
│   │       ├── progress.py        # Job queue with progress tracking
│   │       └── dialogs.py         # Password, save-as, settings dialogs
│   └── resources/
│       ├── icons/                 # SVG icons (Material Design)
│       ├── viewer.html            # PDF.js viewer template
│       └── themes/                # QSS stylesheets
├── tests/                         # pytest + pytest-qt test suite
├── build.py                       # PyInstaller build script
├── requirements.txt               # Python dependencies
├── LICENSE                        # MIT License
└── README.md                      # This file
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **GUI Framework** | PySide6 (Qt 6.12) | Native cross-platform widgets, high-DPI, accessibility |
| **PDF Engine** | PyMuPDF (fitz) 1.28 | Fast, comprehensive PDF manipulation (C backend) |
| **Preview** | PDF.js 4.x + QWebEngineView | Faithful rendering, zoom, search, text selection |
| **Threading** | QThreadPool + QRunnable | Non-blocking UI during heavy operations |
| **Packaging** | PyInstaller | Single-file executables, no dependencies |
| **Testing** | pytest + pytest-qt | Unit + integration tests with Qt event loop |

### Design Principles

1. **Offline-First**: Zero network calls. No telemetry. No auto-updates (manual only).
2. **Performance**: Stream processing for large files; background threads for all I/O.
3. **Safety**: Never modify originals — always write to new paths.
4. **Privacy**: No analytics, no crash reporting, no phone-home.
5. **Accessibility**: WCAG 2.1 AA — keyboard nav, screen readers, high contrast.
6. **Extensibility**: Command pattern + plugin-ready tool registry.

---

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run GUI tests (requires display)
pytest tests/ui/ -v

# Type checking
mypy src/
```

### Test Structure
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_pdf_engine.py
│   └── test_commands.py
├── integration/
│   ├── test_merge.py
│   ├── test_split.py
│   └── test_encrypt.py
└── ui/
    ├── test_main_window.py
    └── test_tool_panels.py
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Quick Contribution Guide
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'feat: add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run linting
ruff check src/
black src/
mypy src/
```

### Code Style
- **Formatting**: Black (line length 100)
- **Linting**: Ruff
- **Type Hints**: Required for all public APIs (mypy strict)
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, etc.)

---

## 🗺️ Roadmap

### v1.1 (Next Release)
- [ ] OCR integration (Tesseract)
- [ ] Batch processing queue
- [ ] Settings persistence (QSettings)
- [ ] Custom keyboard shortcuts
- [ ] Page thumbnails in file list

### v1.2
- [ ] Digital signatures (sign/verify)
- [ ] Form filling & flattening
- [ ] Bookmark/outline editor
- [ ] Metadata editor (full XMP)

### v2.0
- [ ] Plugin system (Python scripts)
- [ ] Command-line interface (CLI)
- [ ] WebAssembly build (browser version)
- [ ] Mobile companion (Android/iOS)

---

## 🐛 Known Issues

| Issue | Status | Workaround |
|-------|--------|------------|
| WebEngine may not render on some Linux Wayland compositors | Investigating | Use X11 session or set `QT_QPA_PLATFORM=xcb` |
| Large PDFs (>500 MB) may cause memory pressure | By design | Split first, then process |
| Encrypted PDFs with unknown encryption handlers | PyMuPDF limitation | Decrypt with Adobe Acrobat first |

Report new issues at [GitHub Issues](https://github.com/deba608/pdf-toolkit/issues).

---

## 🙏 Acknowledgments

- **[PyMuPDF](https://pymupdf.readthedocs.io/)** — Incredible PDF engine by Artifex
- **[PDF.js](https://mozilla.github.io/pdf.js/)** — Mozilla's PDF viewer
- **[PySide6](https://wiki.qt.io/Qt_for_Python)** — Qt for Python by The Qt Company
- **[Material Design Icons](https://fonts.google.com/icons)** — Google Fonts icons

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 deba608

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support & Links

| Resource | Link |
|----------|------|
| **Repository** | https://github.com/deba608/pdf-toolkit |
| **Issues / Bug Reports** | https://github.com/deba608/pdf-toolkit/issues |
| **Discussions** | https://github.com/deba608/pdf-toolkit/discussions |
| **Releases** | https://github.com/deba608/pdf-toolkit/releases |
| **Security Policy** | https://github.com/deba608/pdf-toolkit/security/policy |

---

<div align="center">

**Made with ❤️ for privacy-conscious PDF users everywhere.**

⭐ **Star this repo** if you find it useful!

</div>