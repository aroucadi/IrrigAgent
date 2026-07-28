# Data Model & Components: Quality & Security Gate Module

## Components Overview

```
                 +-----------------------------------+
                 |           git commit              |
                 +-----------------------------------+
                                   |
                                   v
                 +-----------------------------------+
                 |       .git/hooks/pre-commit       |
                 |      (from scripts/pre-commit.sh) |
                 +-----------------------------------+
                                   |
         +-------------------------+-------------------------+
         |                         |                         |
         v                         v                         v
+------------------+     +-------------------+     +-------------------+
| Stage 1:         |     | Stage 2:          |     | Stage 3:          |
| Secret Scanning  |     | Code Formatting   |     | Fast Unit Tests   |
| - Meta Tokens    |     | - ruff check .    |     | - pytest tests/   |
| - GCP Service    |     | - black --check . |     |   unit/ -v        |
|   Account Keys   |     +-------------------+     +-------------------+
| - Firestore Keys |
+------------------+
```

## Gate Stage Specifications

### Stage 1: Secret Scanning Gate
- **Input**: Staged file diffs (`git diff --cached`)
- **Validation Rules**:
  - Reject commits containing hardcoded strings matching:
    - Meta WhatsApp tokens (`EAAB...`, `EAAG...`, `EAAC...`)
    - GCP Private Keys (`-----BEGIN PRIVATE KEY-----`)
    - GCP API Keys (`AIzaSy...`)
- **Output**: Return code 0 (pass) or 1 (fail with red terminal message).

### Stage 2: Code Linting & Formatting Gate
- **Input**: Staged Python files (`.py`)
- **Validation Rules**:
  - Run `ruff check .` across staged codebase.
  - Run `black --check .` on staged Python files.
- **Output**: Return code 0 (pass) or 1 (fail with formatting instructions).

### Stage 3: Fast Unit Tests Gate
- **Input**: `tests/unit/` test suite
- **Validation Rules**:
  - Execute `pytest tests/unit/ -v`.
- **Output**: Return code 0 (pass) or 1 (fail with failing test tracebacks).

## Developer Installation Script
- **Source Script**: `scripts/install-hooks.sh`
- **Target Path**: `.git/hooks/pre-commit`
- **Actions**: Copies script, sets executable mode (`chmod +x`), outputs green success confirmation.
