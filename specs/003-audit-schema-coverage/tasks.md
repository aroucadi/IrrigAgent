# Tasks: Audit Schema & Test Coverage Extension

**Input**: Design documents from `specs/003-audit-schema-coverage/`

**Prerequisites**: [plan.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/003-audit-schema-coverage/plan.md), [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/003-audit-schema-coverage/spec.md), [research.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/003-audit-schema-coverage/research.md), [data-model.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/003-audit-schema-coverage/data-model.md), [contracts/](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/003-audit-schema-coverage/contracts/)

**Organization**: Tasks are grouped by phase and user story to enable independent implementation and testing.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2)
- Exact file paths are specified in descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project prerequisites and base test suite health

- [x] T001 Verify active test environment by executing existing pytest suite via command line

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define strict Pydantic v2 data models required across API endpoints

- [x] T002 Create Pydantic v2 schema definitions (`HealthCheckResponse`, `FarmProfile`, `DailyAdvisoryJobResponse`, `WebhookVerification`) in `app/schemas.py`

---

## Phase 3: User Story 1 - Enforce Strict Data Validation Schemas (Priority: P1) 🎯 MVP

**Goal**: Refactor application API endpoints to enforce Pydantic v2 schema validations and structured response types.

**Independent Test**: Execute `GET /health`, `POST /webhook`, and `POST /jobs/daily-recommendations` to confirm valid JSON serialization matching Pydantic schemas.

### Implementation for User Story 1

- [x] T003 [US1] Import Pydantic models from `app/schemas.py` and annotate `GET /health` with `response_model=HealthCheckResponse` in `app/main.py`
- [x] T004 [US1] Annotate batch recommendation endpoints `POST /jobs/daily-recommendations` and `POST /api/v1/jobs/daily-advisory` with `response_model=DailyAdvisoryJobResponse` in `app/main.py`
- [x] T005 [US1] Verify schema payload validation and error handling across endpoints in `app/main.py`

**Checkpoint**: User Story 1 complete — all API endpoints enforce strict schema serialization.

---

## Phase 4: User Story 2 - Complete Integration Test Coverage Matrix (Priority: P2)

**Goal**: Add explicit pytest integration test cases for health check and job alias endpoints to achieve 100% route test coverage.

**Independent Test**: Run `pytest tests/integration/test_webhook.py` and confirm all test cases pass.

### Implementation for User Story 2

- [x] T006 [P] [US2] Add explicit test case `test_health_endpoint()` verifying `GET /health` status 200 and schema attributes in `tests/integration/test_webhook.py`
- [x] T007 [P] [US2] Add explicit test case `test_daily_advisory_alias_endpoint()` verifying status, authorization rules, and body payload for `POST /api/v1/jobs/daily-advisory` in `tests/integration/test_webhook.py`

**Checkpoint**: User Story 2 complete — integration test matrix reaches 100% endpoint coverage.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Verification and final test suite execution

- [x] T008 [P] Run full `pytest` test suite to verify 100% pass rate across 34+ unit and integration test cases
- [x] T009 Run quickstart validation guide scenarios per `specs/003-audit-schema-coverage/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion. BLOCKS User Story 1.
- **User Story 1 (Phase 3)**: Depends on Foundational completion (`app/schemas.py`).
- **User Story 2 (Phase 4)**: Depends on User Story 1 endpoint refactoring.
- **Polish (Phase 5)**: Depends on all user stories being complete.

### Parallel Opportunities

- T006 and T007 in Phase 4 can be implemented in parallel within `tests/integration/test_webhook.py`.
- T008 in Phase 5 can run in parallel with final verification checks.
