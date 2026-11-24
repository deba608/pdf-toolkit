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

Files are added inside the tool you want to use. There is no shared input
library.

| Method | How |
|--------|-----|
| **Home drop strip** | Drop PDFs on Home, then choose a tool from the picker |
| **Tool workspace** | Drop files on the dashed target, or click **Browse files…** |
| **Menu** | `File → Open PDF(s)…` or `Ctrl+O`, then choose a tool |

Opening the same file twice is a no-op: files are matched by full path and
de-duplicated. Encrypted PDFs prompt for the password once (three attempts).

### Workspaces and Outputs

Each tool opens a fresh workspace. Its file queue belongs only to that tool;
switching tools clears it. Results are added to the **Output Library**, whose
count and recent files appear at the bottom of Home. `Ctrl+O` also loads files
into the Output Library.

---

## Interface Overview

Home is a full-screen tool grid with no sidebar:

```
┌──────────────────────────────────────────────────────────────┐
│ PDF Toolkit   Everything you need for PDFs...      OFFLINE   │
├──────────────────────────────────────────────────────────────┤
│  Drop PDFs here to get started            [Browse files...]  │
│                                                              │
│  TOOLS                                                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                      │
│  │ Merge    │ │ Split    │ │ Rotate   │                      │
│  └──────────┘ └──────────┘ └──────────┘                      │
│  CONVERTER / SECURITY / AUTOMATION / LIBRARY                  │
└──────────────────────────────────────────────────────────────┘
```

After choosing a tool:

```
┌──────────────────────────────────────────────────────────────┐
│ ← Home   Merge   Combine multiple PDFs into one       ?      │
├───────────────────────────────┬──────────────────────────────┤
│ Add at least two PDFs         │ [ Options ] [ Preview ]      │
│ ┌───────────────────────────┐ │                              │
│ │ Drop PDFs here for Merge  │ │  Output destination          │
│ └───────────────────────────┘ │  ...                         │
│ 2 files        [Clear]        │                              │
│ 1. alpha.pdf                  │                              │
│ 2. beta.pdf                   │                              │
│ [Up] [Down] [Remove]          │                              │
└───────────────────────────────┴──────────────────────────────┘
```

- **Options** auto-selects after files are added. **Preview** shows the active
  file when you select a queue item.
- Merge and batch queues support **Up**, **Down**, **Remove**, and **Clear**.
  Single-PDF tools accept one file; **Images → PDF** accepts images only.
- Dropping PDFs on Home opens a tool picker. Dropping files inside a workspace
  adds them to that tool's session.

The preview is rendered by Qt's native PDF engine: it works fully offline and
opens password-protected files with the password you entered.

---

## Core Workflows

### Merge PDFs

1. Home → **Merge**.
2. Drop two or more PDFs into the workspace, or click **Browse files…**.
3. Use **Up** / **Down** in the queue to set merge order.
4. Optionally set an output path (default: `merged.pdf` next to the first file).
5. Click **Merge PDFs**. The result is added to the Output Library.

> Only the files in this workspace are merged. At least two are required.

### Split a PDF

1. Home → **Split**, then add one PDF.
2. Set **Pages per file** (for example `10`).
3. Choose an output folder (default: the source folder).
4. Click **Split PDF**.

Output files are named `{name}_part1.pdf`, `{name}_part2.pdf`, … and are added
to the Output Library.

### Rotate Pages

1. Home → **Rotate**, then add one PDF.
2. Pick `90°`, `180°`, or `270°`.
3. Optionally enter pages such as `1,3,5-8` (blank = all pages).
4. Click **Rotate Pages**.

Rotation is added to each page's existing rotation.

### Reorder / Drop Pages

1. Home → **Reorder**, then add one PDF.
2. Enter the new order, 1-based, for example `3,1,2`.
3. Click **Apply Reorder**.

Leave the field blank to keep the current order. Pages you do not list are
dropped from the output, which makes this a quick way to extract pages too.

### Add a Watermark

1. Home → **Watermark**, then add one PDF.
2. Enter the text, opacity, and font size.
3. Click **Add Watermark**.

The watermark is stamped once, centred, on every page.

### Encrypt

1. Home → **Encrypt**, then add one PDF.
2. Enter a **user password** (required to open) and optionally an **owner
   password** (defaults to the user password).
3. Choose permissions:
   - **No permissions** — printing, copying, and editing are denied.
   - **Allow printing** — printing only.
   - **Allow all** — the default; the password protects opening, not usage.
4. Click **Encrypt PDF**.

Output uses AES-256. There is no recovery: if you lose the password, the file
cannot be opened.

### Decrypt

1. Home → **Decrypt**, then add one PDF. Enter its password when prompted.
2. Leave the password field blank to reuse the password you opened it with, or
   type another one.
3. Click **Decrypt PDF**.

The output has no encryption and no permission restrictions.

### Compress

1. Home → **Compress**, then add one PDF.
2. Set **Image quality** — images above 150 DPI are downsampled and re-encoded
   at this quality; fonts and file structure are also cleaned.
3. Click **Compress PDF**.

Text-only PDFs barely shrink. Scanned/image-heavy PDFs shrink a lot. Lower
quality means a smaller file and more visible JPEG artefacts.

### Export PDF to Images

1. Home → **PDF → Images**, then add one PDF.
2. Choose DPI (72–600) and PNG or JPG.
3. Choose an output folder.
4. Click **Export Images**.

Files are named `{name}_page1.png`, `{name}_page2.png`, …

### Build a PDF from Images

1. Home → **Images → PDF**.
2. Drop PNG, JPG, BMP, or TIFF files into the workspace, or click
   **Add Images**.
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

Open **Home → Batch run** or press `Ctrl+B`.

1. Add one or more PDFs to the batch workspace.
2. Pick an operation: compress, rotate, watermark, encrypt, decrypt, export to
   images, or split.
3. Set the parameters (the same ones as the single-file tool).
4. Optionally choose an output folder (default: each file's own folder).
5. Click **Run batch**.

Each row reports Pending, Running, Done, or Error. Hover an error row for the
message. Files produced by the batch are added back to the Output Library when
the run finishes. **Reset status** clears the row markers for another run.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open PDF files and choose a tool |
| `Ctrl+S` | Save a copy of the selected PDF |
| `Ctrl+Shift+S` | Save a copy (same dialog) |
| `Ctrl+B` | Open batch processing |
| `Ctrl++` / `Ctrl+=` | Zoom preview in |
| `Ctrl+-` | Zoom preview out |
| `Ctrl+0` | Reset preview zoom |
| `Delete` | Clear the Output Library |
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
