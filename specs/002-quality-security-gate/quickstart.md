# Quickstart & Verification Guide: Quality & Security Gate Module

## Prerequisites
- Active Python virtual environment with dependencies installed (`pip install -r requirements.txt pytest ruff black`).
- Git repository initialized.

## Step 1: Install Git Pre-Commit Hooks
Run the hook setup script from the project root:
```bash
bash scripts/install-hooks.sh
```
*Expected Result*: Green checkmark confirmation output: `[✓] Pre-commit hook installed successfully at .git/hooks/pre-commit`.

## Step 2: Test Secret Scanning Gate Failure
1. Create or edit a temporary file with a hardcoded token string (e.g. `WHATSAPP_TOKEN = "EAAB123456789"`).
2. Stage the file: `git add .`
3. Attempt commit: `git commit -m "test secret scan"`
4. *Expected Result*: Commit aborts with return code 1 and error message: `[✗] Secret scanning failed! Hardcoded credentials detected.`

## Step 3: Run Unit Test Suite
Run fast unit tests manually to verify test pass status:
```bash
pytest tests/unit/ -v
```
*Expected Result*: All regex parser and unit tests pass.

## Step 4: Verify Full Pre-Commit Gate (Clean Commit)
1. Unstage/remove temporary secret file.
2. Stage clean changes: `git add .`
3. Commit: `git commit -m "Add quality gate"`
4. *Expected Result*: All 3 stages (Secret Scanning, Code Formatting, Fast Unit Tests) pass under 3.0 seconds, displaying green checkmarks `[✓]`.
