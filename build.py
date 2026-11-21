import sys
import os
import shutil
from pathlib import Path
import PyInstaller.__main__


def build():
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    resources_dir = project_root / "src" / "resources"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"

    # Clean previous builds
    for d in [dist_dir, build_dir]:
        if d.exists():
            shutil.rmtree(d)

    # Ensure resources directory exists
    resources_dir.mkdir(parents=True, exist_ok=True)

    # Create minimal viewer.html if not exists
    viewer_html = resources_dir / "viewer.html"
    if not viewer_html.exists():
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
            pdfjsLib.getDocument(url).promise.then(doc => {
                pdfDoc = doc;
                renderAll();
            });
        }
        function renderAll() {
            const viewer = document.getElementById('viewer');
            viewer.innerHTML = '';
            for (let i = 1; i <= pdfDoc.numPages; i++) {
                renderPage(i);
            }
        }
        function renderPage(num) {
            pdfDoc.getPage(num).then(page => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                const viewport = page.getViewport({scale: 1.5});
                canvas.width = viewport.width;
                canvas.height = viewport.height;
                const div = document.createElement('div');
                div.className = 'page';
                div.appendChild(canvas);
                document.getElementById('viewer').appendChild(div);
                page.render({canvasContext: ctx, viewport: viewport});
            });
        }
        window.renderPdf = render;
    </script>
</body>
</html>
""")

    # PyInstaller arguments
    args = [
        str(src_dir / "main.py"),
        "--name=PDF Toolkit",
        "--onefile",
        "--windowed",
        "--icon=src/resources/icon.ico",
        "--add-data=src/resources;resources",
        "--hidden-import=PySide6.QtWebEngine",
        "--hidden-import=PySide6.QtWebEngineWidgets",
        "--hidden-import=PySide6.QtWebEngineCore",
        "--hidden-import=fitz",
        "--hidden-import=PIL",
        "--collect-all=PySide6",
        f"--workpath={build_dir}",
        f"--distpath={dist_dir}",
        "--clean",
        "--noconfirm",
    ]

    # Add version file for Windows
    if sys.platform == "win32":
        version_file = project_root / "version.txt"
        version_file.write_text("""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
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
        args.append(f"--version-file={version_file}")

    print("Building with PyInstaller...")
    PyInstaller.__main__.run(args)

    exe_path = dist_dir / "PDF Toolkit.exe"
    if exe_path.exists():
        print(f"\nBuild successful!")
        print(f"Executable: {exe_path}")
        print(f"Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    else:
        print("\nBuild failed!")
        sys.exit(1)


if __name__ == "__main__":
    build()