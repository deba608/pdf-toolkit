# PDF Toolkit — User Guide

*Version 1.0 · Last updated: November 2026*

This guide describes the application exactly as it ships today. Features that
are still planned are listed in the [Roadmap](../README.md#-roadmap).

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Core Workflows](#core-workflows)
4. [Tool Reference](#tool-reference)
5. [Batch Processing](#batch-processing)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Getting Started

### First Launch

1. **Download** the executable for your platform from
   [Releases](https://github.com/deba608/pdf-toolkit/releases), or run from
   source with `python -m src.main`.
2. **Run** the application. There is no installer and no account.
3. Accept any OS security prompt (Windows SmartScreen, macOS Gatekeeper) — the
   binaries are not code-signed.

### Opening Files

| Method | How |
|--------|-----|
| **Drag & drop** | Drop PDF files anywhere on the window |
| **Sidebar button** | Click **+ Open PDFs** at the bottom left |
| **Menu** | `File → Open PDF(s)…` or `Ctrl+O` |
| **Home view** | Click **Add** above the file list |

Opening the same file twice is a no-op: files are matched by full path and
de-duplicated. Encrypted PDFs prompt for the password once (three attempts).

### The File Library

The **Home** view lists every loaded PDF with its page count and size.

- **Click** a file to select it; the preview and every tool then act on it.
- **Drag** a row to change the order — this is the merge order.
- **Right-click → Remove**, or select a row and press `Delete`.
- **Clear** empties the library.

---

## Interface Overview

```
┌──────────────┬──────────────────────────────────────────────────┐
│ PDF Toolkit  │  Header: current tool + selected file            │
│              ├──────────────────────────────────────────────────┤
│ LIBRARY      │                                                  │
│  Home        │   File list            │   Preview                │
│ TOOLS        │   (drag to reorder)    │   (native PDF renderer)  │
│  Merge       │                        │                          │
│  Split       │                        │                          │
│  Rotate      │                        │                          │
│  Reorder     │                        │                          │
│  Watermark   │                        │                          │
│  Compress    │                        │                          │
│ SECURITY     │                        │                          │
│  Encrypt     │                        │                          │
│  Decrypt     │                        │                          │
│ CONVERT      │                        │                          │
│  PDF→Images  │                        │                          │
│  Images→PDF  │                        │                          │
│ AUTOMATION   │                        │                          │
│  Batch run   │                        │                          │
├──────────────┴──────────────────────────────────────────────────┤
│  Status bar                                    [progress]       │
└─────────────────────────────────────────────────────────────────┘
```

- **Home** shows the library and a preview of the selected file.
- **Tool views** show the parameter panel on the left and a preview on the
  right. Tools that need a file show a warning banner until one is selected.
- **Batch run** applies one operation to every PDF in the library.

The preview is rendered by Qt's native PDF engine: it works fully offline and
opens password-protected files with the password you entered.

---

## Core Workflows

### Merge PDFs

1. Open two or more PDFs.
2. Drag the rows into the order you want.
3. Sidebar → **Merge**.
4. Optionally set an output path (default: `merged.pdf` next to the first file).
5. Click **Merge PDFs**. The result is added to the library and selected.

> The whole library is merged. At least two files are required.

### Split a PDF

1. Select the PDF.
2. Sidebar → **Split**.
3. Set **Pages per file** (for example `10`).
4. Choose an output folder (default: the source folder).
5. Click **Split PDF**.

Output files are named `{name}_part1.pdf`, `{name}_part2.pdf`, … and are added
to the library.

### Rotate Pages

1. Select the PDF.
2. Sidebar → **Rotate**.
3. Pick `90°`, `180°`, or `270°`.
4. Optionally enter pages such as `1,3,5-8` (blank = all pages).
5. Click **Rotate Pages**.

Rotation is added to each page's existing rotation.

### Reorder / Drop Pages

1. Select the PDF.
2. Sidebar → **Reorder**.
3. Enter the new order, 1-based, for example `3,1,2`.
4. Click **Apply Reorder**.

Leave the field blank to keep the current order. Pages you do not list are
dropped from the output, which makes this a quick way to extract pages too.

### Add a Watermark

1. Select the PDF.
2. Sidebar → **Watermark**.
3. Enter the text, opacity, and font size.
4. Click **Add Watermark**.

The watermark is stamped once, centred, on every page.

### Encrypt

1. Select the PDF.
2. Sidebar → **Encrypt**.
3. Enter a **user password** (required to open) and optionally an **owner
   password** (defaults to the user password).
4. Choose permissions:
   - **No permissions** — printing, copying, and editing are denied.
   - **Allow printing** — printing only.
   - **Allow all** — the default; the password protects opening, not usage.
5. Click **Encrypt PDF**.

Output uses AES-256. There is no recovery: if you lose the password, the file
cannot be opened.

### Decrypt

1. Select the encrypted PDF (enter its password when prompted).
2. Sidebar → **Decrypt**.
3. Leave the password field blank to reuse the password you opened it with, or
   type another one.
4. Click **Decrypt PDF**.

The output has no encryption and no permission restrictions.

### Compress

1. Select the PDF.
2. Sidebar → **Compress**.
3. Set **Image quality** — images above 150 DPI are downsampled and re-encoded
   at this quality; fonts and file structure are also cleaned.
4. Click **Compress PDF**.

Text-only PDFs barely shrink. Scanned/image-heavy PDFs shrink a lot. Lower
quality means a smaller file and more visible JPEG artefacts.

### Export PDF to Images

1. Select the PDF.
2. Sidebar → **PDF → Images**.
3. Choose DPI (72–600) and PNG or JPG.
4. Choose an output folder.
5. Click **Export Images**.

Files are named `{name}_page1.png`, `{name}_page2.png`, …

### Build a PDF from Images

1. Sidebar → **Images → PDF** (no PDF needs to be selected).
2. Click **Add Images** and pick PNG, JPG, BMP, or TIFF files.
3. Optionally set the output path.
4. Click **Create PDF**.

Each image becomes one page, sized to the image's dimensions.

---

## Tool Reference

| Tool | Key parameters | Defaults |
|------|----------------|----------|
| **Merge** | Output file | `merged.pdf` next to first source |
| **Split** | Pages per file, output folder | 1 page, source folder |
| **Rotate** | Angle, pages | 90°, all pages |
| **Reorder** | New order (1-based) | Current order |
| **Watermark** | Text, opacity, font size | 0.3, 48 pt, grey |
| **Encrypt** | User/owner password, permissions | Allow all, AES-256 |
| **Decrypt** | Password | Password used to open the file |
| **Compress** | Image quality | 75% |
| **PDF → Images** | DPI, format, output folder | 200 DPI, PNG |
| **Images → PDF** | Image list, output path | `images.pdf` next to first image |

Every operation writes a **new** file. The app refuses to write over one of its
own inputs; choose a different output name if you see that error.

---

## Batch Processing

Open **Batch run** from the sidebar or with `Ctrl+B`.

1. The queue shows every PDF currently in the library.
2. Pick an operation: compress, rotate, watermark, encrypt, decrypt, export to
   images, or split.
3. Set the parameters (the same ones as the single-file tool).
4. Optionally choose an output folder (default: each file's own folder).
5. Click **Run batch**.

Each row reports Pending, Running, Done, or Error. Hover an error row for the
message. Files produced by the batch are added back to the library when the run
finishes. **Reset status** clears the row markers for another run.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open PDF files |
| `Ctrl+S` | Save a copy of the selected PDF |
| `Ctrl+Shift+S` | Save a copy (same dialog) |
| `Ctrl+B` | Open batch processing |
| `Ctrl++` / `Ctrl+=` | Zoom preview in |
| `Ctrl+-` | Zoom preview out |
| `Ctrl+0` | Reset preview zoom |
| `Delete` | Remove the selected file from the library |
| `F1` | Show the shortcut list |
| `Ctrl+Q` | Quit |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "PDF is encrypted — a password is required" | The file needs a password | Open it again and enter the password when prompted |
| "Incorrect password" | Wrong password | Check caps lock; try the owner password |
| "Refusing to overwrite the source file" | Output path equals an input path | Pick a different output name/folder |
| Compressed file is barely smaller | PDF is text-only | Downsampling only affects images; there is nothing else to remove |
| Preview is blank | The file is corrupt or uses an unsupported encryption handler | Try opening it in another PDF reader first |
| App won't start on Windows | Missing Visual C++ runtime or antivirus quarantine | Install the VC++ redistributable, allow the exe |
| Large PDFs use a lot of memory | PyMuPDF loads the document into memory | Split first, then process the parts |

---

## FAQ

**Is anything uploaded?**
No. There are no network calls, no telemetry, and no accounts.

**Can I use it commercially?**
Yes — MIT licence. See [LICENSE](../LICENSE).

**Does it edit existing text or fill forms?**
No. It manipulates document structure and adds content. Text editing, form
filling, and signatures are on the roadmap.

**Can I process many files at once?**
Yes — use **Batch run** (`Ctrl+B`).

**Is the preview searchable?**
Not yet. The native preview supports scrolling and zoom; text search is planned.

**Why is the source never modified?**
Every operation writes to a new path and the engine refuses to overwrite an
input. Keep the original and delete it yourself when you are happy with the
result.

---

## File Format Support

| Operation | Input | Output |
|-----------|-------|--------|
| Merge, Split, Rotate, Reorder | PDF | PDF |
| Watermark, Compress | PDF | PDF |
| Encrypt / Decrypt | PDF | PDF (AES-256 / none) |
| PDF → Images | PDF | PNG, JPG |
| Images → PDF | PNG, JPG, BMP, TIFF | PDF |

---

## Support

- **Bugs**: [GitHub Issues](https://github.com/deba608/pdf-toolkit/issues)
- **Ideas**: [GitHub Discussions](https://github.com/deba608/pdf-toolkit/discussions)
- **Security**: [Security Policy](https://github.com/deba608/pdf-toolkit/security/policy)

---

*Last updated: November 2026 · PDF Toolkit v1.0*
