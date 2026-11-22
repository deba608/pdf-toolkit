"""Freeze PyInstaller spec values to enable incremental builds."""
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

datas = [('src/resources', 'resources')]
binaries = []
hiddenimports = ['fitz']

pyide_modules = [
    'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets',
    'PySide6.QtPdf', 'PySide6.QtPdfWidgets', 'PySide6.QtNetwork',
    'PySide6.QtPrintSupport'
]

for mod in pyide_modules:
    df = collect_data_files(mod)
    for entry in df:
        datas.append(entry)

    bl = collect_dynamic_libs(mod)
    for entry in bl:
        binaries.append(entry)

    sm = collect_submodules(mod)
    for entry in sm:
        if entry not in hiddenimports:
            hiddenimports.append(entry)

# Build the spec content
hiddenimports_str = ", ".join(f"'{h}'" for h in sorted(hiddenimports))

spec_lines = [
    "# -*- mode: python ; coding: utf-8 -*-",
    "# PyInstaller frozen spec for PDF Toolkit",
    "# ALL VALUES ARE STATIC - no dynamic collect_* calls",
    "# This enables incremental builds by avoiding \"excludes changed\" TOC hash regeneration.",
    f"datas = {datas!r}",
    f"binaries = {binaries!r}",
    f"hiddenimports = {hiddenimports_str!r}",
    "",
    "a = Analysis(",
    "    ['src/main.py'],",
    "    pathex=['src'],",
    f"    binaries={binaries!r},",
    f"    datas=datas,",
    f"    hiddenimports={hiddenimports_str!r},",
    "    hookspath=[],",
    "    hooksconfig={{}},",
    "    runtime_hooks=[],",
    "    excludes=['PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets'],",
    "    noarchive=False,",
    "    optimize=0,",
    ")",
    "",
    "pyz = PYZ(a.pure)",
    "",
    "exe = EXE(",
    "    pyz,",
    "    a.scripts,",
    "    a.binaries,",
    "    a.datas,",
    "    [],",
    "    name='PDF Toolkit',",
    "    debug=False,",
    "    bootloader_ignore_signals=False,",
    "    strip=False,",
    "    upx=True,",
    "    upx_exclude=[],",
    "    runtime_tmpdir=None,",
    "    console=False,",
    "    disable_windowed_traceback=False,",
    "    argv_emulation=False,",
    "    target_arch=None,",
    "    codesign_identity=None,",
    "    entitlements_file=None,",
    "    version='version.txt',",
    "    icon=['src/resources/icon.ico'],",
    ")",
]

with open('PDF Toolkit.spec', 'w') as f:
    f.write("\n".join(spec_lines) + "\n")

print('Frozen PDF Toolkit.spec written successfully!')
print(f'datas: {len(datas)} entries')
print(f'binaries: {len(binaries)} entries')
print(f'hiddenimports: {len(hiddenimports)} entries: {hiddenimports_str}')