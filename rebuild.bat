@echo off
REM Quick rebuild script for PDF Toolkit
cd /d "%~dp0"

echo ============================
echo PDF Toolkit - Quick Rebuild
echo ============================

echo [1/4] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [2/4] Building with PyInstaller...
python build.py

echo.
if exist "dist\PDF Toolkit.exe" (
    echo [3/4] Build SUCCESS!
    for %%f in ("dist\PDF Toolkit.exe") do (
        set FILESIZE=%%~zf
    )
    set /a SIZE_MB=%FILESIZE%/1024/1024
    echo      Executable: dist\PDF Toolkit.exe (%FILESIZE% bytes, %SIZE_MB% MB)
    echo [4/4] Ready to run: dist\PDF Toolkit.exe
) else (
    echo [3/4] Build FAILED - check output above
    exit /b 1
)

echo.
echo ============================
echo Done!
echo ============================