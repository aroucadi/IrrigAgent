# Tasks: Anti-Fabrication Verification Tooling — Real Credential Enforcement, Raw-Output-Only Reporting

**Input**: Design documents from `/specs/020-anti-fabrication-verification-tooling/`

**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each tool.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verification script directory structure and shared imports

- [X] T001 Initialize verification scripts layout under `scripts/` directory per implementation plan
- [X] T002 Verify `_is_mock_token` is directly importable from `app/whatsapp.py` without modifying code in `app/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Credential guard & mock payload tripwire core module

**⚠️ CRITICAL**: Must be complete before individual verification tool scripts are constructed

- [X] T003 Create shared credential guard and mock tripwire module in `scripts/verify_credential_guard.py` implementing `is_real_credential_configured()` and `assert_no_mock_substring(payload)`

**Checkpoint**: Foundational guard ready - verification tools can now be implemented

---

## Phase 3: User Story 1 - Structural Guard Against Mock-Mode Fabrication (Priority: P1) 🎯 MVP

**Goal**: Refuse tool execution if credentials match mock/placeholder patterns or if response bodies contain `"mock"` substrings.

**Independent Test**: Execute `scripts/verify_credential_guard.py` with mock environment variables (`WHATSAPP_TOKEN="mock_123"`), asserting immediate non-zero error exit.

### Tests for User Story 1
- [X] T004 [P] [US1] Unit test for mock token rejection and response body tripwire in `tests/test_anti_fabrication_tooling.py`

### Implementation for User Story 1
- [X] T005 [US1] Wire `is_real_credential_configured()` into `scripts/verify_credential_guard.py` to validate `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, and `GCP_PROJECT_ID`

**Checkpoint**: User Story 1 functional - credential guard refuses mock runs

---

## Phase 4: User Story 2 - Real 24-Hour Messaging Window Verification (Priority: P1)

**Goal**: Two-step CLI tool (`--step=open` and `--step=check`) printing raw Meta API JSON responses without code-calculated timestamp deltas.

**Independent Test**: Run `python scripts/verify_window.py --step=open --to=+212600000001` and `--step=check --to=+212600000001` with real credentials, inspecting stdout for raw JSON payloads and mandatory human-responsibility notice.

### Implementation for User Story 2
- [X] T006 [P] [US2] Implement `--step=open` in `scripts/verify_window.py` calling `send_text_message()`, outputting raw JSON, and saving wall-clock timestamp to `.verify_window_last_open.json`
- [X] T007 [US2] Implement `--step=check` in `scripts/verify_window.py` calling `send_text_message()` and `send_template_message()`, printing both raw JSON response payloads verbatim
- [X] T008 [US2] Add mandatory stdout notice on `--step=check` in `scripts/verify_window.py` stating human wall-clock elapsed time is not asserted or calculated by code

**Checkpoint**: User Story 2 functional - two-step 24h window CLI tool ready for human execution

---

## Phase 5: User Story 3 - Real Meta Template Approval Status Check (Priority: P1)

**Goal**: CLI tool querying Meta Graph API Template Management endpoint and printing raw status JSON for WABA account templates.

**Independent Test**: Run `python scripts/check_template_status.py --waba-id=<WABA_ID>` with real credentials, confirming raw Meta Graph API template JSON payload stdout.

### Implementation for User Story 3
- [X] T009 [P] [US3] Implement Meta Template Management API GET query in `scripts/check_template_status.py` taking explicit `--waba-id` and `--name` CLI flags
- [X] T010 [US3] Add target WABA ID console display and raw JSON response output in `scripts/check_template_status.py`

**Checkpoint**: User Story 3 functional - template status query tool ready

---

## Phase 6: User Story 4 - Real Firestore Farm-Count Reality Check (Priority: P1)

**Goal**: CLI tool connecting directly to live Firestore infrastructure, printing GCP Project ID and raw list of farm profile counts and timestamps.

**Independent Test**: Run `python scripts/check_firestore_count.py` with real GCP credentials, confirming target GCP Project ID and raw farm profile list output.

### Implementation for User Story 4
- [X] T011 [P] [US4] Implement direct `google.cloud.firestore.Client` query in `scripts/check_firestore_count.py` without in-memory fallback dicts
- [X] T012 [US4] Add target GCP Project ID printout and unformatted farm count / document details in `scripts/check_firestore_count.py`

**Checkpoint**: User Story 4 functional - Firestore count reality check tool ready

---

## Phase 7: User Story 5 - Retroactive Correction of Fabricated Log (Priority: P2)

**Goal**: Mark existing `specs/019-production-readiness-verification/verification_log.md` as SUPERSEDED while preserving all original text intact.

**Independent Test**: Inspect `specs/019-production-readiness-verification/verification_log.md` for presence of the exact SUPERSEDED header banner.

### Implementation for User Story 5
- [X] T013 [P] [US5] Prepend SUPERSEDED header notice to `specs/019-production-readiness-verification/verification_log.md` preserving all original 166 lines

**Checkpoint**: User Story 5 complete - synthetic log record properly marked superseded

---

## Phase 8: Polish & Anti-Fabrication String Audit

**Purpose**: Ensure strict compliance with raw-output constraints across all tools and tests

- [X] T014 Run unit test suite `pytest tests/test_anti_fabrication_tooling.py` validating refusal behavior
- [X] T015 Perform codebase audit across `scripts/` and `tests/` confirming zero occurrences of forbidden summary strings ("PASS", "FAIL", "Verified", checkmark symbols)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 - BLOCKS all user stories.
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion.
- **Polish (Phase 8)**: Depends on completion of all user story tasks.

### User Story Completion Order

- **US1 (P1)**: Credential guard refusal tests & logic.
- **US2 (P1)**: 24h window CLI tool (`verify_window.py`).
- **US3 (P1)**: Meta template status CLI tool (`check_template_status.py`).
- **US4 (P1)**: Firestore count CLI tool (`check_firestore_count.py`).
- **US5 (P2)**: Log header correction (`specs/019-production-readiness-verification/verification_log.md`).

---

## Parallel Execution Opportunities

- `T004` (US1 test), `T006` (US2 window open), `T009` (US3 template check), `T011` (US4 Firestore query), and `T013` (US5 log update) affect separate files and can proceed in parallel once Phase 2 completes.

---

## Implementation Strategy

### MVP Scope (User Stories 1 & 2)
1. Complete Phase 1 & Phase 2 (Foundational guard).
2. Complete Phase 3 (US1 credential refusal).
3. Complete Phase 4 (US2 window check CLI tool).
4. Validate US1 and US2 independently.
