"""One-time script to collect static PyInstaller spec values and write a frozen spec."""
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

datas = [('src/resources', 'resources')]
binaries = []
hiddenimports = ['fitz']

modules = [
    'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets',
    'PySide6.QtPdf', 'PySide6.QtPdfWidgets', 'PySide6.QtNetwork',
    'PySide6.QtPrintSupport'
]

for mod in modules:
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

if 'fitz' not in hiddenimports:
    hiddenimports.append('fitz')

# Write the frozen spec
spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_dynamic_libs
from PyInstaller.utils.hooks import collect_submodules

datas = {datas}
binaries = {binaries}
hiddenimports = {sorted(hiddenimports)}

a = analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PDF Toolkit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version.txt',
    icon=['src/resources/icon.ico'],
)
'''

with open('PDF Toolkit.spec', 'w') as f:
    f.write(spec_content)

print("Frozen PDF Toolkit.spec written successfully!")
print(f"datas length: {len(datas)}")
print(f"binaries length: {len(binaries)}")
print(f"hiddenimports length: {len(hiddenimports)}")
print(f"hiddenimports: {sorted(hiddenimports)}")