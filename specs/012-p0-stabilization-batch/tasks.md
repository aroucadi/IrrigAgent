# Tasks: P0 Stabilization — Real Voice Transcription, Terraform Scope Resolution, Spec Status Accuracy

**Input**: Design documents from `/specs/012-p0-stabilization-batch/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/voice_asr_api.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Includes exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project environment check & pre-execution setup

- [ ] T001 [P] Verify Python environment and dependencies in requirements.txt
- [ ] T002 [P] Verify pre-commit hooks and .specify/ directory status

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Baseline verification before implementing bug fixes

- [ ] T003 [P] Execute existing test suite pytest tests/ to establish 100% passing baseline

**Checkpoint**: Foundation ready — user story implementation can begin

---

## Phase 3: User Story 1 - Real Darija Voice Transcription (Priority: P1) 🎯 MVP (Resolves BUG-001)

**Goal**: Replace hardcoded transcript and confidence facade in `parse_voice_intent()` with an active Gemini 1.5 Flash Audio ASR call via Vertex AI SDK, preserving confidence gating, 60s duration cap, and confirmation loops. Add anti-mock regression test.

**Independent Test**: Run `pytest tests/unit/test_voice_darija_stt.py -v`. Verify that two dynamic mocked Vertex AI ASR responses produce distinct outputs and that hardcoded transcript facades fail the anti-mock test.

- [ ] T004 [P] [US1] Add anti-mock regression test in tests/unit/test_voice_darija_stt.py asserting dynamic Vertex AI SDK responses produce distinct transcripts
- [ ] T005 [US1] Implement Vertex AI Gemini 1.5 Flash Audio ASR call in parse_voice_intent() in app/decision.py
- [ ] T006 [US1] Implement exception handling and low-confidence fallback degradation in app/decision.py
- [ ] T007 [US1] Execute pytest tests/unit/test_voice_darija_stt.py verifying anti-mock test and fixture fallbacks pass 100%

**Checkpoint**: User Story 1 fully functional and testable independently

---

## Phase 4: User Story 2 - Terraform/IaC Scope Resolved Explicitly (Priority: P2) (Resolves BUG-003 - Option A)

**Goal**: Execute Option A — delete `infra/*.tf` files from the active build, update `.specify/memory/constitution.md` to permanently record IaC deferral for pilot deployment, and align project documentation.

**Independent Test**: Confirm zero `.tf` files exist in `infra/`, verify `.specify/memory/constitution.md` Section VII contains Option A policy, and confirm `README.md` contains no contradictory completion metrics.

- [ ] T008 [P] [US2] Delete infra/*.tf and infra/.terraform.lock.hcl files from infra/ directory
- [ ] T009 [P] [US2] Update .specify/memory/constitution.md Section VII to record Option A IaC deferral for pilot deployment
- [ ] T010 [US2] Audit and update README.md to align IaC deployment language with Option A constitution policy

**Checkpoint**: User Stories 1 AND 2 work independently

---

## Phase 5: User Story 3 - Spec Status Metadata Accuracy (Priority: P3) (Resolves BUG-004)

**Goal**: Update Status headers in `spec.md` files for specs 001, 002, 003, 005, 006, and 007 from `Draft` to `Implemented`. Retain `Status: Blocked` for specs 008 and 009.

**Independent Test**: Inspect top frontmatter/header lines of `specs/00*/spec.md`. Confirm specs 001-007 show `Status: Implemented`, and specs 008-009 show `Status: Blocked`.

- [ ] T011 [P] [US3] Update header status to Status: Implemented in specs/001-hassan-irrigation-agent/spec.md
- [ ] T012 [P] [US3] Update header status to Status: Implemented in specs/002-quality-security-gate/spec.md
- [ ] T013 [P] [US3] Update header status to Status: Implemented in specs/003-audit-schema-coverage/spec.md
- [ ] T014 [P] [US3] Update header status to Status: Implemented in specs/005-onssa-registry-sync/spec.md
- [ ] T015 [P] [US3] Update header status to Status: Implemented in specs/006-crop-etc-calculation/spec.md
- [ ] T016 [P] [US3] Update header status to Status: Implemented in specs/007-image-prefilter-heuristics/spec.md
- [ ] T017 [US3] Verify spec 008 and spec 009 header statuses remain Status: Blocked in specs/008-sentinel-canopy-heatmaps/spec.md and specs/009-voice-darija-stt-safety/spec.md

**Checkpoint**: All user story tasks complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end verification and final validation

- [ ] T018 [P] Run validation steps documented in specs/012-p0-stabilization-batch/quickstart.md
- [ ] T019 Execute full test suite pytest tests/ asserting 100% pass rate with zero regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS user story work.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion. User stories (US1, US2, US3) can proceed in priority order (US1 → US2 → US3) or in parallel across non-overlapping files.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Touches `app/decision.py` and `tests/unit/test_voice_darija_stt.py`.
- **User Story 2 (P2)**: Touches `infra/`, `.specify/memory/constitution.md`, and `README.md`. Independent of US1.
- **User Story 3 (P3)**: Touches `specs/00*/spec.md`. Independent of US1 and US2.

---

## Parallel Execution Opportunities

- `T001` and `T002` (Setup phase) can run in parallel.
- `T008` (Delete `infra/*.tf`), `T009` (Update `constitution.md`), and `T011`-`T016` (Update spec headers) can all run in parallel as they touch distinct files.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2 baseline checks.
2. Complete Phase 3 (US1: Voice ASR wiring & anti-mock test).
3. Validate US1 via `pytest tests/unit/test_voice_darija_stt.py`.

### Full Stabilization Batch Completion

1. Complete Phase 4 (US2: Delete `infra/*.tf` & update constitution).
2. Complete Phase 5 (US3: Update spec status headers across `specs/`).
3. Run Phase 6 validation (`quickstart.md` & full `pytest tests/`).
