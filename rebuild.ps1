#!/usr/bin/env pwsh
# Build launcher for PDF Toolkit (PowerShell).

#   ./rebuild.ps1               Fast incremental dev build (onedir, frozen spec)
#   ./rebuild.ps1 release        Full one-file release build

param([string]$Mode = "fast")
if ($Mode -notin @("fast", "release")) { $Mode = "fast" }

Set-Location $PSScriptRoot

Write-Host "============================" -ForegroundColor Cyan
Write-Host "PDF Toolkit - $Mode build" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

if ($Mode -eq "release") {
    Write-Host "[1/3] Full clean for release build..." -ForegroundColor Yellow
    if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
    if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
} else {
    Write-Host "[1/3] Fast incremental build (frozen spec)..." -ForegroundColor Yellow
    # Windows locks DLLs from recent runs. Rename old dir (works even when locked).
    if (Test-Path "dist\PDF Toolkit") {
        Write-Host "[CLEAN] Moving dist\PDF Toolkit to dist\PDF Toolkit.old..." -ForegroundColor Cyan
        Move-Item -Path "dist\PDF Toolkit" -Destination "dist\PDF Toolkit.old" -Force -ErrorAction SilentlyContinue
    }
    # Clean up old dirs from previous runs (best effort)
    Get-ChildItem "dist\PDF Toolkit.old*" -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

$started = Get-Date
Write-Host "[2/3] Building with PyInstaller ($Mode)..." -ForegroundColor Yellow

if ($Mode -eq "release") {
    python build.py --release
} else {
    python -m PyInstaller -y "PDF Toolkit.spec"
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[3/3] Build FAILED - check output above" -ForegroundColor Red
    exit 1
}

if ($Mode -eq "release") {
    $exe = "dist\PDF Toolkit.exe"
} else {
    $exe = "dist\PDF Toolkit\PDF Toolkit.exe"
}

Write-Host ""
if (Test-Path $exe) {
    $sizeMB = [math]::Round((Get-Item $exe).Length / 1MB, 1)
    $elapsed = [math]::Round(((Get-Date) - $started).TotalSeconds, 1)
    Write-Host "[3/3] Build SUCCESS!" -ForegroundColor Green
    Write-Host "      Executable: $exe ($sizeMB MB)" -ForegroundColor Green
    Write-Host "      Elapsed   : $elapsed s" -ForegroundColor Green
    Write-Host "      Run with  : `"$exe`"" -ForegroundColor Green
} else {
    Write-Host "[3/3] Build FAILED - executable not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan