#!/usr/bin/env pwsh
# Quick rebuild script for PDF Toolkit (PowerShell)

Set-Location $PSScriptRoot

Write-Host "============================" -ForegroundColor Cyan
Write-Host "PDF Toolkit - Quick Rebuild" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Cleaning previous build..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }

Write-Host "[2/4] Building with PyInstaller..." -ForegroundColor Yellow
python build.py

Write-Host ""
if (Test-Path "dist\PDF Toolkit.exe") {
    $size = (Get-Item "dist\PDF Toolkit.exe").Length
    $sizeMB = [math]::Round($size / 1MB, 1)
    Write-Host "[3/4] Build SUCCESS!" -ForegroundColor Green
    Write-Host "      Executable: dist\PDF Toolkit.exe ($sizeMB MB)" -ForegroundColor Green
    Write-Host "[4/4] Ready to run: dist\PDF Toolkit.exe" -ForegroundColor Green
} else {
    Write-Host "[3/4] Build FAILED - check output above" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan