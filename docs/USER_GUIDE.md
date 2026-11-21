# PDF Toolkit — User Guide

*Version 1.0 | Last Updated: November 2026*

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Core Workflows](#core-workflows)
4. [Tool Reference](#tool-reference)
5. [Keyboard Shortcuts](#keyboard-shortcuts)
6. [Settings & Preferences](#settings--preferences)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Getting Started

### First Launch

1. **Download** the executable for your platform from [Releases](https://github.com/deba608/pdf-toolkit/releases)
2. **Run** the application — no installation required
3. **Accept** any OS security prompts (Windows SmartScreen, macOS Gatekeeper)
4. **Welcome screen** appears with quick-start options

### Opening Files

| Method | How To |
|--------|--------|
| **Drag & Drop** | Drag PDF files from Explorer/Finder directly into the window |
| **Menu** | `File → Open PDF(s)...` or press `Ctrl+O` |
| **Toolbar** | Click the **Open** button (folder icon) |
| **Recent Files** | `File → Recent Files` (last 10 files) |

**Multiple files**: Select multiple PDFs in the file dialog or drag a folder — all PDFs inside will be loaded.

### File List (Left Panel)

The **Files** tab shows all loaded documents:

```
┌─────────────────────────────────────┐
│  📄 report.pdf (12 pages, 3.2 MB)  │
│  📄 invoice.pdf  (5 pages, 1.1 MB)  │
│  📄 contract.pdf (25 pages, 8.7 MB) │
└─────────────────────────────────────┘
```

- **Click** a file to select it and show preview
- **Drag** to reorder (affects merge order)
- **Right-click** for context menu: Remove, Open Folder, Properties
- **Double-click** to open in system default PDF viewer

---

## Interface Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  PDF Toolkit                                    [−] [□] [×]    │
├─────────────────────────────────────────────────────────────────┤
│  File  Edit  Tools  View  Help                                   │
├─────────────────────────────────────────────────────────────────┤
│  [Open] [Save] [Save As]              [Zoom-] [100%] [Zoom+]   │
├─────────┬───────────────────────────────────────────────────────┤
│         │                                                         │
│  TABS   │         MAIN CONTENT AREA                               │
│  ─────  │                                                         │
│  📁Files│  ┌─────────────┐  ┌─────────────────────────────────┐ │
│  🔧Tools│  │  FILE LIST  │  │        PREVIEW PANE             │ │
│  ⚙Batch │  │             │  │  (PDF.js renderer)              │ │
│  🔧Settings│            │  │  - Zoom / Pan                    │ │
│         │  │ - Thumbnail │  │  - Text selection               │ │
│         │  │ - Page count│  │  - Search (Ctrl+F)              │ │
│         │  │ - File size │  │  - Page navigation              │ │
│         │  └─────────────┘  └─────────────────────────────────┘ │
│         │                                                         │
├─────────┴───────────────────────────────────────────────────────┤
│  Status: Ready                                    [Progress]   │
└─────────────────────────────────────────────────────────────────┘
```

### Four Main Tabs

| Tab | Purpose |
|-----|---------|
| **📁 Files** | Load, organize, preview files; drag-drop reorder |
| **🔧 Tools** | All PDF operations with parameter panels |
| **⚙ Batch** | Queue multiple operations (coming in v1.1) |
| **🔧 Settings** | Theme, shortcuts, defaults (coming in v1.1) |

---

## Core Workflows

### Workflow 1: Merge Multiple PDFs

**Goal**: Combine `chapter1.pdf`, `chapter2.pdf`, `chapter3.pdf` → `book.pdf`

1. Open all three files (`Ctrl+O` or drag-drop)
2. In **Files tab**, verify order — drag to reorder if needed
3. Switch to **Tools tab** → **Merge** panel (selected by default)
4. Set **Output path** (optional — defaults to `merged.pdf` in first file's folder)
5. Click **Merge All Files**
6. Result appears in file list; preview updates automatically
7. Save with `Ctrl+S` or **Save As** from toolbar

> 💡 **Tip**: Merge uses the file list order. Reorder in Files tab before merging.

---

### Workflow 2: Split a Large PDF

**Goal**: Split `annual-report.pdf` (100 pages) into 10-page chunks

1. Open `annual-report.pdf`
2. **Tools tab** → **Split** panel
3. Set **Pages per file**: `10`
4. Choose **Output folder** (defaults to source folder)
5. Click **Split**
6. Ten new files appear: `annual-report_part1.pdf` ... `annual-report_part10.pdf`

> 💡 **Tip**: For custom ranges, use **Extract Pages** (coming in v1.1) or split then merge specific parts.

---

### Workflow 3: Add Watermark

**Goal**: Mark `draft-proposal.pdf` as "CONFIDENTIAL — DO NOT DISTRIBUTE"

1. Open the PDF
2. **Tools tab** → **Watermark** panel
3. **Text**: `CONFIDENTIAL — DO NOT DISTRIBUTE`
4. **Opacity**: `30%` (subtle but visible)
5. **Font Size**: `48` (adjust for page size)
6. Click **Add Watermark**
7. Preview shows watermark on all pages
8. Save with `Ctrl+S`

> 💡 **Tip**: Watermark is added to **every page**. For single-page watermarks, use Extract → Watermark → Merge (v1.1).

---

### Workflow 4: Encrypt for Secure Sharing

**Goal**: Send `contract.pdf` to client — they can view/print only, not edit/copy

1. Open `contract.pdf`
2. **Tools tab** → **Encrypt** panel
3. **User Password**: `ClientView2026!` (what client enters to open)
4. **Owner Password**: `OwnerSecret2026!` (your master password — keep safe!)
5. **Permissions**: Select **"Allow printing only"**
   - ✅ Print
   - ❌ Copy text/images
   - ❌ Modify
   - ❌ Annotate
   - ❌ Fill forms
   - ❌ Accessibility extraction
6. Click **Encrypt**
7. Save encrypted version: `contract-secure.pdf`
8. Send `contract-secure.pdf` + **User Password** to client
9. **Store Owner Password securely** — needed to change permissions later

> ⚠️ **Warning**: If you lose both passwords, the PDF is permanently locked. No backdoors exist.

---

### Workflow 5: Compress for Email

**Goal**: Reduce `presentation.pdf` (25 MB) to under 10 MB for email attachment

1. Open the PDF
2. **Tools tab** → **Compress** panel
3. **Quality**: Start at `75%` (good balance)
4. Click **Compress**
5. Check result size in file list
6. If still too large, re-open original and try `60%` or `50%`
7. Save compressed version

> 💡 **Tip**: Compression works by downsampling images and removing redundant data. Text-heavy PDFs compress less.

---

### Workflow 6: Convert PDF to Images

**Goal**: Extract pages from `diagram.pdf` as high-res PNGs for PowerPoint

1. Open `diagram.pdf`
2. **Tools tab** → **To Images** panel
3. **DPI**: `300` (print quality) or `150` (screen)
4. **Format**: `PNG` (lossless, transparency) or `JPG` (smaller)
5. **Output folder**: Choose destination
6. Click **Convert**
7. Files saved as `diagram_page1.png`, `diagram_page2.png`, ...

> 💡 **Tip**: For single pages, use page range (coming in v1.1) or extract pages first.

---

### Workflow 7: Combine Scans into PDF

**Goal**: Turn `scan001.jpg`, `scan002.jpg`, `scan003.jpg` → `scanned-document.pdf`

1. **Tools tab** → **Images to PDF** panel
3. Click **Add Images** → select all scan files
4. Verify order — drag to reorder in list
5. Set **Output PDF path**
6. Click **Create PDF**
7. Result opens in preview automatically

> 💡 **Tip**: For OCR (searchable text), use **OCR** tool (coming in v1.1) after creating PDF.

---

## Tool Reference

### Merge
| Parameter | Description | Default |
|-----------|-------------|---------|
| Output Path | Where to save merged PDF | `merged.pdf` in first file's folder |

**Input**: 2+ PDFs in file list (order = merge order)
**Output**: Single merged PDF

---

### Split
| Parameter | Description | Default |
|-----------|-------------|---------|
| Pages per file | Number of pages in each output file | `1` (burst) |
| Output Folder | Destination directory | Source file's folder |

**Input**: Single PDF
**Output**: Multiple PDFs named `{name}_part{N}.pdf`

---

### Rotate
| Parameter | Description | Default |
|-----------|-------------|---------|
| Rotation | Degrees to rotate (90/180/270) | `90` |
| Pages | Which pages to rotate | All pages |

**Input**: Single PDF
**Output**: PDF with rotated pages

---

### Reorder
| Parameter | Description | Default |
|-----------|-------------|---------|
| (none) | Uses drag-drop order from Files tab | — |

**Input**: Single PDF (pages reordered in Files tab)
**Output**: PDF with new page order

> 💡 **How to reorder**: In **Files tab**, click a file to show its pages in the list. Drag page thumbnails to reorder. Then use **Reorder** tool.

---

### Watermark
| Parameter | Description | Default |
|-----------|-------------|---------|
| Text | Watermark text | `CONFIDENTIAL` |
| Opacity | Transparency (0–100%) | `30%` |
| Font Size | Point size | `48` |
| Color | Text color (RGB) | Gray (128,128,128) |
| Angle | Rotation angle | `45°` |

**Input**: Single PDF
**Output**: PDF with watermark on all pages

---

### Encrypt
| Parameter | Description | Default |
|-----------|-------------|---------|
| User Password | Password to open/view | Required |
| Owner Password | Password to change permissions | Same as user |
| Permissions | What user can do | None (all denied) |

**Permission Options**:
- **No permissions** — View only (print/copy/edit all blocked)
- **Allow printing** — Can print, but not copy/edit
- **Allow all** — Full access except permission changes

**Input**: Single PDF
**Output**: Encrypted PDF (AES-256)

---

### Decrypt
| Parameter | Description | Default |
|-----------|-------------|---------|
| Password | User or owner password | Required |

**Input**: Encrypted PDF
**Output**: Decrypted PDF (no passwords, no restrictions)

---

### Compress
| Parameter | Description | Default |
|-----------|-------------|---------|
| Quality | Image quality 10–100% | `75%` |

**What gets compressed**:
- Image downsampling (to effective DPI)
- JPEG recompression at quality setting
- Duplicate object removal
- Garbage collection (unused objects)
- Stream deflation

**Input**: Single PDF
**Output**: Smaller PDF (visually similar at 75%+)

---

### To Images
| Parameter | Description | Default |
|-----------|-------------|---------|
| DPI | Output resolution (72–600) | `200` |
| Format | `PNG` or `JPG` | `PNG` |
| Output Folder | Destination | Source folder |

**Input**: Single PDF
**Output**: Image files `{name}_page{N}.{ext}`

---

### Images to PDF
| Parameter | Description | Default |
|-----------|-------------|---------|
| Image List | Added via "Add Images" button | — |
| Output Path | Where to save PDF | `images.pdf` in first image's folder |

**Supported formats**: PNG, JPG, JPEG, BMP, TIFF, GIF (first frame)
**Input**: Multiple image files
**Output**: Single PDF (one page per image, preserving aspect ratio)

---

## Keyboard Shortcuts

### Global
| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file(s) |
| `Ctrl+S` | Save current document |
| `Ctrl+Shift+S` | Save As... |
| `Ctrl+W` | Close current file |
| `Ctrl+Q` | Quit application |
| `F11` | Toggle fullscreen |
| `Ctrl+,` | Open Settings (v1.1) |

### Navigation
| Shortcut | Action |
|----------|--------|
| `Ctrl+1` | Files tab |
| `Ctrl+2` | Tools tab |
| `Ctrl+3` | Batch tab (v1.1) |
| `Ctrl+4` | Settings tab (v1.1) |
| `Tab` | Cycle focus: File list → Preview → Tool panel |
| `Shift+Tab` | Reverse cycle |

### Preview
| Shortcut | Action |
|----------|--------|
| `Ctrl++` / `Ctrl+=` | Zoom in |
| `Ctrl+-` | Zoom out |
| `Ctrl+0` | Reset zoom (100%) |
| `Ctrl+F` | Find text |
| `F3` / `Enter` | Next match |
| `Shift+F3` | Previous match |
| `Space` | Pan (hold + drag) |
| `←` / `→` | Previous/Next page |
| `Home` / `End` | First/Last page |

### File List
| Shortcut | Action |
|----------|--------|
| `Delete` | Remove selected file |
| `Ctrl+A` | Select all files |
| `↑` / `↓` | Navigate files |
| `Enter` | Select file (show preview) |
| `Ctrl+↑` / `Ctrl+↓` | Move file up/down in list |

---

## Settings & Preferences

*(Available in v1.1 — currently shows placeholder)*

### Planned Settings

| Category | Options |
|----------|---------|
| **Appearance** | Theme: Light / Dark / System; Accent color; Font size |
| **Behavior** | Auto-save on operation; Confirm overwrites; Clear file list on new session |
| **Defaults** | Default DPI (images); Default compression quality; Default output folder |
| **Shortcuts** | View/edit all keyboard shortcuts; Export/import shortcut schemes |
| **Advanced** | PDF.js render settings; Thread pool size; Cache size; Log level |

---

## Troubleshooting

### Application Won't Start

| Symptom | Cause | Solution |
|---------|-------|----------|
| Nothing happens on double-click | Missing Visual C++ Redistributable (Windows) | Install [VC++ Redist](https://aka.ms/vs/17/release/vc_redist.x64.exe) |
| "App is damaged" (macOS) | Gatekeeper quarantine | `xattr -cr /Applications/PDF\ Toolkit.app` |
| Segfault on Linux | Wayland + WebEngine conflict | Run with `QT_QPA_PLATFORM=xcb ./PDF_Toolkit` |
| DLL load failed (Windows) | Antivirus blocking PyInstaller bootstrap | Add exception for `PDF Toolkit.exe` |

### PDF Operations Fail

| Error | Likely Cause | Fix |
|-------|--------------|-----|
| "Incorrect password" | Wrong password entered | Verify caps lock; try owner password |
| "Permission denied" | File locked by another app | Close PDF in browser/reader; retry |
| "Out of memory" | PDF too large for RAM | Split first; increase virtual memory |
| "Corrupted PDF" | Invalid PDF structure | Try opening in Adobe Reader → Save As → retry |
| Preview shows blank | WebEngine not rendering | Restart app; update GPU drivers |

### Performance Issues

| Issue | Fix |
|-------|-----|
| Slow preview on large PDFs | Lower preview DPI in Settings (v1.1); use "Fit Width" not "Fit Page" |
| Merge takes forever | Ensure files aren't on network drive; disable antivirus scanning on temp folder |
| High memory usage | Process files individually; restart app between large jobs |

---

## FAQ

### General

**Q: Is my data uploaded anywhere?**
A: **Never.** PDF Toolkit is 100% offline. No network calls, no telemetry, no accounts. Your documents never leave your computer.

**Q: Can I use this commercially?**
A: Yes. MIT license allows commercial use, modification, distribution. See [LICENSE](../LICENSE).

**Q: Does it work on Linux?**
A: Yes, but WebEngine preview may require X11 (not Wayland) on some distros. AppImage provided.

**Q: How do I update?**
A: Download new release from GitHub. No auto-updater (by design — offline-first).

### Features

**Q: Can I edit text in a PDF?**
A: Not yet. PDF Toolkit manipulates structure (merge, split, rotate) and adds content (watermark), but doesn't edit existing text. Planned for v2.0.

**Q: Can I fill PDF forms?**
A: Not yet. Form filling/flattening planned for v1.2.

**Q: Does it support digital signatures?**
A: Planned for v1.2 (sign/verify with certificates).

**Q: Can I batch process 100 files?**
A: Batch queue coming in v1.1. For now, process individually or use command line (v2.0).

**Q: OCR / make scanned PDF searchable?**
A: Planned for v1.1 with Tesseract integration.

### Technical

**Q: Why PySide6 not PyQt6?**
A: PySide6 is the official Qt for Python (LGPL), better licensing for commercial use.

**Q: Why PyMuPDF not pdfplumber/pikepdf?**
A: PyMuPDF (fitz) is fastest, most feature-complete, handles encryption/compression natively.

**Q: Can I build from source?**
A: Yes. `pip install -r requirements.txt && python -m src.main`. See [Building](#building-standalone-executable).

**Q: How to contribute?**
A: See [CONTRIBUTING.md](CONTRIBUTING.md). Fork → branch → PR. All PRs need tests + type hints.

---

## Appendix: File Format Support

| Operation | Input Formats | Output Formats |
|-----------|---------------|----------------|
| Merge | PDF | PDF |
| Split | PDF | PDF |
| Rotate | PDF | PDF |
| Reorder | PDF | PDF |
| Watermark | PDF | PDF |
| Encrypt | PDF | PDF (AES-256) |
| Decrypt | PDF (encrypted) | PDF |
| Compress | PDF | PDF |
| To Images | PDF | PNG, JPG |
| Images to PDF | PNG, JPG, BMP, TIFF, GIF | PDF |

---

## Support

- **Bug Reports**: [GitHub Issues](https://github.com/deba608/pdf-toolkit/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/deba608/pdf-toolkit/discussions)
- **Security Issues**: [Security Policy](https://github.com/deba608/pdf-toolkit/security/policy)

---

*Last updated: November 2026 | PDF Toolkit v1.0*