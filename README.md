# PDF Toolkit

<div align="center">

<img src="assets/logo.png" alt="PDF Toolkit logo" width="140" />

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-6.7%2B-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.23%2B-FF6B35?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-0078D4?style=for-the-badge&logo=windows&logoColor=white)
![Build](https://img.shields.io/badge/Build-PyInstaller-FF69B4?style=for-the-badge)

**A powerful, offline-first desktop application for all your PDF needs.**

[Features](#-features) • [Screenshots](#-screenshots) • [Installation](#-installation) • [Usage](#-usage) • [User Guide](docs/USER_GUIDE.md) • [Building](#-building-standalone-executable) • [Architecture](#-architecture) • [Contributing](#-contributing) • [License](#-license)

</div>

---

## About

**PDF Toolkit** is an open-source, offline-first desktop PDF utility for Windows, macOS, and Linux. It brings common PDF workflows into one local app: merge, split, rotate, reorder, watermark, encrypt/decrypt, compress, and convert between PDFs and images. Built with Python, PySide6, and PyMuPDF, it pairs a Vite-inspired dark UI with local processing — no cloud upload, telemetry, or account requirement.

## 🎯 Overview

PDF Toolkit is a **completely offline** desktop application built with Python, Qt6 (PySide6), and PyMuPDF. It provides a suite of PDF manipulation tools in a Vite-inspired dark interface without ever sending your documents to the cloud. Perfect for handling sensitive documents, working in air-gapped environments, or simply avoiding upload limits.

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
| **Merge** | Combine multiple PDFs into a single document, in library order |
| **Split** | Split into chunks of N pages |
| **Rotate** | Rotate selected pages (or all) by 90°, 180°, or 270° |
| **Reorder** | Rearrange or drop pages by entering a new 1-based order |

### 🎨 Content & Appearance
| Feature | Description |
|---------|-------------|
| **Watermark** | Add customizable text watermarks (opacity, font size, colour) |

### 🔒 Security
| Feature | Description |
|---------|-------------|
| **Encrypt** | AES-256 encryption with user/owner passwords |
| **Permissions** | Three presets: no permissions, allow printing, allow all |
| **Decrypt** | Remove passwords and restrictions (with valid password) |

### 📦 Optimization & Conversion
| Feature | Description |
|---------|-------------|
| **Compress** | Image downsampling/re-encoding plus lossless cleanup |
| **PDF → Images** | Export pages as PNG/JPG at configurable DPI (72–600) |
| **Images → PDF** | Combine multiple images (PNG, JPG, BMP, TIFF) into a PDF |
| **Batch run** | Apply one operation to every loaded PDF with per-file status |
| **OCR** *(planned)* | Make scanned PDFs searchable with Tesseract |

### 🖥️ User Experience
- **Vite-inspired dark theme** — charcoal surfaces, indigo accents, Inter-style typography
- **Drag & drop** files directly into the window, drag to reorder
- **Native PDF preview** (QtPdf) — offline, zoomable, password-aware
- **Keyboard shortcuts** for power users
- **Progress tracking** for long-running operations
- **Background threading** so the UI never blocks

---

## 📸 Screenshots

> Screenshots are not committed yet. Run the app to see the Home, Tools, and
> Batch views; the UI uses a single dark theme with a sidebar and card layout.

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

| Platform | Build | File |
|----------|-------|------|
| Windows x64 | Fast (`rebuild.ps1`) | `dist\PDF Toolkit.exe` |
| Windows x64 | Release (`build.py --release` / `rebuild.ps1 release`) | `dist\PDF Toolkit.exe` |

Only Windows binaries are produced today. The source runs anywhere PySide6
and PyMuPDF are available; macOS/Linux packaging is not set up yet.

> **Windows SmartScreen**: Since the app isn't code-signed, you may see "Windows protected your PC". Click "More info" → "Run anyway". This is normal for open-source unsigned binaries.

---

## 📖 Usage

### Quick Start
1. **Launch** the application
2. **Drag & drop** one or more PDF files into the window (or use `Ctrl+O`)
3. **Select** a tool from the sidebar or the **Tools** menu
4. **Configure** parameters in the left panel
5. **Click** the action button (Merge, Split, Encrypt, etc.)
6. The result is added to the library and selected — use **Save As…** for a copy

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open PDF(s) |
| `Ctrl+S` | Save a copy of the selected PDF |
| `Ctrl+Shift+S` | Save a copy (same dialog) |
| `Ctrl+B` | Open batch processing |
| `Ctrl++` / `Ctrl+-` | Zoom preview in/out |
| `Ctrl+0` | Reset preview zoom |
| `Delete` | Remove selected file from the library |
| `F1` | Show the shortcut list |
| `Ctrl+Q` | Quit application |

### Common Workflows

#### Merge Multiple PDFs
```
Home → Add 3+ PDFs → Drag rows into order → Sidebar: Merge → Set output path → Merge PDFs
```

#### Split a Large PDF
```
Home → Open large.pdf → Sidebar: Split → "Pages per file" (e.g. 10) → Choose output folder → Split PDF
```

#### Add Confidential Watermark
```
Home → Open document → Sidebar: Watermark → Text: "CONFIDENTIAL" → Opacity: 0.3 → Size: 48 → Add Watermark
```

#### Encrypt for Secure Sharing
```
Home → Open document → Sidebar: Encrypt → User Password: [strong] → Owner Password: [different] → Permissions: "Allow printing only" → Encrypt PDF
```

---

## 🔨 Building Standalone Executable

### Requirements
```bash
pip install pyinstaller
```

### Build Commands
```bash
# Fast incremental dev build — frozen spec, one-file exe
python -m PyInstaller -y "PDF Toolkit.spec"
./rebuild.ps1

# Full clean one-file release build
python build.py --release
./rebuild.ps1 release
```

`python build.py` with no flags still uses PyInstaller's onedir mode; use the
frozen spec or a wrapper script for the fast one-file output. After changing
imports, resources, or exclusions, regenerate the static spec:

```bash
python freeze_spec.py    # rewrites PDF Toolkit.spec
```

### Build Output
```
dist/
├── PDF Toolkit.exe              # frozen-spec fast build / release build
└── PDF Toolkit/
    └── PDF Toolkit.exe          # only from bare `python build.py` (onedir)
```

Version metadata is generated from `src/__version__.py`: on Windows,
`build.py --release` rewrites `version.txt`, which the frozen spec reads.
Bump the version there before building.

### What gets bundled
Only the Qt modules the app imports (`QtCore`, `QtGui`, `QtWidgets`,
`QtPdf`, `QtPdfWidgets`, `QtNetwork`, `QtPrintSupport`). The frozen spec
stores these values statically so repeated builds can reuse PyInstaller's
cache. QtWebEngine is explicitly excluded, so the build stays small and
works fully offline.

---

## 🏗️ Architecture

```
pdf-toolkit/
├── src/
│   ├── main.py                    # Application entry point (DPI policy, Fusion style)
│   ├── __version__.py             # Single source of truth for the version
│   ├── paths.py                   # resource_path(): works from source and PyInstaller
│   ├── core/
│   │   ├── models.py              # PdfFile, PdfPage, OperationResult
│   │   └── pdf_engine.py          # PyMuPDF wrapper — every PDF operation
│   ├── ui/
│   │   ├── icons.py               # Vector icons rendered from SVG paths
│   │   ├── main_window.py         # MainWindow: sidebar nav, menus, threading, wiring
│   │   ├── theme.py               # Vite-inspired dark palette + QSS tokens
│   │   └── widgets/
│   │       ├── file_list.py       # Draggable library list
│   │       ├── preview.py         # Native QtPdf preview (QPdfView)
│   │       ├── tool_panels.py     # Parameter panel for each tool
│   │       └── batch_view.py      # Queue runner with per-file status
│   └── resources/
│       ├── icon.ico
│       └── icon.png
├── docs/
│   └── USER_GUIDE.md              # End-user workflows and tool reference
├── tests/                         # Plain-Python test scripts (no pytest needed)
├── build.py                       # Full clean PyInstaller build script
├── freeze_spec.py                 # Regenerates the static PyInstaller spec
├── PDF Toolkit.spec               # Frozen spec used by the fast one-file build
├── rebuild.ps1 / rebuild.bat      # Fast and release build wrappers
├── DESIGN.md                      # UI design tokens
├── requirements.txt               # Python dependencies
├── CHANGELOG.md                   # Release notes
├── CONTRIBUTING.md                # Contribution guide
├── LICENSE                        # MIT License
└── README.md                      # This file
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **GUI Framework** | PySide6 (Qt 6) | Native cross-platform widgets, high-DPI, accessibility |
| **PDF Engine** | PyMuPDF (fitz) | Fast PDF manipulation and rendering (C backend) |
| **Preview** | QtPdf (`QPdfView`) | Native, offline, zoomable rendering |
| **Threading** | QThreadPool + QRunnable | Non-blocking UI during heavy operations |
| **Packaging** | PyInstaller | Standalone executables, no dependencies |
| **Testing** | Plain Python scripts | Headless (`QT_QPA_PLATFORM=offscreen`) engine + UI tests |

### Design Principles

1. **Offline-First**: Zero network calls. No telemetry. No auto-updates (manual only).
2. **Performance**: Stream processing for large files; background threads for all I/O.
3. **Safety**: Never modify originals — always write to new paths.
4. **Privacy**: No analytics, no crash reporting, no phone-home.
5. **Accessibility**: Keyboard navigation, screen-reader labels, high-contrast dark palette.
6. **Extensibility**: Tool registry maps sidebar actions to panels and engine calls; plugins are planned for v2.0.

---

## 🧪 Testing

The suite is plain Python — no pytest plugin required. Each script prints
PASS/FAIL lines and exits non-zero on failure.

```bash
# Engine-level checks (14 operations)
.venv\Scripts\python.exe tests\test_all_features.py

# Tool-panel → engine wiring (10 panels)
$env:QT_QPA_PLATFORM="offscreen"
.venv\Scripts\python.exe tests\test_ui_wiring.py

# Full MainWindow flow (11 operations incl. batch)
.venv\Scripts\python.exe tests\test_e2e_ui.py

# Regression tests for the flow fixes
.venv\Scripts\python.exe tests\test_flow_fixes.py
```

### Test Structure
```
tests/
├── test_all_features.py    # every PdfEngine operation
├── test_ui_wiring.py       # each tool panel emits the right engine call
├── test_e2e_ui.py          # drives a real MainWindow end to end
├── test_flow_fixes.py      # regressions: page parsing, overwrite guard, dedupe
├── test_ui_operations.py   # headless operation smoke test
└── test_ui_check.py        # inspects widget state for UI regressions
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
# Runtime dependencies only (there is no separate dev requirements file)
pip install -r requirements.txt

# Optional: PyInstaller, needed only for packaging
pip install pyinstaller

# Run the test suite (headless)
$env:QT_QPA_PLATFORM="offscreen"
.venv\Scripts\python.exe tests\test_all_features.py
.venv\Scripts\python.exe tests\test_e2e_ui.py
```

### Code Style
- **Formatting**: 4-space indent, ~100 character lines
- **Imports**: standard library, third-party, then `src.*`
- **Type Hints**: on public engine methods and widget signals
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, etc.)

---

## 🗺️ Roadmap

### v1.1 (Next Release)
- [ ] OCR integration (Tesseract)
- [ ] Settings persistence (QSettings)
- [ ] Custom keyboard shortcuts
- [ ] Page thumbnails in file list
- [ ] Preview text search

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
| Preview text search / selection is not available | Planned (v1.1) | Use another reader for searching |
| Large PDFs (>500 MB) may cause memory pressure | By design | Split first, then process |
| Encrypted PDFs with unknown encryption handlers | PyMuPDF limitation | Decrypt with another tool first |
| Binary is not code-signed | By design | SmartScreen: More info → Run anyway |
| `rebuild.bat` fast mode checks the old onedir path after a one-file build | Wrapper lag | Use `rebuild.ps1` or `python -m PyInstaller -y "PDF Toolkit.spec"` |

Report new issues at [GitHub Issues](https://github.com/deba608/pdf-toolkit/issues).

---

## 🙏 Acknowledgments

- **[PyMuPDF](https://pymupdf.readthedocs.io/)** — Incredible PDF engine by Artifex
- **[Qt / QtPdf](https://doc.qt.io/qt-6/qtpdf-index.html)** — Native PDF rendering
- **[PySide6](https://wiki.qt.io/Qt_for_Python)** — Qt for Python by The Qt Company

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
| **User Guide** | [docs/USER_GUIDE.md](docs/USER_GUIDE.md) |
| **Repository** | https://github.com/deba608/pdf-toolkit |
| **Issues / Bug Reports** | https://github.com/deba608/pdf-toolkit/issues |
| **Discussions** | https://github.com/deba608/pdf-toolkit/discussions |
| **Releases** | https://github.com/deba608/pdf-toolkit/releases |
| **Security Policy** | https://github.com/deba608/pdf-toolkit/security/policy |

---

<div align="center">

**Made with ❤️ by <Dev/> for privacy-conscious PDF users everywhere.**

⭐ **Star this repo** if you find it useful!

</div>
