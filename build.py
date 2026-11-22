"""Build script for PDF Toolkit.

Usage:
    python build.py                 # fast incremental onedir build (dev)
    python build.py --fast          # same, explicit
    python build.py --release       # slow one-file release build (UPX, clean)

Fast mode trades file size for build time:
  - --onedir instead of --onefile (no final packing step)
  - no --clean (PyInstaller cache is reused across runs)
  - UPX disabled
  - PySide6 collection narrowed to the submodules we actually use
  - build/ and dist/ are NOT wiped; PyInstaller reuses them

Release mode is the original behavior, suitable for distribution.
"""
import sys
import os
import shutil
from pathlib import Path
import PyInstaller.__main__


USED_PYSIDE_MODULES = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtNetwork",      # pulled in by WebEngine
    "PySide6.QtPrintSupport", # harmless; some dialogs reach for it
]


def _write_viewer(resources_dir: Path):
    resources_dir.mkdir(parents=True, exist_ok=True)
    viewer_html = resources_dir / "viewer.html"
    if viewer_html.exists():
        return
    viewer_html.write_text("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; padding: 20px; background: #f0f0f0; font-family: sans-serif; }
        .viewer { background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        canvas { display: block; }
        .page { margin-bottom: 20px; }
    </style>
</head>
<body>
    <div id="viewer" class="viewer"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.min.js"></script>
    <script>
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.js';
        let pdfDoc = null;
        function render(url) {
            pdfjsLib.getDocument(url).promise.then(doc => { pdfDoc = doc; renderAll(); });
        }
        function renderAll() {
            const viewer = document.getElementById('viewer');
            viewer.innerHTML = '';
            for (let i = 1; i <= pdfDoc.numPages; i++) renderPage(i);
        }
        function renderPage(num) {
            pdfDoc.getPage(num).then(page => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                const viewport = page.getViewport({scale: 1.5});
                canvas.width = viewport.width; canvas.height = viewport.height;
                const div = document.createElement('div');
                div.className = 'page'; div.appendChild(canvas);
                document.getElementById('viewer').appendChild(div);
                page.render({canvasContext: ctx, viewport: viewport});
            });
        }
        window.renderPdf = render;
    </script>
</body>
</html>
""")


def _write_version_file(project_root: Path) -> Path:
    version_file = project_root / "version.txt"
    version_file.write_text("""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(u'040904B0',
        [StringStruct(u'CompanyName', u'Local'),
         StringStruct(u'FileDescription', u'PDF Toolkit'),
         StringStruct(u'FileVersion', u'1.0.0'),
         StringStruct(u'InternalName', u'pdf-toolkit'),
         StringStruct(u'LegalCopyright', u'Copyright (C) 2026'),
         StringStruct(u'OriginalFilename', u'PDF Toolkit.exe'),
         StringStruct(u'ProductName', u'PDF Toolkit'),
         StringStruct(u'ProductVersion', u'1.0.0')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
""")
    return version_file


def build(mode: str = "fast"):
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    resources_dir = project_root / "src" / "resources"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"

    _write_viewer(resources_dir)

    release = (mode == "release")

    if release:
        # Full clean for release
        for d in [dist_dir, build_dir]:
            if d.exists():
                shutil.rmtree(d)

    # Core args shared by both modes
    args = [
        str(src_dir / "main.py"),
        "--name=PDF Toolkit",
        "--windowed",
        "--icon=src/resources/icon.ico",
        "--add-data=src/resources;resources",
        "--hidden-import=fitz",
        "--hidden-import=PIL",
        f"--workpath={build_dir}",
        f"--distpath={dist_dir}",
        "--noconfirm",
    ]

    if release:
        # Slow, distributable: one-file, cleaned cache, everything from PySide6
        args += [
            "--onefile",
            "--clean",
            "--collect-all=PySide6",
            "--hidden-import=PySide6.QtWebEngine",
            "--hidden-import=PySide6.QtWebEngineWidgets",
            "--hidden-import=PySide6.QtWebEngineCore",
        ]
    else:
        # Fast dev build: one-dir, keep caches, narrow PySide6 collection
        args += [
            "--onedir",
            "--noupx",
        ]
        # Collect ONLY the submodules we actually use, as data/binaries/hiddenimports
        for mod in USED_PYSIDE_MODULES:
            args.append(f"--collect-submodules={mod}")
            args.append(f"--collect-binaries={mod}")
            args.append(f"--collect-data={mod}")
        # QtWebEngineProcess + its resources must travel with QtWebEngineCore;
        # collect-binaries/data on that module brings them.

    if sys.platform == "win32":
        version_file = _write_version_file(project_root)
        args.append(f"--version-file={version_file}")

    print(f"Building with PyInstaller [{mode}]...")
    PyInstaller.__main__.run(args)

    if release:
        exe_path = dist_dir / "PDF Toolkit.exe"
    else:
        exe_path = dist_dir / "PDF Toolkit" / "PDF Toolkit.exe"

    if exe_path.exists():
        print(f"\nBuild successful ({mode}).")
        print(f"Executable: {exe_path}")
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"Exe size: {size_mb:.1f} MB")
        if not release:
            # Report full folder size for onedir
            folder = exe_path.parent
            total = sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())
            print(f"Dist folder size: {total / (1024*1024):.1f} MB")
    else:
        print("\nBuild failed!")
        sys.exit(1)


if __name__ == "__main__":
    mode = "fast"
    for a in sys.argv[1:]:
        if a in ("--release", "release"):
            mode = "release"
        elif a in ("--fast", "fast"):
            mode = "fast"
    build(mode)
