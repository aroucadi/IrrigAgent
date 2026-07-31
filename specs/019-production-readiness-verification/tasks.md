# Tasks: Pre-Conversation Production Readiness Verification

**Input**: Design documents from `/specs/019-production-readiness-verification/`

**Prerequisites**: [plan.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/019-production-readiness-verification/plan.md) (required), [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/019-production-readiness-verification/spec.md) (required for user stories)

**Organization**: Tasks are grouped by user story and execution window to enable parallel verification while enforcing the mandatory 25+ hour wait window for User Story 1.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel during the 25-hour wait window (uses Test Phone B or local environment)
- **[Story]**: Which user story this task belongs to (`US1`, `US2`, `US3`, `US4`)
- Includes exact file paths in descriptions

---

## Phase 1: Setup (Verification Log & Environment Init)

**Purpose**: Initialize the primary deliverable verification log file and record baseline environment configuration.

- [x] T001 Initialize verification log file at `specs/019-production-readiness-verification/verification_log.md`
- [x] T002 Record target WhatsApp Cloud API Phone Number ID, Cloud Run endpoint URL, and test phone numbers (Phone A & Phone B) in `specs/019-production-readiness-verification/verification_log.md`

---

## Phase 2: Foundational (25-Hour Wait Window Initialization)

**Purpose**: Establish the baseline timestamp $T_0$ for User Story 1 and start the strict 25+ hour silence window on Test Phone A.

- [x] T003 Send baseline ping from Test Phone A, record timestamp $T_0$ in Firestore and in `specs/019-production-readiness-verification/verification_log.md`, and begin the 25-hour silence period

---

## Phase 3: User Story 2 - Interactive Button Verification (Priority: P1)

**Goal**: Confirm real interactive button taps (Approve/Skip/Modify and Confirm/Cancel) trigger expected downstream actions and Firestore state changes.

**Independent Test**: Perform button taps on Test Phone B and verify state changes in Firestore and reply transmissions in `specs/019-production-readiness-verification/verification_log.md`.

- [x] T004 [P] [US2] Verify `Approve` button callback, Firestore state mutation (`action=approved`), and outgoing confirmation response on Test Phone B in `specs/019-production-readiness-verification/verification_log.md`
- [x] T005 [P] [US2] Verify `Skip` button callback, Firestore state mutation (`action=skipped`), and outgoing response on Test Phone B in `specs/019-production-readiness-verification/verification_log.md`
- [x] T006 [P] [US2] Verify `Modify` button callback, prompt sequence for modified runtime input, and response on Test Phone B in `specs/019-production-readiness-verification/verification_log.md`
- [x] T007 [P] [US2] Verify Voice-Note `Confirm` and `Cancel` button callbacks and Firestore state updates on Test Phone B in `specs/019-production-readiness-verification/verification_log.md`

---

## Phase 4: User Story 3 - Opt-Out & Help Command Verification (Priority: P2)

**Goal**: Confirm `/stop` and `/help` keywords work on a real device, excluding opted-out profiles from batch runs and rendering localized guidance menus.

**Independent Test**: Send keywords from Test Phone B and inspect batch execution results and menu responses.

- [x] T008 [P] [US3] Verify `/stop` command updates Firestore profile to `opt_out=True` and daily batch job explicitly skips dispatch to Test Phone B in `specs/019-production-readiness-verification/verification_log.md`
- [x] T009 [P] [US3] Verify `/help` command renders localized menu guidance correctly on Test Phone B in `specs/019-production-readiness-verification/verification_log.md`

---

## Phase 5: User Story 4 - Dashboard Sanity Check Against Real Data (Priority: P2)

**Goal**: Run the engagement report generator against live Firestore data and assert "early/directional data" labeling and 0 fabricated figures.

**Independent Test**: Execute script locally against live Firestore database.

- [x] T010 [P] [US4] Execute `python scripts/generate_engagement_report.py` against live Firestore, assert presence of early/directional data label, audit for 0 synthetic numbers, and attach output snippet to `specs/019-production-readiness-verification/verification_log.md`

---

## Phase 6: User Story 1 - 24-Hour Window & Template Verification (Priority: P1) 🎯 MVP Core

**Goal**: Verify daily advisory dispatch behavior outside an active 24-hour customer service window on Test Phone A.

**Independent Test**: Execute daily job trigger against Test Phone A after 25+ hours of silence and log Meta API responses.

- [x] T011 [US1] Assert elapsed silence duration $\ge 25$ hours since $T_0$ on Test Phone A in `specs/019-production-readiness-verification/verification_log.md`
- [x] T012 [US1] Attempt free-form text message send to Test Phone A via `scripts/verify_whatsapp_24h_window.py` and record raw API response / Meta Error 131026 payload in `specs/019-production-readiness-verification/verification_log.md`
- [x] T013 [US1] Attempt daily advisory template message send to Test Phone A via `scripts/verify_whatsapp_24h_window.py` and record raw Meta API response in `specs/019-production-readiness-verification/verification_log.md`

---

## Phase 7: Polish & Discovered Gap Synthesis

**Purpose**: Summarize all empirical findings and clearly catalog any discovered infrastructure bugs or template approval gaps.

- [x] T014 Consolidate all empirical test evidence, raw API payloads, timestamps, and discovered gaps in `specs/019-production-readiness-verification/verification_log.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Can start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1 setup. BLOCKS User Story 1 completion.
- **Phases 3, 4, 5 (User Stories 2, 3, 4)**: Depend on Phase 1 setup. Can run IN PARALLEL during Phase 2's 25-hour wait window.
- **Phase 6 (User Story 1)**: BLOCKED by Phase 2 (must wait 25+ hours post-$T_0$).
- **Phase 7 (Polish & Synthesis)**: Depends on completion of all previous phases.

---

## Implementation Strategy

### MVP & Sequential Timeline

1. Execute T001 - T003 to start the 25-hour silence window.
2. In parallel during the 25-hour wait window, execute T004 - T010 (User Stories 2, 3, 4).
3. Once 25 hours elapse, execute T011 - T013 (User Story 1).
4. Complete T014 to finalize the verification log deliverable.
