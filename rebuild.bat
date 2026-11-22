@echo off
REM PDF Toolkit build launcher.
REM
REM Usage:
REM   rebuild.bat           Fast incremental dev build (onedir, cache reused).
REM   rebuild.bat release   Full one-file release build (slow, distributable).
REM
REM Fast mode uses a frozen .spec file for true incremental builds (~2s).
REM Release mode uses build.py for a full clean one-file build.

cd /d "%~dp0"

set MODE=fast
if /I "%~1"=="release" set MODE=release
if /I "%~1"=="--release" set MODE=release

echo ============================
echo PDF Toolkit - %MODE% build
echo ============================

if /I "%MODE%"=="release" (
    echo [1/3] Full clean for release build...
    if exist build rmdir /s /q build
    if exist dist rmdir /s /q dist
) else (
    echo [1/3] Fast incremental build (frozen spec^)
    REM Windows locks DLLs from recent runs. Rename old dir (works even when locked).
    if exist "dist\PDF Toolkit" (
        echo [CLEAN] Moving dist\PDF Toolkit to dist\PDF Toolkit.old...
        move /y "dist\PDF Toolkit" "dist\PDF Toolkit.old" >nul
    )
    REM Clean up old dirs from previous runs (best effort)
    for /d %%d in ("dist\PDF Toolkit.old*") do rmdir /s /q "%%d" 2>nul
)

set START_TIME=%TIME%
echo [2/3] Building...

if /I "%MODE%"=="release" (
    python build.py --release
) else (
    python -m PyInstaller -y "PDF Toolkit.spec"
)

if errorlevel 1 (
    echo.
    echo [3/3] Build FAILED - check output above
    exit /b 1
)

echo.
if /I "%MODE%"=="release" (
    set EXE=dist\PDF Toolkit.exe
) else (
    set EXE=dist\PDF Toolkit\PDF Toolkit.exe
)

if exist "%EXE%" (
    echo [3/3] Build SUCCESS!
    echo      Executable: %EXE%
    echo      Started  : %START_TIME%
    echo      Finished : %TIME%
    if /I "%MODE%"=="fast" (
        echo.
        echo Run with:    "%EXE%"
        echo Release with: rebuild.bat release
    )
) else (
    echo [3/3] Build FAILED - executable not found
    exit /b 1
)

echo.
echo ============================
echo Done!
echo ============================
