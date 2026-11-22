"""Build script for PDF Toolkit.

Usage:
    python build.py                 # fast incremental onedir build (dev)
    python build.py --fast          # same, explicit
    python build.py --release       # slow one-file release build

Fast mode trades file size for build time:
  - --onedir instead of --onefile (no final packing step)
  - no --clean (PyInstaller cache is reused across runs)
  - UPX disabled
  - PySide6 collection narrowed to the submodules we actually use
  - build/ and dist/ are NOT wiped; PyInstaller reuses them

Release mode uses the same narrowed collection but packs everything into a
single executable. WebEngine is deliberately not collected: the preview uses
Qt's native PDF engine (QtPdf), which keeps the app offline and the build small.
"""
import shutil
import sys
from pathlib import Path

try:
    import PyInstaller.__main__
except ModuleNotFoundError:  # pragma: no cover - developer machine setup
    sys.exit(
        "PyInstaller is not installed in this environment.\n"
        "Install it first:  pip install pyinstaller"
    )

from src.__version__ import __version__


USED_PYSIDE_MODULES = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtPdf",
    "PySide6.QtPdfWidgets",
    "PySide6.QtNetwork",       # pulled in by Qt internals
    "PySide6.QtPrintSupport",  # file dialogs / printing helpers
]


def _write_version_file(project_root: Path) -> Path:
    version_file = project_root / "version.txt"
    parts = [int(p) for p in __version__.split(".") if p.isdigit()]
    while len(parts) < 4:
        parts.append(0)
    nums = ", ".join(str(p) for p in parts[:4])
    version_file.write_text(f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({nums}),
    prodvers=({nums}),
    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(u'040904B0',
        [StringStruct(u'CompanyName', u'Local'),
         StringStruct(u'FileDescription', u'PDF Toolkit'),
         StringStruct(u'FileVersion', u'{__version__}'),
         StringStruct(u'InternalName', u'pdf-toolkit'),
         StringStruct(u'LegalCopyright', u'Copyright (C) 2026'),
         StringStruct(u'OriginalFilename', u'PDF Toolkit.exe'),
         StringStruct(u'ProductName', u'PDF Toolkit'),
         StringStruct(u'ProductVersion', u'{__version__}')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
""")
    return version_file


def build(mode: str = "fast"):
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"

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
        # The entry script lives in src/, so the project root must be on the
        # analysis path for "import src.*" to resolve.
        f"--paths={project_root}",
        "--hidden-import=fitz",
        f"--workpath={build_dir}",
        f"--distpath={dist_dir}",
        "--noconfirm",
    ]

    # Collect only the PySide6 submodules the app imports. This is what keeps
    # the build in the tens of megabytes instead of bundling all of Qt.
    for mod in USED_PYSIDE_MODULES:
        args.append(f"--collect-submodules={mod}")
        args.append(f"--collect-binaries={mod}")
        args.append(f"--collect-data={mod}")

    # Never drag Chromium in through a stale hook/import.
    args.append("--exclude-module=PySide6.QtWebEngineCore")
    args.append("--exclude-module=PySide6.QtWebEngineWidgets")

    if release:
        args += ["--onefile", "--clean"]
    else:
        args += ["--onedir", "--noupx"]

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
            folder = exe_path.parent
            total = sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())
            print(f"Dist folder size: {total / (1024 * 1024):.1f} MB")
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
