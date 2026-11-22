# Changelog

All notable changes to PDF Toolkit are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Native `QPdfView` preview with zoom in/out/reset and password support
  (replaces the CDN-dependent PDF.js/WebEngine viewer)
- Batch run view: apply one operation to every loaded PDF with per-file
  status, and add the produced files back to the library
- Keyboard shortcuts: `Ctrl+O`, `Ctrl+S`, `Ctrl+Shift+S`, `Ctrl+B`,
  `Ctrl++`/`Ctrl+-`/`Ctrl+0`, `Delete`, `F1`, `Ctrl+Q`
- `src/paths.py` for correct resource lookup in frozen (PyInstaller) builds
- Regression test suite (`tests/test_flow_fixes.py`)

### Changed
- Compression now actually downsamples/re-encodes images and subsets fonts;
  the quality control is respected (previously it was ignored)
- The library de-duplicates files by full path
- Fast onedir build mode by default; release mode is opt-in
- PyInstaller collects only the Qt modules the app imports

### Removed
- QtWebEngine / PDF.js preview and `viewer.html`
- Unused `progress.py` widget and the Pillow dependency

### Fixed
- Reorder panel applied 1-based page numbers as 0-based indices, producing
  out-of-range pages (`3,1,2` became `[3,1,2]`)
- Invalid page text raised an uncaught `ValueError` inside a Qt slot; the
  panels now emit a validation signal that shows a message box
- Operations could silently overwrite their own source file; the engine now
  refuses to write over an input
- `PdfFile.is_encrypted` reported `False` for files opened with a password
- Busy state could stay stuck after an operation finished or failed
- Delete shortcut was registered twice (widget + menu)
- Icons/resources were not found in frozen builds

---

## [1.0.0] - 2026-11-22

### Added
- First public release
- Core operations: merge, split, rotate, reorder, watermark
- Security: AES-256 encrypt, decrypt, permission flags
- Optimization: compress
- Conversion: PDF → Images, Images → PDF
- Drag & drop file loading with reordering
- Dark theme
- Offline-first architecture with no network calls
- Documentation (README, USER_GUIDE, CONTRIBUTING, CODE_OF_CONDUCT)
- PyInstaller build script for standalone executables

---

## Release Template

### [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Now removed features

### Fixed
- Bug fixes

### Security
- Vulnerability fixes
