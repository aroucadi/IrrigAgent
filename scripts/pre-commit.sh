#!/usr/bin/env bash
# Quality & Security Gate - Git Pre-Commit Hook

set -e

# Terminal ANSI Color Codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}     IrrigAgent Quality & Security Pre-Commit Gate  ${NC}"
echo -e "${BLUE}====================================================${NC}"

# Detect Python executable
if command -v python3 > /dev/null 2>&1; then
    PY_BIN="python3"
elif command -v python > /dev/null 2>&1; then
    PY_BIN="python"
elif command -v py > /dev/null 2>&1; then
    PY_BIN="py"
elif [ -f ".venv/Scripts/python.exe" ]; then
    PY_BIN=".venv/Scripts/python.exe"
else
    PY_BIN="python"
fi

# Identify staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    echo -e "${GREEN}[✓] Stage 0: No staged files to check.${NC}"
    exit 0
fi

# ----------------------------------------------------
# STAGE 1: Secret Scanning
# ----------------------------------------------------
echo -e "\n${BLUE}[+] Running Stage 1: Secret Scanning...${NC}"

SECRET_FOUND=0

# Loop through staged files and scan for hardcoded credentials
for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        # Exclude documentation files under specs/ from secret scanning
        case "$file" in
            specs/*|*.md)
                continue
                ;;
        esac

        # Extract added lines in diff, filtering out pattern definition lines in scripts
        ADDED_LINES=$(git diff --cached "$file" | grep '^+' | grep -v '+++' | grep -v -E 'grep -E|\$diffContent -match|SECRET DETECTED|Potential Google Cloud' || true)
        
        if [ -n "$ADDED_LINES" ]; then
            # Check Meta WhatsApp tokens (e.g. EAAB..., EAAG..., EAAC...)
            if echo "$ADDED_LINES" | grep -E 'EAAB[A-Za-z0-9]{20,}|EAAG[A-Za-z0-9]{20,}|EAAC[A-Za-z0-9]{20,}' > /dev/null 2>&1; then
                echo -e "${RED}[✗] SECRET DETECTED in $file: Potential Meta WhatsApp Access Token${NC}"
                SECRET_FOUND=1
            fi
            
            # Check GCP Service Account Keys
            if echo "$ADDED_LINES" | grep -E '"type":\s*"service_account"|-----BEGIN PRIVATE KEY-----' > /dev/null 2>&1; then
                echo -e "${RED}[✗] SECRET DETECTED in $file: Potential Google Cloud Service Account Key${NC}"
                SECRET_FOUND=1
            fi
            
            # Check Firestore / GCP API Keys
            if echo "$ADDED_LINES" | grep -E 'AIzaSy[A-Za-z0-9_-]{33}' > /dev/null 2>&1; then
                echo -e "${RED}[✗] SECRET DETECTED in $file: Potential Firestore/GCP API Key${NC}"
                SECRET_FOUND=1
            fi
        fi
    fi
done

if [ $SECRET_FOUND -ne 0 ]; then
    echo -e "${RED}\n[✗] Stage 1 FAIL: Hardcoded credentials or tokens detected in staged files!${NC}"
    echo -e "${YELLOW}Fix instructions: Remove secret values, use environment variables, and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}[✓] Stage 1 PASS: No hardcoded credentials detected.${NC}"

# ----------------------------------------------------
# STAGE 2: Code Linting & Formatting (Python Files)
# ----------------------------------------------------
STAGED_PY_FILES=$(echo "$STAGED_FILES" | grep -E '\.py$' || true)

if [ -n "$STAGED_PY_FILES" ]; then
    echo -e "\n${BLUE}[+] Running Stage 2: Code Linting & Formatting...${NC}"
    
    # Check if ruff is available
    if command -v ruff > /dev/null 2>&1; then
        echo "Running ruff check..."
        if ! ruff check .; then
            echo -e "${RED}[✗] Stage 2 FAIL: ruff check found lint errors.${NC}"
            echo -e "${YELLOW}Fix instructions: Run 'ruff check --fix .' to fix lint errors.${NC}"
            exit 1
        fi
    elif $PY_BIN -m ruff --version > /dev/null 2>&1; then
        echo "Running ruff check via $PY_BIN -m ruff..."
        if ! $PY_BIN -m ruff check .; then
            echo -e "${RED}[✗] Stage 2 FAIL: ruff check found lint errors.${NC}"
            echo -e "${YELLOW}Fix instructions: Run '$PY_BIN -m ruff check --fix .' to fix lint errors.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}[!] ruff linter not found, skipping ruff check.${NC}"
    fi

    # Check if black is available
    if command -v black > /dev/null 2>&1; then
        echo "Running black --check..."
        if ! black --check .; then
            echo -e "${RED}[✗] Stage 2 FAIL: black format check failed.${NC}"
            echo -e "${YELLOW}Fix instructions: Run 'black .' to format python code.${NC}"
            exit 1
        fi
    elif $PY_BIN -m black --version > /dev/null 2>&1; then
        echo "Running black --check via $PY_BIN -m black..."
        if ! $PY_BIN -m black --check .; then
            echo -e "${RED}[✗] Stage 2 FAIL: black format check failed.${NC}"
            echo -e "${YELLOW}Fix instructions: Run '$PY_BIN -m black .' to format python code.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}[!] black formatter not found, skipping black check.${NC}"
    fi

    echo -e "${GREEN}[✓] Stage 2 PASS: Linting and formatting clean.${NC}"
else
    echo -e "\n${GREEN}[✓] Stage 2 PASS: No Python files staged.${NC}"
fi

# ----------------------------------------------------
# STAGE 3: Fast Unit & Regex Tests
# ----------------------------------------------------
echo -e "\n${BLUE}[+] Running Stage 3: Fast Unit & Regex Tests...${NC}"

if command -v pytest > /dev/null 2>&1; then
    PYTEST_CMD="pytest"
else
    PYTEST_CMD="$PY_BIN -m pytest"
fi

if ! $PYTEST_CMD tests/unit/ -v; then
    echo -e "${RED}\n[✗] Stage 3 FAIL: Fast unit tests failed!${NC}"
    echo -e "${YELLOW}Fix instructions: Fix failing unit tests before committing.${NC}"
    exit 1
fi

echo -e "${GREEN}[✓] Stage 3 PASS: Core unit tests passed cleanly.${NC}"

echo -e "\n${GREEN}====================================================${NC}"
echo -e "${GREEN} [✓] ALL QUALITY & SECURITY GATES PASSED (Commit OK) ${NC}"
echo -e "${GREEN}====================================================${NC}"
exit 0
