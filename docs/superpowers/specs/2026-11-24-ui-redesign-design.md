# PDF Toolkit UI Redesign — Design Spec

**Date:** 2026-11-24
**Status:** Approved by user
**Scope:** Full interface redesign of the PySide6/Qt desktop shell. Engine and file-format behavior unchanged.

## 1. Problem

Current UI is organized around a fixed 240px left sidebar (`src/ui/main_window.py:174-255`) and a shared "Home Library". Users must load files on Home before configuring a tool, which produces duplicated titles, competing CTAs, empty preview space, and a disconnected workflow (see `UI_UX_AUDIT.md`). Wanted: iLovePDF-style task-first flow — choose a tool, add files there, configure on the right.

## 2. Goals / success criteria

1. Launch shows a full-screen Home Grid; no sidebar exists in the widget tree.
2. Home Grid shows grouped tool cards: Tools, Converter, Security, Automation, Library.
3. Clicking any tool card opens a fresh Tool Workspace with a Drop Zone and File Queue; no files carry over from another tool.
4. Dropping or browsing files adds them to the workspace session. Wrong file types are rejected with a status message.
5. Right panel has Options and Preview tabs. Options auto-selects after the first file.
6. Execute uses session files, not the global Output Library.
7. Existing `PdfEngine` signatures and the ten existing tool panels remain unchanged.
8. All existing UI tests pass, including `tests/test_e2e_ui.py`.

## 3. Non-goals

- No web frontend, Electron, or QWebEngine.
- No new PDF operations, no new file formats.
- No light theme; keep the Vite dark palette from `DESIGN.md`.
- No cloud/upload/network features; app remains offline.
- No rewrite of `PdfEngine`, `PreviewWidget`, or `BatchView` internals.

## 4. Architecture

### 4.1 Approach chosen

New shell + adapter around the existing engine. `MainWindow` owns a `HomeView` and one reusable `ToolWorkspace`. `ToolWorkspace` reuses `ToolPanelsStack` for settings and `PreviewWidget` for preview. `PdfEngine` is untouched. A `ToolRegistry` and `ToolSession` replace `NAV_ITEMS` as navigation and per-tool state.

Alternatives rejected: (B) per-tool workspace classes — higher cost and drift risk; (C) hide sidebar only — fails dropzone/right-panel requirements.

### 4.2 New modules

| File | Responsibility |
|---|---|
| `src/ui/tool_registry.py` | `ToolSpec` dataclass and immutable `TOOLS` registry; section order and lookup helpers. |
| `src/ui/widgets/tool_session.py` | Per-tool state: files, image paths, active file, input-mode rules, add/remove/move operations. |
| `src/ui/widgets/drop_zone.py` | Reusable dashed drop target with browse button, MIME filtering, drag-highlight, `filesDropped`/`browseRequested` signals. |
| `src/ui/widgets/file_queue.py` | Reusable ordered file list with selected item, move up/down, remove, clear, `currentItemChanged` relay. |
| `src/ui/widgets/home_view.py` | Home header, Home drop strip, responsive tool-card grid, recent-files strip. |
| `src/ui/widgets/tool_workspace.py` | Splitter: left Drop Zone + File Queue; right QTabWidget Options/Preview; hosts ToolPanelsStack or BatchView. |

### 4.3 Modified modules

| File | Change |
|---|---|
| `src/ui/main_window.py` | Replace sidebar/content stack with Home Grid + Tool Workspace; add back button in header; route registry tools; keep compatibility aliases for tests. |
| `src/ui/theme.py` | Append QSS for `HomeGrid`, `ToolCard`, `DropZone`, `FileQueue`, `ToolTabs`, `SettingsPanel`, `HomeDropStrip`; keep all existing tokens and the user's uncommitted audit fixes. |
| `src/ui/widgets/tool_panels.py` | Add `set_external_queue(True)` so the merge panel hides its in-panel queue when the workspace supplies one. Keep the user's uncommitted merge-queue code intact. |
| `docs/USER_GUIDE.md` | Update the UI wireframe and workflow description. |

## 5. Information architecture

`ToolSpec` fields: `key`, `label`, `icon`, `section`, `description`, `input_mode`, `panel_key`.

Input modes:

| Mode | Tools | Rule |
|---|---|---|
| `single_pdf` | split, rotate, reorder, watermark, compress, encrypt, decrypt, to images | Queue holds at most one PDF; extra drops are rejected. |
| `multi_pdf` | merge, batch | Queue holds any number of PDFs; merge requires ≥2 for execute. |
| `multi_image` | images to pdf | Queue holds image paths only; PDFs rejected. |

Sections and cards:

- **Tools** — Merge, Split, Rotate, Reorder, Watermark, Compress
- **Security** — Encrypt, Decrypt
- **Converter** — PDF → Images, Images → PDF
- **Automation** — Batch run
- **Library** — Open PDFs, recent files, file count

Home drop behavior: dropping PDFs on the Home strip opens a tool picker (`QInputDialog.getItem`) listing all PDF-accepting tools. Choosing a tool opens its workspace and loads the dropped files into that session. Cancelling leaves Home unchanged.

## 6. Screen behavior

### 6.1 Home Grid

- Header: "PDF Toolkit", subtitle "Everything you need for PDFs. Fast, private, offline.", `OFFLINE` badge.
- Drop strip: icon + "Drop PDFs here to get started" + "Choose files" secondary button.
- Cards: 22px tinted icon tile, title, wrapped one-line description, arrow; minimum height 112px; keyboard focusable; Enter activates.
- Responsive grid recalculated in `resizeEvent`: 3 columns ≥1060px, 2 columns 760–1059px, 1 column <760px.
- Library section: file count, "Open PDFs…" button, up to five recent file buttons.

### 6.2 Tool Workspace

- Header: `← Home`, tool title, tool description, Help.
- Left card: requirement hint ("Add at least 2 PDFs"), Drop Zone, File Queue.
- Right card: QTabWidget with Options (0) and Preview (1).
- Options tab: existing `ToolPanelsStack` inside a scroll area for all tools except batch; `BatchView` for batch. Sticky execute comes from the existing panel/batch UI, not a new duplicate button.
- Preview tab: one `PreviewWidget` + empty state; shows `session.active_file`.
- Options tab auto-selects when the first file is added; Preview tab auto-selects when a queue item is clicked.
- Drop Zone drag-enter sets `dropActive` property and repolishes style; drag-leave clears it.
- In-panel merge queue from the user's uncommitted work is hidden via `set_external_queue(True)`; `set_files()` still drives merge button enablement.

### 6.3 State / dispatch

- `MainWindow.session` is replaced on every tool open. `current_file` is a property mapped to `session.active_file`.
- `MainWindow.files` remains the Output Library for produced files and legacy `_load_files()`.
- `_run_operation(op, params)` reads `session.files` for merge and `session.active_file` for single-file tools. If the session is empty (legacy E2E path), it falls back to `self.files` / `self.current_file`.
- `_load_with_password()` is reused for every PDF path entering a session.
- `images to pdf` uses image paths from `session.image_paths`, merged into `params["image_paths"]` when the panel did not supply its own list.
- Batch receives `session.files` via `batch_view.set_files()`.

## 7. Error handling

- Rejected drop file type → status message: "Only PDF files are supported by Merge" (or image equivalent).
- Single-PDF tool with 2+ dropped files → first accepted, rest rejected with status message counting rejected files.
- Merge with <2 session files → existing "Not enough files" dialog.
- Password-protected PDF → existing three-attempt `_load_with_password()` dialog.
- Operation failure → existing `_operation_error()` message box.

## 8. Verification

- `tests/test_ui_wiring.py` — unchanged; must pass.
- `tests/test_e2e_ui.py` — unchanged; must pass via compatibility aliases.
- `tests/test_ui_check.py` — unchanged; must pass via hidden `file_list` and `tool_panels` aliases.
- New `tests/test_redesign_ui.py` — headless checks: no sidebar object, 11 tool specs, 11 home cards, fresh session per tool, correct MIME rules, right-tab switch, drop-to-picker route.
- Manual: launch app, verify Home grid, open Merge, drop two PDFs, reorder, execute, check output added to Output Library and Preview tab works.

## 9. Decisions made

- Home drop → tool picker dialog.
- Keep dark Vite theme.
- Keep existing tool panel parameter widgets as-is.
- No left navigation anywhere; back button only.
- Workspace input files are per-tool; outputs still accumulate in the Output Library.
