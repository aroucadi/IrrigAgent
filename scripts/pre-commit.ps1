# Quality & Security Gate - Git Pre-Commit Hook (Windows PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "====================================================" -ForegroundColor Blue
Write-Host "     IrrigAgent Quality & Security Pre-Commit Gate  " -ForegroundColor Blue
Write-Host "====================================================" -ForegroundColor Blue

# Detect Python binary
$PyBin = "python"
if (Get-Command "python3" -ErrorAction SilentlyContinue) {
    $PyBin = "python3"
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $PyBin = "py"
} elseif (Test-Path ".venv/Scripts/python.exe") {
    $PyBin = ".venv/Scripts/python.exe"
}

# Identify staged files
$StagedFiles = git diff --cached --name-only --diff-filter=ACM

if (-not $StagedFiles) {
    Write-Host "`n[+] Stage 0: No staged files to check." -ForegroundColor Green
    exit 0
}

# ----------------------------------------------------
# STAGE 1: Secret Scanning
# ----------------------------------------------------
Write-Host "`n[+] Running Stage 1: Secret Scanning..." -ForegroundColor Blue

$SecretFound = $false

foreach ($file in $StagedFiles) {
    if (Test-Path $file) {
        # Exclude documentation files under specs/ or .md files from secret scanning
        if ($file -match '^specs/' -or $file -match '\.md$') {
            continue
        }

        $diffLines = git diff --cached $file | Select-String -Pattern '^\+' | Where-Object { 
            $_ -notmatch '^\+\+\+' -and $_ -notmatch 'grep -E' -and $_ -notmatch '\$diffContent' -and $_ -notmatch 'SECRET DETECTED' -and $_ -notmatch 'Potential Google Cloud'
        }
        $diffContent = $diffLines -join "`n"

        if ($diffContent) {
            # Check Meta WhatsApp tokens (e.g. EAAB..., EAAG..., EAAC...)
            if ($diffContent -match 'EAAB[A-Za-z0-9]{20,}|EAAG[A-Za-z0-9]{20,}|EAAC[A-Za-z0-9]{20,}') {
                Write-Host "[x] SECRET DETECTED in $($file): Potential Meta WhatsApp Access Token" -ForegroundColor Red
                $SecretFound = $true
            }

            # Check GCP Service Account Keys
            if ($diffContent -match '"type":\s*"service_account"|-----BEGIN PRIVATE KEY-----') {
                Write-Host "[x] SECRET DETECTED in $($file): Potential Google Cloud Service Account Key" -ForegroundColor Red
                $SecretFound = $true
            }

            # Check Firestore / GCP API Keys
            if ($diffContent -match 'AIzaSy[A-Za-z0-9_-]{33}') {
                Write-Host "[x] SECRET DETECTED in $($file): Potential Firestore/GCP API Key" -ForegroundColor Red
                $SecretFound = $true
            }
        }
    }
}

if ($SecretFound) {
    Write-Host "`n[x] Stage 1 FAIL: Hardcoded credentials or tokens detected in staged files!" -ForegroundColor Red
    Write-Host "Fix instructions: Remove secret values, use environment variables, and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host "[+] Stage 1 PASS: No hardcoded credentials detected." -ForegroundColor Green

# ----------------------------------------------------
# STAGE 2: Code Linting & Formatting (Python Files)
# ----------------------------------------------------
$StagedPyFiles = $StagedFiles | Where-Object { $_ -match '\.py$' }

if ($StagedPyFiles) {
    Write-Host "`n[+] Running Stage 2: Code Linting & Formatting..." -ForegroundColor Blue

    if (Get-Command "ruff" -ErrorAction SilentlyContinue) {
        Write-Host "Running ruff check..."
        ruff check .
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[x] Stage 2 FAIL: ruff check found lint errors." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[!] ruff not found, checking via $PyBin -m ruff..." -ForegroundColor Yellow
        & $PyBin -m ruff check .
    }

    if (Get-Command "black" -ErrorAction SilentlyContinue) {
        Write-Host "Running black --check..."
        black --check .
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[x] Stage 2 FAIL: black format check failed." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[!] black not found, checking via $PyBin -m black..." -ForegroundColor Yellow
        & $PyBin -m black --check .
    }

    Write-Host "[+] Stage 2 PASS: Linting and formatting clean." -ForegroundColor Green
} else {
    Write-Host "`n[+] Stage 2 PASS: No Python files staged." -ForegroundColor Green
}

# ----------------------------------------------------
# STAGE 3: Fast Unit & Regex Tests
# ----------------------------------------------------
Write-Host "`n[+] Running Stage 3: Fast Unit & Regex Tests..." -ForegroundColor Blue

& $PyBin -m pytest tests/unit/ -v

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[x] Stage 3 FAIL: Fast unit tests failed!" -ForegroundColor Red
    Write-Host "Fix instructions: Fix failing unit tests before committing." -ForegroundColor Yellow
    exit 1
}

Write-Host "[+] Stage 3 PASS: Core unit tests passed cleanly." -ForegroundColor Green

Write-Host "`n====================================================" -ForegroundColor Green
Write-Host " [+] ALL QUALITY & SECURITY GATES PASSED (Commit OK) " -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
exit 0
