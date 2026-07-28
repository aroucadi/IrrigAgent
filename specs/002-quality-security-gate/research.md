# Research & Technical Decisions: Quality & Security Gate Module

## 1. Secret Scanning in Git Pre-Commit Hook

### Decision
Use a lightweight POSIX shell script (`grep -E` / regex matching) over `git diff --cached` staged contents to scan for API keys and sensitive credentials before commit completion.

### Rationale
- Zero additional external heavy dependencies required (keeps pre-commit hook execution under 3.0 seconds).
- Native execution in Git Bash, macOS, and Linux terminal environments.

### Patterns Monitored
- **Meta WhatsApp Access Tokens**: `EAAB...`, `EAAG...`, `EAAC...`, or `WHATSAPP_ACCESS_TOKEN`
- **Google Cloud Service Account Keys**: GCP Service Account JSON key structures or `-----BEGIN PRIVATE KEY-----`
- **GCP / Firebase API Keys**: `AIzaSy[A-Za-z0-9_-]{33}`

### Alternatives Considered
- *Trufflehog / Gitleaks*: Powerful but requires external binary installations across developer setups, introducing dependency friction and potential sub-3.0 second performance degradation.

---

## 2. Code Linting & Fast Test Execution Strategy

### Decision
Execute Stage 2 (`ruff check .` and `black --check .`) and Stage 3 (`pytest tests/unit/ -v`) conditionally when Python files are staged or changed.

### Rationale
- Running linting and fast unit tests ensures zero formatting/logic regression enters the repo.
- Restricting tests run in pre-commit to `tests/unit/` ensures sub-3.0 second execution speed.

---

## 3. Hook Setup Script (`scripts/install-hooks.sh`)

### Decision
Provide `scripts/install-hooks.sh` that copies `scripts/pre-commit.sh` to `.git/hooks/pre-commit`, applying `chmod +x`.

### Rationale
- Ensures cross-platform compatibility (Windows Git Bash, macOS, Linux) without hard symlink dependency issues on Windows filesystems.
- Single shell command installation (`bash scripts/install-hooks.sh`) standardizes developer experience.

---

## 4. Test Suite Enhancements

### Decision
Expand `tests/unit/test_regex_parser.py` to cover Option 1, Option 2, and Option 3 edge cases (`3 +10 min at 05:00`, `3 -15 min`, `3 06h30`, invalid formats).
Expand `tests/integration/test_webhook.py` to cover FastAPI webhook endpoints (`/webhook` GET and POST) with mocked Async Firestore and WhatsApp API calls.

### Rationale
- Validates end-to-end webhook processing logic and regex parsing resilience without network calls or external database side effects.
