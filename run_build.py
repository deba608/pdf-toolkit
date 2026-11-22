"""Run PyInstaller build with proper arguments."""
import sys
import PyInstaller.__main__

args = [
    'src/main.py',
    '--name=PDF Toolkit',
    '--windowed',
    '--icon=src/resources/icon.ico',
    '--add-data=src/resources;resources',
    '--paths=.',
    '--hidden-import=fitz',
    '--collect-submodules=PySide6.QtCore',
    '--collect-submodules=PySide6.QtGui',
    '--collect-submodules=PySide6.QtWidgets',
    '--collect-submodules=PySide6.QtPdf',
    '--collect-submodules=PySide6.QtPdfWidgets',
    '--collect-submodules=PySide6.QtNetwork',
    '--collect-submodules=PySide6.QtPrintSupport',
    '--exclude-module=PySide6.QtWebEngineCore',
    '--exclude-module=PySide6.QtWebEngineWidgets',
    '--noupx',
    '--onedir',
]

print(f"Building with PyInstaller [fast]...")
PyInstaller.__main__.run(args)

import pathlib
exe_path = pathlib.Path("dist/PDF Toolkit/PDF Toolkit.exe")
if exe_path.exists():
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"\nBuild successful.")
    print(f"Executable: {exe_path}")
    print(f"Exe size: {size_mb:.1f} MB")
else:
    print("\nBuild failed!")
    sys.exit(1)