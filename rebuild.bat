@echo off
REM PDF Toolkit build launcher.
REM
REM Usage:
REM   rebuild.bat           Fast incremental dev build (onedir, cache reused).
REM   rebuild.bat release   Full one-file release build (slow, distributable).
REM
REM The fast path keeps build\ and dist\ between runs so PyInstaller reuses
REM its analysis and binary caches. First run is ~normal speed; subsequent
REM runs are typically many times faster because only changed modules are
REM re-analyzed and nothing is recompressed.

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
    echo [1/3] Keeping build\ cache for incremental build...
    REM Only remove stale exe and PyInstaller's spec from a prior release,
    REM so the onedir output lands cleanly. Leave build\ alone so caches
    REM can be reused.
    if exist "dist\PDF Toolkit.exe" del /q "dist\PDF Toolkit.exe"
)

set START_TIME=%TIME%
echo [2/3] Building with PyInstaller (%MODE%)...
python build.py --%MODE%
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
