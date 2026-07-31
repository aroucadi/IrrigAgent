# Tasks: MVP Polish — WhatsApp Client Unit Tests & Multi-Farm Batch Integration Test

**Input**: Design documents from `/specs/013-mvp-polish-whatsapp-batch-tests/`  
**Prerequisites**: [plan.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/013-mvp-polish-whatsapp-batch-tests/plan.md), [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/013-mvp-polish-whatsapp-batch-tests/spec.md), [research.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/013-mvp-polish-whatsapp-batch-tests/research.md), [data-model.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/013-mvp-polish-whatsapp-batch-tests/data-model.md), [test-suite-contract.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/013-mvp-polish-whatsapp-batch-tests/contracts/test-suite-contract.md), [quickstart.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/013-mvp-polish-whatsapp-batch-tests/quickstart.md)

---

## Phase 1: Setup (Shared Test Infrastructure)

**Purpose**: Test directory environment validation and fixture setup

- [x] T001 Verify pytest test runner configuration and fixture helpers in tests/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core HTTP mocking and token override helpers for unit & integration testing

- [x] T002 Implement mock Graph API token override fixture helper in tests/conftest.py

---

## Phase 3: User Story 1 - Direct Unit Test Coverage for WhatsApp Client (Priority: P2) 🎯 Primary Unit Increment

**Goal**: Implement comprehensive isolated unit test coverage for `send_text_message()`, `upload_media()`, and `extract_incoming_message()` in `tests/unit/test_whatsapp.py` without live network calls.

**Independent Test**: Execute `pytest tests/unit/test_whatsapp.py` in isolation.

### Implementation for User Story 1

- [x] T003 [P] [US1] Create test file `tests/unit/test_whatsapp.py` with standard imports and fixtures
- [x] T004 [P] [US1] Implement `test_send_text_message_success()` asserting Graph API URL, Bearer auth header, JSON payload schema, and 200 response handling in tests/unit/test_whatsapp.py
- [x] T005 [P] [US1] Implement `test_send_text_message_http_error()` asserting 4xx/5xx HTTP error status exception handling in tests/unit/test_whatsapp.py
- [x] T006 [P] [US1] Implement `test_upload_media_success()` asserting multipart form construction, headers, and media ID extraction in tests/unit/test_whatsapp.py
- [x] T007 [P] [US1] Implement `test_upload_media_http_error()` asserting HTTP status error handling on media upload failure in tests/unit/test_whatsapp.py
- [x] T008 [P] [US1] Implement `test_extract_incoming_message_payloads()` asserting text, image, and voice/audio payload extraction in tests/unit/test_whatsapp.py
- [x] T009 [P] [US1] Implement `test_extract_incoming_message_non_message_and_malformed()` asserting status callbacks and invalid payloads evaluate to None in tests/unit/test_whatsapp.py

**Checkpoint**: `pytest tests/unit/test_whatsapp.py` passes 100% with complete coverage of WhatsApp client functions across success and error branches.

---

## Phase 4: User Story 2 - Multi-Farm Daily Batch Job Integration Test (Priority: P2)

**Goal**: Implement multi-farm daily recommendation batch execution integration test in `tests/integration/test_daily_batch_multi_farm.py` validating data differentiation and single-farm fault isolation.

**Independent Test**: Execute `pytest tests/integration/test_daily_batch_multi_farm.py` in isolation.

### Implementation for User Story 2

- [x] T010 [P] [US2] Create integration test file `tests/integration/test_daily_batch_multi_farm.py` with FastAPI TestClient setup and Firestore mocks
- [x] T011 [P] [US2] Implement `test_daily_batch_multi_farm_differentiation()` seeding 2 distinct farm profiles (Tomatoes/Agadir in French, Citrus/Berkane in Darija) and asserting farm-specific recommendations in tests/integration/test_daily_batch_multi_farm.py
- [x] T012 [P] [US2] Implement `test_daily_batch_single_farm_failure_resilience()` simulating weather lookup failure for Farm 1 and verifying Farm 2 processing completes successfully in tests/integration/test_daily_batch_multi_farm.py
- [x] T013 [P] [US2] Implement `test_daily_batch_all_farms_failure_resilience()` simulating weather lookup failure for all farms and verifying graceful batch endpoint completion in tests/integration/test_daily_batch_multi_farm.py

**Checkpoint**: `pytest tests/integration/test_daily_batch_multi_farm.py` passes 100% confirming multi-farm batch execution and fault isolation.

---

## Phase 5: Polish & Cross-Cutting Verification

**Purpose**: Execute full verification suite and validate zero regressions

- [x] T014 Execute full test suite `pytest tests/` ensuring 100% pass rate across unit and integration tests
- [x] T015 Verify quickstart guide instructions in specs/013-mvp-polish-whatsapp-batch-tests/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1)
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion (can run in parallel with Phase 3 or sequentially)
- **Polish (Phase 5)**: Depends on completion of User Story 1 and User Story 2

### Parallel Execution Opportunities

- Unit test cases within US1 (`T004` through `T009`) in `tests/unit/test_whatsapp.py` can be authored in parallel.
- Integration test cases within US2 (`T011` through `T013`) in `tests/integration/test_daily_batch_multi_farm.py` can be authored in parallel.
- US1 (`tests/unit/test_whatsapp.py`) and US2 (`tests/integration/test_daily_batch_multi_farm.py`) target completely separate files and can proceed in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 Unit Tests)

1. Complete Phase 1 & 2 Setup.
2. Implement User Story 1 unit tests (`tests/unit/test_whatsapp.py`).
3. Run `pytest tests/unit/test_whatsapp.py` to achieve 100% pass rate for WhatsApp client.

### Incremental Delivery (User Story 2 Integration Tests)

4. Implement User Story 2 multi-farm integration tests (`tests/integration/test_daily_batch_multi_farm.py`).
5. Run `pytest tests/integration/test_daily_batch_multi_farm.py` to achieve 100% pass rate for multi-farm batch processing.
6. Execute full verification suite `pytest tests/` to confirm zero regressions.
