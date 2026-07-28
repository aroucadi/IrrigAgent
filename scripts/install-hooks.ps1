# Developer Hook Setup Script for IrrigAgent (Windows PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "Installing IrrigAgent Git Pre-Commit Hooks..." -ForegroundColor Cyan

if (-not (Test-Path ".git")) {
    Write-Host "[✗] Error: .git directory not found. Please run this script from the repository root." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "scripts/pre-commit.sh")) {
    Write-Host "[✗] Error: scripts/pre-commit.sh not found." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".git/hooks")) {
    New-Item -ItemType Directory -Path ".git/hooks" | Out-Null
}

Copy-Item -Force -Path "scripts/pre-commit.sh" -Destination ".git/hooks/pre-commit"

Write-Host "[✓] Pre-commit hook installed successfully at .git/hooks/pre-commit" -ForegroundColor Green
