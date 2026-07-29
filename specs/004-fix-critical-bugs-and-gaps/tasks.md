# Tasks: Critical Bug Fixes and Spec Alignment

**Input**: Design documents from `specs/004-fix-critical-bugs-and-gaps/`

**Prerequisites**: [`plan.md`](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/004-fix-critical-bugs-and-gaps/plan.md), [`spec.md`](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/004-fix-critical-bugs-and-gaps/spec.md), [`research.md`](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/004-fix-critical-bugs-and-gaps/research.md), [`data-model.md`](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/004-fix-critical-bugs-and-gaps/data-model.md), [`contracts/whatsapp-webhook.md`](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/004-fix-critical-bugs-and-gaps/contracts/whatsapp-webhook.md)

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story mapping ([US1], [US2], [US3], [US4], [US5])
- File paths are exact and project-relative (`app/`, `tests/`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project environment and test configuration readiness

- [x] T001 Verify project environment dependencies and pytest configuration in `pytest.ini`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core prerequisites before story implementation

- [x] T002 Verify base test utilities and fixtures in `tests/conftest.py`

---

## Phase 3: User Story 1 - Reliable Crop Disease Photo Diagnosis (Priority: P1) 🎯 MVP

**Goal**: Prevent real JPEG leaf photos from colliding with mock test signatures so all real farmer photos trigger live Gemini AI vision analysis.

**Independent Test**: Execute `pytest tests/unit/test_cropdoctor.py` and verify real JPEG image bytes do not trigger hardcoded mock diagnosis.

### Implementation for User Story 1

- [x] T003 [US1] Remove generic JPEG magic bytes check `startswith(b"\xFF\xD8\xFF\xE0")` in `app/cropdoctor.py` and restrict mock detection to exact byte equality `image_bytes == b"fake_high_confidence"` or explicit `force_confidence`.
- [x] T004 [P] [US1] Update unit test assertions in `tests/unit/test_cropdoctor.py` to test real JPEG bytes vs mock byte payloads.

**Checkpoint**: User Story 1 complete — real JPEG photos reach Gemini vision model while mock test fixtures pass cleanly.

---

## Phase 4: User Story 2 - Accurate Language Detection without Clock-Time Misclassifications (Priority: P2)

**Goal**: Prevent clock-time strings (`\dh\d` like `06h30`, `07h00`, `19h00`) from falsely triggering Arabizi script detection and altering user language state.

**Independent Test**: Execute `pytest tests/unit/test_firestore_client.py -k test_detect_arabizi` and verify clock-time strings preserve existing language state.

### Implementation for User Story 2

- [x] T005 [US2] Update `detect_arabizi_or_arabic_strict` in `app/firestore_client.py` to extract and strip clock-time tokens matching `\b\d{1,2}h\d{2}\b` before evaluating Arabizi digit/letter triggers.
- [x] T006 [P] [US2] Add unit tests for clock-time string exclusions (`07h00`, `19h00`, `06h30`) in `tests/unit/test_firestore_client.py`.

**Checkpoint**: User Story 2 complete — clock-time strings no longer trigger spurious Arabizi language switches.

---

## Phase 5: User Story 3 - Verified Farm Profile Data Schema Validation (Priority: P2)

**Goal**: Reconcile `FarmProfile` Pydantic schema field names with actual farm profile dictionaries and wire validation into profile update flows.

**Independent Test**: Execute `pytest tests/unit/test_schemas.py` and verify profile update validation cleanly accepts valid data and rejects invalid profile inputs.

### Implementation for User Story 3

- [x] T007 [P] [US3] Update `FarmProfile` Pydantic model in `app/schemas.py` with standard field names (`phone_number`, `location`, `crop_type`, `acreage_hectares`, `preferred_language`).
- [x] T008 [US3] Wire `FarmProfile.model_validate()` validation into `parse_profile_command` and profile persistence in `app/firestore_client.py` and `app/main.py`.
- [x] T009 [P] [US3] Add unit test suite for `FarmProfile` validation in `tests/unit/test_schemas.py`.

**Checkpoint**: User Story 3 complete — profile data is strictly validated against the standard schema.

---

## Phase 6: User Story 4 - Voice Teaser Feature Governance & Gated Rollout (Priority: P3)

**Goal**: Gate Darija Voice Output (TTS) behind `ENABLE_DARIJA_VOICE_TEASER=true` feature flag, ensure asynchronous background execution, and verify end-to-end WhatsApp audio delivery.

**Independent Test**: Execute `pytest tests/unit/test_tts_voice.py` and verify feature flag control and OGG/OPUS media dispatch.

### Implementation for User Story 4

- [x] T010 [US4] Verify feature flag check `ENABLE_DARIJA_VOICE_TEASER` in `app/tts_voice.py` and ensure synthesis fails silently without interrupting sub-second text replies.
- [x] T011 [P] [US4] Add OGG/OPUS media payload dispatch test (`upload_media` -> `send_audio_message`) in `tests/unit/test_tts_voice.py`.

**Checkpoint**: User Story 4 complete — voice output is cleanly gated and test-verified.

---

## Phase 7: User Story 5 - Strict Crop Catalog Fallback Elimination & Accurate Safety Claims (Priority: P1)

**Goal**: Remove silent fallback to tomatoes for unsupported crops in `lookup_onssa_product()` and refine README safety claim text to accurately scope pilot crop lookup guarantees.

**Independent Test**: Execute `pytest tests/unit/test_cropdoctor.py -k test_unsupported_crop` and verify triage for `crop_type="olives"` returns `onssa_product_pointer: None` across all confidence tiers.

### Implementation for User Story 5

- [x] T012 [US5] Update `lookup_onssa_product()` in `app/cropdoctor.py` to return `None` when `crop_type` is not present in `ONSSA_STATIC_CATALOG` (removing the `, ONSSA_STATIC_CATALOG["tomatoes"]` fallback).
- [x] T013 [P] [US5] Add unit test `test_cropdoctor_triage_unsupported_crop_type` in `tests/unit/test_cropdoctor.py` asserting that requests with `crop_type="olives"` return `onssa_product_pointer: None` and general retailer advice.
- [x] T014 [P] [US5] Update `README.md` safety claim section to state product names are strictly retrieved from a static lookup table scoped to pilot crops (tomatoes, citrus) and note that model confidence scores are uncalibrated self-reports.

**Checkpoint**: User Story 5 complete — unsupported crops fail closed without tomato chemical substitutions, and README safety claims are accurate.

---

## Phase 8: Polish & Verification

**Purpose**: End-to-end test execution and quality gate validation

- [x] T015 Run full test suite `.venv\Scripts\python.exe -m pytest tests/` to confirm 100% pass rate with zero errors and zero warnings.
- [x] T016 [P] Verify pre-commit hook gate execution and git status cleanliness.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup & Foundational (Phases 1-2)**: Complete.
- **User Stories 1-4 (Phases 3-6)**: Complete.
- **User Story 5 (Phase 7)**: Complete.
- **Polish (Phase 8)**: Complete.

### Parallel Opportunities

- T013 [US5] unit test addition can run in parallel with T012 code change.
- T014 [US5] README documentation update can run in parallel with code tasks.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phases 1 & 2.
2. Complete Phase 3 (US1: CropDoctor JPEG magic byte fix).

### Full Feature Delivery
1. Complete US1 → US2 → US3 → US4 → US5.
2. Execute full validation suite in Phase 8.
