# Tasks: v1.0 — ONSSA Live Registry Activation, Frost Alerts, Parcel UX Hardening, and Post-Selection IaC (gated)

**Input**: Design documents from `/specs/014-v1-0-post-selection-batch/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (`[US1]`, `[US2]`, `[US3]`, `[US4]`)
- File paths specified for all tasks

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verification of workspace and test environment

- [x] T001 Verify project test setup and directory structure in `specs/014-v1-0-post-selection-batch/`
- [x] T002 [P] Verify `data/` output directory and dependencies in `requirements.txt`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Threshold configuration constants for advisory decision engine

- [x] T003 [P] Configure `HEAT_WARNING_TEMP_C` (40.0) and `FROST_WARNING_TEMP_C` (2.0) default threshold constants in `app/config.py`

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Activate Live ONSSA Registry as Primary Source (Priority: P1) 🎯 MVP

**Goal**: Execute live ONSSA scrape commit run and wire CropDoctor product lookup to use dynamic registry first with static fallback.

**Independent Test**: Execute `pytest tests/unit/test_cropdoctor.py tests/test_cropdoctor_onssa.py` and verify dynamic lookup, static fallback, and fail-closed handling.

### Implementation for User Story 1

- [x] T004 [US1] Execute live ONSSA registry scrape commit run to generate `data/onssa_registry.json` via `scripts/sync_onssa_registry.py`
- [x] T005 [P] [US1] Add unit tests for dynamic ONSSA lookup, static fallback chain, and missing/malformed JSON dataset recovery in `tests/test_cropdoctor_onssa.py`
- [x] T006 [US1] Update `lookup_onssa_product()` in `app/cropdoctor.py` to query `data/onssa_registry.json` using normalized keys (`crop_type.strip().lower()`, `pathogen.strip().lower()`), with static catalog fallback and fail-closed handling
- [x] T007 [US1] Update existing unit tests in `tests/unit/test_cropdoctor.py` to verify dynamic registry primary lookup and regulatory disclaimer preservation

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Extreme Weather Advisory Alerts (Priority: P1)

**Goal**: Append frost (<2°C) and heatwave (>40°C) threshold warnings with actionable guidance to daily WhatsApp advisory messages.

**Independent Test**: Execute `pytest tests/unit/test_decision.py tests/unit/test_weather.py` and verify forecast evaluation against thresholds.

### Implementation for User Story 2

- [x] T008 [P] [US2] Add unit tests in `tests/unit/test_decision.py` covering heatwave (>40°C), frost (<2°C), normal temps, and rainfall-skip co-existence
- [x] T009 [US2] Implement extreme weather forecast threshold evaluation and advisory message formatting in `app/decision.py`
- [x] T010 [US2] Verify daily weather forecast payload fields in `app/weather.py` support min/max temperature threshold checks

**Checkpoint**: User Stories 1 AND 2 work independently and in combination.

---

## Phase 5: User Story 3 - Hardened Parcel Boundary Collection UX (Priority: P2)

**Goal**: Detect invalid boundary submissions (<3 pins, <5m apart, self-intersecting) and support multi-lingual reset commands.

**Independent Test**: Execute `pytest tests/unit/test_parcel_pin_collection.py` and verify boundary validation guidance responses and restart flow.

### Implementation for User Story 3

- [x] T011 [P] [US3] Add unit tests in `tests/unit/test_parcel_pin_collection.py` covering <3 pins, <5m pin distance, self-intersecting polygons, and reset commands
- [x] T012 [US3] Update boundary validation logic in `app/parcel_validation.py` to validate pin counts (<3), geodesic pin proximity (<5m), and self-intersecting polygon geometry
- [x] T013 [US3] Implement multi-lingual boundary restart command parser (`"restart boundary"`, `"restart"`, `"recommencer"`, `"réinitialiser"`, `"بداية جديدة"`) and state handler in `app/main.py`

**Checkpoint**: User Stories 1, 2, and 3 are fully functional independently.

---

## Phase 6: User Story 4 - Post-Selection Infrastructure as Code (Priority: P3, GATED)

**Goal**: Declarative IaC for post-selection cloud deployment.

**⚠️ HARD GATE — DO NOT IMPLEMENT NOW**: Tasks associated with this user story MUST NOT be executed until explicit maintainer confirmation of StartGate selection is recorded.

### Gated Placeholder Tasks

- [ ] T014 [US4] [BLOCKED / DEFERRED] Author GCP Cloud Run, Firestore, Scheduler, and IAM service account Terraform IaC in `infra/` (gated pending StartGate confirmation)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and zero-regression audit

- [x] T015 [P] Run quickstart validation scenarios in `specs/014-v1-0-post-selection-batch/quickstart.md`
- [x] T016 Run full automated test suite `pytest tests/` ensuring 100% pass rate and zero regressions

---

## Dependencies & Execution Order

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational phase (T003) - No story dependencies
- **User Story 2 (P1)**: Can start after Foundational phase (T003) - Independent of US1
- **User Story 3 (P2)**: Can start after Foundational phase (T003) - Independent of US1 & US2
- **User Story 4 (P3)**: BLOCKED pending explicit StartGate selection confirmation

### Parallel Opportunities

- `T002`, `T003` can run in parallel during Setup & Foundational
- `T005` (US1 tests), `T008` (US2 tests), `T011` (US3 tests) can run in parallel
- `T015` (quickstart guide verification) can run in parallel during Polish

---

## Implementation Strategy

### MVP Scope (User Story 1 First)

1. Complete Setup (T001-T002) + Foundational (T003)
2. Complete User Story 1 (T004-T007)
3. Run `pytest tests/unit/test_cropdoctor.py tests/test_cropdoctor_onssa.py` to validate MVP

### Incremental Delivery

1. Foundation + US1 (Dynamic ONSSA Triage) → MVP Delivery
2. Add US2 (Extreme Weather Alerts) → Increment 2 Delivery
3. Add US3 (Hardened Boundary Collection & Reset) → Increment 3 Delivery
4. US4 remains deferred pending StartGate selection confirmation
