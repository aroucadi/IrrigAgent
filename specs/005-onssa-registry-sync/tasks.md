# Tasks: ONSSA Phytosanitary Registry Sync Tool

**Input**: Design documents from `specs/005-onssa-registry-sync/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-contract.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Basic directory setup for dataset outputs

- [x] T001 Ensure dataset output directory `data/` exists with `data/.gitkeep`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and politeness infrastructure required across user stories

- [x] T002 [P] Implement `robots.txt` check helper and politeness rate limiter in `scripts/sync_onssa_registry.py`
- [x] T003 [P] Define `PhytosanitaryProductEntry`, `SyncResult`, and metadata data models in `scripts/sync_onssa_registry.py`

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Dry-Run Extraction (Priority: P1) 🎯 MVP

**Goal**: Enable developer to run safe, flagless dry-run extraction up to `--limit N` entries (default 20) with stdout summary reporting and zero file persistence.

**Independent Test**: Execute `python scripts/sync_onssa_registry.py --limit 5` and verify stdout parsed rows and zero persistence to `data/onssa_registry.json`.

### Tests for User Story 1

- [x] T004 [P] [US1] Create unit tests for HTML row parsing and CLI dry-run behavior in `tests/test_sync_onssa_registry.py`

### Implementation for User Story 1

- [x] T005 [US1] Implement HTML parser for ONSSA WebForm product table rows in `scripts/sync_onssa_registry.py`
- [x] T006 [US1] Implement CLI argument parser with `--dry-run` default mode and `--limit N` (default 20) in `scripts/sync_onssa_registry.py`
- [x] T007 [US1] Implement execution summary reporter (parsed count, failed rows with raw content, elapsed time) in `scripts/sync_onssa_registry.py`

**Checkpoint**: User Story 1 fully functional and testable independently (MVP ready)

---

## Phase 4: User Story 2 - Full One-Shot Extraction with Explicit Persistence (Priority: P2)

**Goal**: Support explicit `--commit` extraction with WebForms postback state handling, politeness delay, exponential retry backoffs, checkpoint progress resilience, and persisted dataset generation at `data/onssa_registry.json`.

**Independent Test**: Execute `python scripts/sync_onssa_registry.py --commit --limit 2` and verify `data/onssa_registry.json` is created with metadata and entries array.

### Tests for User Story 2

- [x] T008 [P] [US2] Create unit tests for WebForms postback pagination, checkpoint saving/resuming, and `robots.txt` disallow handling in `tests/test_sync_onssa_registry.py`

### Implementation for User Story 2

- [x] T009 [US2] Implement ASP.NET WebForms postback session state navigator (`__VIEWSTATE`, `__EVENTVALIDATION`, `__VIEWSTATEGENERATOR`) in `scripts/sync_onssa_registry.py`
- [x] T010 [US2] Implement retry logic with exponential backoff for transient request failures in `scripts/sync_onssa_registry.py`
- [x] T011 [US2] Implement checkpoint progress persistence (`data/onssa_registry.checkpoint.json`) and resume capability in `scripts/sync_onssa_registry.py`
- [x] T012 [US2] Implement `--commit` flag persistence writing structured dataset and metadata to `data/onssa_registry.json`

**Checkpoint**: User Stories 1 and 2 work independently

---

## Phase 5: User Story 3 - Modular Structure for Scheduled Re-Sync (Priority: P3)

**Goal**: Expose programmatic `run_sync()` entrypoint function for automated background schedulers (Cloud Run Jobs / Cron).

**Independent Test**: Import `run_sync` from `scripts.sync_onssa_registry` in a Python test script and verify execution returns a valid `SyncResult`.

### Tests for User Story 3

- [x] T013 [P] [US3] Add unit test for programmatic module invocation `run_sync()` in `tests/test_sync_onssa_registry.py`

### Implementation for User Story 3

- [x] T014 [US3] Refactor core extraction runner into importable `run_sync()` entrypoint function in `scripts/sync_onssa_registry.py`

**Checkpoint**: Core sync engine reusable programmatically by schedulers

---

## Phase 6: User Story 4 - CropDoctor Runtime Dataset Integration & Documentation Update (Priority: P3)

**Goal**: Connect `app/cropdoctor.py` to read product recommendations from `data/onssa_registry.json` with fallback to `ONSSA_STATIC_CATALOG`, and update `README.md`.

**Independent Test**: Execute `pytest tests/test_cropdoctor_onssa.py` with `data/onssa_registry.json` present versus absent and verify lookup behavior.

### Tests for User Story 4

- [x] T015 [P] [US4] Create unit tests for CropDoctor dynamic dataset loading and static catalog fallback in `tests/test_cropdoctor_onssa.py`

### Implementation for User Story 4

- [x] T016 [US4] Implement `_load_onssa_catalog()` and treatment lookup logic in `app/cropdoctor.py`
- [x] T017 [P] [US4] Update system documentation in `README.md` to reflect expanded ONSSA phytosanitary registry dataset usage

**Checkpoint**: All user stories functional and integrated

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: System verification and final validation

- [x] T018 Run full automated test suite `pytest tests/` and verify 100% pass rate
- [x] T019 Execute quickstart validation scenarios from `specs/005-onssa-registry-sync/quickstart.md`


---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS user story tasks.
- **User Stories (Phases 3-6)**: All depend on Foundational completion.
  - US1 (Phase 3) → US2 (Phase 4) → US3 (Phase 5) → US4 (Phase 6).
- **Polish (Phase 7)**: Depends on all user stories being complete.

### Parallel Opportunities

- T002, T003 can run in parallel in Phase 2.
- Test tasks marked `[P]` (T004, T008, T013, T015, T017) can run in parallel before or alongside non-blocking file edits.

---

## Implementation Strategy

### MVP Scope (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational).
2. Complete Phase 3 (User Story 1: Dry-run extraction).
3. Validate: `python scripts/sync_onssa_registry.py --limit 5` (verify zero file output).
