# Tasks: Pre-Demo Critical Fixes — Template-Based Daily Advisory, Dependency Fix, Mock-ID Backdoor Closure

**Input**: Design documents from `specs/016-pre-demo-critical-fixes/` and `implementation_plan.md`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `implementation_plan.md`

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Includes exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment check

- [x] T001 Verify project structure and configuration in `requirements.txt` and `app/config.py`

---

## Phase 2: Foundational & Dependency Fix (Blocking Prerequisites - US4 / CRIT-006)

**Purpose**: Fix missing dependency blocking clean virtual environment installation and FastAPI app startup

- [x] T002 [P] [US4] Add `python-multipart>=0.0.12` to `requirements.txt`
- [x] T003 [P] [US4] Execute clean virtual environment installation test script per `quickstart.md` to verify `python-multipart` resolution

**Checkpoint**: Foundational dependency fix complete — core user story implementation can begin.

---

## Phase 3: User Story 1 - Live 24-Hour Window Restriction Verification (Priority: P1)

**Goal**: Factually confirm Meta Cloud API out-of-window behavior (`131026` error code) using a real sandbox test number after 25+ hours without inbound traffic.

**Independent Test**: Trigger free-form message send after 25-hour wait, record exact Graph API error response in `research.md`.

- [x] T004 [US1] Execute 25-hour out-of-window verification test protocol on sandbox test phone number per `quickstart.md` and document exact timestamps and API error payload in `specs/016-pre-demo-critical-fixes/research.md`

---

## Phase 4: User Story 2 - Unified Message Template & Quick Reply Buttons (Priority: P1) 🎯 MVP

**Goal**: Implement `send_template_message()` for proactive daily advisories (`irrigagent_daily_advisory`) with 3 embedded Quick Reply buttons (`Approve`, `Skip`, `Modify`), and parse `button_reply` webhook payloads to standard text action routing.

**Independent Test**: `pytest tests/unit/test_whatsapp.py tests/integration/test_daily_batch_multi_farm.py`

- [x] T005 [P] [US2] Implement `send_template_message(to, template_name, language_code, components)` in `app/whatsapp.py` to construct Meta Cloud API `"type": "template"` payload with Quick Reply button components per `data-model.md`
- [x] T006 [P] [US2] Update `extract_incoming_message()` in `app/whatsapp.py` to parse Meta `interactive.button_reply` postback payloads, mapping `btn_approve` -> `"1"`, `btn_skip` -> `"2"`, `btn_modify` -> `"3"`
- [x] T007 [US2] Update daily recommendation job `/jobs/daily-recommendations` in `app/main.py` to dispatch daily advisories using `send_template_message()` with `irrigagent_daily_advisory` parameters and Quick Reply components
- [x] T008 [P] [US2] Add unit tests in `tests/unit/test_whatsapp.py` verifying `send_template_message()` payload structure and `extract_incoming_message()` button click postback parsing
- [x] T009 [P] [US2] Add integration tests in `tests/integration/test_daily_batch_multi_farm.py` verifying daily job dispatches template messages with correct Quick Reply components

**Checkpoint**: User Story 2 complete — daily advisory dispatches via approved template with 1-tap quick reply buttons.

---

## Phase 5: User Story 3 - Graceful Handling of Template Send Failures (Priority: P2)

**Goal**: Catch and log structured error details (phone number, error message, ISO timestamp) when template dispatch calls fail, without interrupting batch execution for remaining farm profiles.

**Independent Test**: `pytest tests/integration/test_daily_batch_multi_farm.py`

- [x] T010 [US3] Implement structured logging and exception handling around `send_template_message()` in `/jobs/daily-recommendations` in `app/main.py`
- [x] T011 [P] [US3] Add integration test in `tests/integration/test_daily_batch_multi_farm.py` asserting daily job logs failure details and increments `failed_count` when template dispatch raises an exception

**Checkpoint**: User Story 3 complete — template send failures are fully auditable and non-blocking.

---

## Phase 6: User Story 5 - Close Mock-Media-ID Production Backdoor (Priority: P1)

**Goal**: Remove fallback defaults `"mock_img_1"` and `"mock_audio_1"` in `app/main.py`, log raw missing media ID failures internally, and send friendly farmer-facing retry messages.

**Independent Test**: `pytest tests/integration/test_webhook.py`

- [x] T012 [US5] Remove `or "mock_img_1"` and `or "mock_audio_1"` fallback strings from production request handling in `app/main.py`
- [x] T013 [US5] Implement missing media ID handler in `app/main.py`'s `receive_webhook` to log internal payload details and send polite WhatsApp retry messages (`"🍃 Nous n'avons pas pu lire votre photo..."`) when photo/voice events lack media IDs
- [x] T014 [P] [US5] Add integration test in `tests/integration/test_webhook.py` asserting missing media ID payloads produce friendly retry text and internal log entries without executing mock triage or ASR fixtures

**Checkpoint**: User Story 5 complete — mock-ID production backdoor closed.

---

## Phase 7: Code Quality & Polish Fixes

**Purpose**: Audit code quality refinements and final end-to-end regression testing

- [x] T015 [P] Replace `.strip("```json").strip("```")` with explicit `removeprefix`/`removesuffix` / regex JSON parsing and clean up `importlib.import_module("google.genai")` imports in `app/decision.py` (SMELL-001 / SMELL-003)
- [x] T016 [P] Pass `out_shape=red_data.shape` to `src_nir.read(1, window=window, out_shape=red_data.shape)` in `app/sentinel.py` to force exact matching window dimensions during rasterio reads (SMELL-002)
- [x] T017 [P] Run complete automated test suite (`pytest`) and confirm 100% pass rate with zero regressions
- [x] T018 Execute all scenario checks in `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Fixes `requirements.txt` (US4 / CRIT-006) — BLOCKS clean app boot.
- **User Story 1 (Phase 3)**: Live 24-hour verification test running against sandbox number.
- **User Story 2 (Phase 4)**: Implementation of `send_template_message()` and `extract_incoming_message()` button parsing.
- **User Story 3 (Phase 5)**: Depends on US2 template dispatcher in `main.py`.
- **User Story 5 (Phase 6)**: Webhook handler media-ID backdoor fix in `main.py` (can proceed in parallel with US2/US3).
- **Code Quality & Polish (Phase 7)**: Minor refactorings (T015, T016) and final pytest suite execution (T017, T018).

### Parallel Opportunities

- T002 (`requirements.txt`), T005 (`whatsapp.py` template payload), T006 (`whatsapp.py` button parsing), T015 (`decision.py`), and T016 (`sentinel.py`) can be written in parallel.
- Test tasks T008 (`test_whatsapp.py`), T009 (`test_daily_batch_multi_farm.py`), T011 (`test_daily_batch_multi_farm.py`), T014 (`test_webhook.py`), and T017 (`pytest`) can be executed in parallel alongside main logic.
