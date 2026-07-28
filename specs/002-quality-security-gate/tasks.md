# Tasks: Quality & Security Gate Module

**Input**: Design documents from `/specs/002-quality-security-gate/`

**Prerequisites**: [plan.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/002-quality-security-gate/plan.md) (required), [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/002-quality-security-gate/spec.md) (required for user stories), [research.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/002-quality-security-gate/research.md), [data-model.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/002-quality-security-gate/data-model.md), [git-hook-interface.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/002-quality-security-gate/contracts/git-hook-interface.md), [quickstart.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/002-quality-security-gate/quickstart.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Explicit file paths are included in all task descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Repository script directory initialization

- [x] T001 Initialize script directory `scripts/`
- [x] T002 [P] Verify pytest configuration in `pytest.ini`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Pre-commit hook template structure and secret patterns definition

- [x] T003 Define secret scanning regex patterns (Meta tokens, GCP service account keys, Firestore API keys) and terminal color variables for shell scripts

---

## Phase 3: User Story 1 - Automated Pre-Commit Quality & Security Verification (Priority: P1) 🎯 MVP

**Goal**: Create versioned pre-commit hook script `scripts/pre-commit.sh` that executes Secret Scanning (Stage 1), Code Formatting (Stage 2: `ruff check .`, `black --check .`), and Fast Unit Tests (Stage 3: `pytest tests/unit/ -v`), failing with exit code 1 on errors.

**Independent Test**: Executing `bash scripts/pre-commit.sh` on staged files containing secrets or lint/test errors aborts execution with status 1.

### Implementation for User Story 1

- [x] T004 [P] [US1] Create versioned pre-commit hook script `scripts/pre-commit.sh` with Secret Scanning (Stage 1) for Meta tokens, GCP keys, and Firestore credentials
- [x] T005 [US1] Implement Code Linting & Formatting checks (`ruff check .`, `black --check .`) in `scripts/pre-commit.sh` (Stage 2)
- [x] T006 [US1] Implement Fast Unit Tests execution (`pytest tests/unit/ -v`) and terminal color formatting (green checkmarks, red error messages) in `scripts/pre-commit.sh` (Stage 3)

**Checkpoint**: At this point, `scripts/pre-commit.sh` is complete and independently testable.

---

## Phase 4: User Story 2 - One-Touch Developer Gate Setup (Priority: P2)

**Goal**: Provide setup script `scripts/install-hooks.sh` to install or update `.git/hooks/pre-commit` from `scripts/pre-commit.sh` with executable permissions.

**Independent Test**: Running `bash scripts/install-hooks.sh` creates/updates `.git/hooks/pre-commit` and verifies its executable permissions.

### Implementation for User Story 2

- [x] T007 [P] [US2] Create developer hook installation script `scripts/install-hooks.sh` (and PowerShell `scripts/install-hooks.ps1`) copying `scripts/pre-commit.sh` to `.git/hooks/pre-commit` and applying `chmod +x`
- [x] T008 [US2] Execute `bash scripts/install-hooks.sh` to install executable pre-commit hook in local `.git/hooks/pre-commit`

**Checkpoint**: Developer setup script installs local `.git/hooks/pre-commit` seamlessly.

---

## Phase 5: User Story 3 - Automated Test Suite Coverage for Decision Logic & Webhook Handlers (Priority: P3)

**Goal**: Expand test suite coverage for regex parser (options 1, 2, 3 and edge cases) and FastAPI webhook handlers (mocking Async Firestore & WhatsApp API calls).

**Independent Test**: `pytest tests/unit/ -v` and `pytest tests/integration/ -v` pass 100% of test cases.

### Implementation for User Story 3

- [x] T009 [P] [US3] Expand unit test suite in `tests/unit/test_regex_parser.py` covering Option 1 ("1"), Option 2 ("2"), Option 3 variations (`3 +10 min at 05:00`, `3 -15 min`, `3 06h30`, `3 -10 min at 04h15`), and unmatched fallback text
- [x] T010 [P] [US3] Expand integration test suite in `tests/integration/test_webhook.py` covering FastAPI `/webhook` GET verification handshake and POST payloads for Options 1, 2, 3 with Async Firestore and WhatsApp API mocks

**Checkpoint**: All user stories functional with high test coverage.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end verification and documentation update

- [x] T011 Run end-to-end quality gate validation per `quickstart.md`
- [x] T012 Update feature documentation and record task completion in `tasks.md`

---

## Phase 7: Convergence

**Purpose**: Cross-platform dual script standards compliance (Windows PowerShell + POSIX Shell)

- [x] T013 [P] Create twin PowerShell pre-commit hook script `scripts/pre-commit.ps1` for native Windows pre-commit gate execution per Constitution VIII (missing)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Completed.
- **Foundational (Phase 2)**: Completed.
- **User Story 1 (Phase 3)**: Completed.
- **User Story 2 (Phase 4)**: Completed.
- **User Story 3 (Phase 5)**: Completed.
- **Polish (Phase 6)**: Completed.
- **Convergence (Phase 7)**: Completed.
