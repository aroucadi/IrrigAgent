# Tasks: Image Pre-Filter OpenCV Heuristics

**Input**: Design documents from `/specs/007-image-prefilter-heuristics/`

**Prerequisites**: [plan.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/007-image-prefilter-heuristics/plan.md), [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/007-image-prefilter-heuristics/spec.md), [research.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/007-image-prefilter-heuristics/research.md), [data-model.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/007-image-prefilter-heuristics/data-model.md), [contracts/image-prefilter-contract.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/007-image-prefilter-heuristics/contracts/image-prefilter-contract.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Includes exact file paths in all task descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependency installation and basic configuration

- [x] T001 Update dependencies in `requirements.txt` to include `opencv-python-headless>=4.8.0` and `numpy>=1.24.0`
- [x] T002 [P] Configure pre-filter environment settings and threshold defaults in `app/config.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schemas and module scaffold that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 [P] Define `QualityDefectReason`, `PreFilterConfig`, `ImageQualityMetrics`, and `QualityCheckResult` models in `app/schemas.py`
- [x] T004 Create base `validate_image_quality` function signature and configuration loader in `app/image_prefilter.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Fast Rejection of Blurry Photos (Priority: P1) 🎯 MVP

**Goal**: Instantly detect out-of-focus leaf photos via OpenCV Laplacian variance analysis and reject them before invoking Gemini 1.5 Flash vision.

**Independent Test**: Pass blurry and sharp synthetic images to `validate_image_quality()` and verify sub-second rejection with actionable retake guidance on blurry images.

### Tests for User Story 1

- [x] T005 [P] [US1] Write unit tests for Laplacian variance calculation, image decoding, and blur rejection in `tests/test_image_prefilter.py`

### Implementation for User Story 1

- [x] T006 [US1] Implement memory image decoding (`cv2.imdecode`) and Laplacian variance sharpness evaluation in `app/image_prefilter.py`
- [x] T007 [US1] Integrate blur pre-filter check as step 0 in `perform_cropdoctor_triage()` inside `app/cropdoctor.py` to bypass Gemini AI on blur failure

**Checkpoint**: At this point, User Story 1 (Blur Rejection MVP) is fully functional and independently testable

---

## Phase 4: User Story 2 - Validation of Extreme Exposure and Lighting (Priority: P2)

**Goal**: Detect underexposed (too dark) or overexposed (glare-heavy) photos using mean luminance and histogram clipping ratios.

**Independent Test**: Pass dark ($\mu < 40$) and bright ($\mu > 220$) test images to `validate_image_quality()` and verify rejection with exposure retake advice.

### Tests for User Story 2

- [x] T008 [P] [US2] Write unit tests for mean grayscale luminance and dark/bright pixel ratio validations in `tests/test_image_prefilter.py`

### Implementation for User Story 2

- [x] T009 [US2] Implement mean grayscale luminance and clipped dark/bright pixel percentage evaluation in `app/image_prefilter.py`
- [x] T010 [US2] Integrate exposure quality defect reporting into `validate_image_quality()` in `app/image_prefilter.py`

**Checkpoint**: User Stories 1 AND 2 are both functional and testable independently

---

## Phase 5: User Story 3 - Comprehensive Quality Gate & Diagnostic Logging (Priority: P3)

**Goal**: Provide detailed numerical diagnostic metrics, resolution bounds validation, and expose an optional `POST /cropdoctor/prefilter` REST endpoint.

**Independent Test**: Send an image payload to `POST /cropdoctor/prefilter` endpoint and verify the returned JSON contains full diagnostic metrics and execution latency.

### Tests for User Story 3

- [x] T011 [P] [US3] Write contract & integration tests for `POST /cropdoctor/prefilter` endpoint in `tests/test_image_prefilter.py`

### Implementation for User Story 3

- [x] T012 [US3] Implement image resolution validation and diagnostic metrics recording (`ImageQualityMetrics`) in `app/image_prefilter.py`
- [x] T013 [US3] Expose standalone `POST /cropdoctor/prefilter` REST endpoint in `app/main.py`

**Checkpoint**: All user stories (P1, P2, P3) are fully functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification and documentation

- [x] T014 [P] Update `specs/007-image-prefilter-heuristics/quickstart.md` with final API response schemas and test execution instructions
- [x] T015 Run full automated test suite (`pytest tests/`) to ensure 100% pass rate under zero-broken-tests policy

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion (P1 MVP)
- **User Story 2 (Phase 4)**: Depends on Foundational completion & `app/image_prefilter.py` base structure
- **User Story 3 (Phase 5)**: Depends on `app/image_prefilter.py` core heuristic logic
- **Polish (Phase 6)**: Depends on all user stories completion

### Parallel Opportunities

- `T002` (Config) and `T003` (Schemas) can be implemented in parallel
- `T005` (US1 Tests) and `T008` (US2 Tests) can be written in parallel
- `T014` (Documentation) can run in parallel with final verification

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational schemas & scaffold)
2. Complete Phase 3 (User Story 1: Blur Rejection)
3. **VALIDATE**: Run `pytest tests/test_image_prefilter.py -k test_blur` to confirm MVP blur rejection works without invoking Gemini
4. Proceed to Phase 4 (Exposure) and Phase 5 (REST Endpoint & Diagnostics)
