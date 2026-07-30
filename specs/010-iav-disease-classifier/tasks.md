# Tasks: Fine-Tuned Disease Classifier & IAV Hassan II Strategy

**Input**: Design documents from `/specs/010-iav-disease-classifier/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Revision**: v2 — Regenerated after `/speckit-analyze` + `/speckit-clarify` (2026-07-29). All 13 findings resolved, 10 clarification decisions encoded.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Update configuration defaults and Pydantic schema foundations for vision pre-filtering, calibration, and the new `VisionClassificationResult` formal contract.

- [x] T001 [P] Update Pydantic data schemas for **existing** response fields — `foliage_pixel_ratio` (float), `calibrated_confidence` (float), `fail_closed_active` (bool) — in `app/schemas.py`. *(Scope: updates to existing `ImageQualityMetrics` / `QualityCheckResult` models only. New IAVDatasetRecord is T005. New VisionClassificationResult is T003.)*
- [x] T002 [P] Verify environment configuration parameters in `app/config.py`: foliage green HSV range (`PREFILTER_MIN_HUE=35`, `PREFILTER_MAX_HUE=85` **in OpenCV 0–180 scale**), minimum foliage ratio (`PREFILTER_MIN_FOLIAGE_RATIO=0.30`), milestone count (`IAV_MILESTONE_SAMPLES=500`), fail-closed threshold (`FAIL_CLOSED_CONFIDENCE_THRESHOLD=0.75`), and temperature scaling parameter (`TEMPERATURE_SCALING_PARAM=1.25`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schema entities and confidence-gating logic required across all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 [P] Add formal `VisionClassificationResult` Pydantic model to `app/schemas.py` with fields: `pathogen_identified` (str), `symptom_name` (str|None), `confidence_score` (float), `calibrated_confidence` (float), `confidence_tier` (str|None), `fail_closed_active` (bool), `onssa_product_pointer` (str|None), `disclaimer_included` (bool), `is_unreadable` (bool), `response_text` (str). *(Resolves U3 — plan.md referenced this model but it was absent from schemas.py)*
- [x] T004 [P] Implement green channel foliage HSV heuristic analysis function `compute_foliage_green_ratio()` in `app/image_prefilter.py` using OpenCV range `[min_hue, max_hue]` **without** dividing by 2 — config values are already in OpenCV 0–180 scale. *(Bug was fixed in implementation; ensure function docstring explicitly states OpenCV scale.)*
- [x] T005 [P] Implement **new** `IAVDatasetRecord` Pydantic model in `app/schemas.py` with mandatory fields: `sample_id` (str), `image_path` (str), `crop_type` (Literal["tomatoes","citrus"]), `disease_onssa_code` (str), `severity_index` (int, 1–5), `bounding_boxes` (list[dict] with normalized 0.0–1.0 coords), optional `region` (Literal["Souss-Massa","Gharb"]), optional `cultivar` (str). *(Scope: new entity only — existing field updates are T001)*
- [x] T006 Update triage engine in `app/cropdoctor.py`: wire `apply_temperature_scaling(raw, T)` returning `raw ** T` (with T=1.25 default), populate `calibrated_confidence` and `fail_closed_active` on every triage response, expose both fields in returned dict/`VisionClassificationResult`

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Leaf Photo Disease Triage via Interim 2-Stage Pipeline (Priority: P1) 🎯 MVP

**Goal**: Process acceptable leaf photos through OpenCV quality gate and route to Zero-Shot Gemini 1.5 Flash + ONSSA RAG with ONSSA-authorized chemical pointers and full verbatim §III legal disclaimer.

**Independent Test**: `pytest tests/unit/test_cropdoctor.py -k "triage"`

### Implementation for User Story 1

- [x] T007 [P] [US1] Rename canonical ONSSA registry file from `data/onssa_registry.json` → `data/onssa_authorized_products.json` and update all references in `app/cropdoctor.py` (ONSSA_CATALOG lookup, RAG loader) and `app/config.py`. *(Resolves C2 — two filenames created ambiguity about the authoritative runtime registry)*
- [x] T008 [P] [US1] Extend ONSSA static catalog in `app/cropdoctor.py` for full target disease coverage: tomatoes (TYLCV, Tuta Absoluta, Early Blight) + citrus (HLB/Citrus Greening, Alternaria Leaf Spot, Red Spider Mite), all referenced against `data/onssa_authorized_products.json`
- [x] T009 [US1] Update all triage response text generation in `app/cropdoctor.py` to append the **exact verbatim** ONSSA §III disclaimer: *"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."* *(Resolves C1 — US1 Acceptance Scenario 1.2 was using the truncated short form)*
- [x] T010 [US1] Add unit tests for 2-stage interim triage pipeline in `tests/unit/test_cropdoctor.py`, including:
  - High-confidence path: ONSSA chemical pointer present, disclaimer verbatim match
  - Non-target crop redirect (olive/wheat → polite redirect message asserting: *"target vision support currently focuses on Tomatoes and Citrus"*) — existing partial test at L91 must be upgraded to assert exact redirect text *(Resolves G2)*
  - ONSSA registry unavailable fallback → cultural advice + disclaimer
- [x] T011 [US1] Integrate photo triage execution into WhatsApp webhook flow in `app/main.py` and format triage response for WhatsApp delivery in `app/whatsapp.py`

**Checkpoint**: User Story 1 fully functional and independently testable.

---

## Phase 4: User Story 2 - Photo Quality Feedback & Re-shoot Guidance Gate (Priority: P1)

**Goal**: Catch blurry (< 100.0 Laplacian variance), low-resolution (< 400px), or non-foliage (< 30% green HSV coverage in OpenCV 0–180 scale) photos immediately and return specific re-shoot instructions — no AI model invoked.

**Independent Test**: `pytest tests/test_image_prefilter.py -k "blur or resolution or foliage"`

### Implementation for User Story 2

- [x] T012 [P] [US2] Enhance `validate_image_quality()` in `app/image_prefilter.py` to evaluate foliage green hue coverage using `compute_foliage_green_ratio()` and reject if below `PREFILTER_MIN_FOLIAGE_RATIO` (0.30), populating `QualityDefectReason.NO_LEAF_DETECTED`
- [x] T013 [P] [US2] Add unit tests for Quality Gate in `tests/test_image_prefilter.py`:
  - Green leaf passes all three checks (blur ≥ 100, res ≥ 400px, foliage ≥ 30%)
  - Blurry image rejected (`BLURRY`)
  - Low-resolution image rejected (`RESOLUTION_TOO_LOW`)
  - Non-foliage image rejected (`NO_LEAF_DETECTED`)
  - Exactly 400×400px passes resolution check (boundary test)
  - `compute_foliage_green_ratio()` returns ≥ 0.30 for green images and < 0.30 for red/grey images
- [x] T014 [US2] Update quality defect feedback messages in `app/image_prefilter.py` for `NO_LEAF_DETECTED` defect reason: return *"Photo is blurry or unreadable. Please take a close-up photo of the leaf under direct light."*

**Checkpoint**: User Story 2 fully functional and independently testable.

---

## Phase 5: User Story 3 - Transition to Calibrated Fine-Tuned Model (Phase 2.2b Activation) (Priority: P2)

**Goal**: Switch primary vision engine from Zero-Shot Gemini 1.5 Flash to fine-tuned EfficientNet-B4 with temperature scaling calibration once dataset milestone is reached; enforce 75% fail-closed confidence threshold.

**Independent Test**: `pytest tests/test_iav_disease_classifier.py::TestFailClosedBehavior`

### Implementation for User Story 3

- [x] T015 [P] [US3] Add unit tests for temperature scaling calibration in `tests/test_iav_disease_classifier.py::TestApplyTemperatureScaling`:
  - `apply_temperature_scaling(0.90, T=1.25)` returns value **< 0.90** (T > 1 softens — formula: `p ** T`) *(Resolves I2 — formula was documented as `z/T` but implemented correctly as `p^T`)*
  - `apply_temperature_scaling(0.70, T=0.80)` returns value **> 0.70** (T < 1 amplifies)
  - `apply_temperature_scaling(x, T=1.0)` is identity
  - Boundary clamps: 0.0 and 1.0 inputs
- [x] T016 [P] [US3] Implement Phase 2.2b engine router toggle in `app/cropdoctor.py`: read `PHASE_2_2B_ACTIVE` env flag; when True route to fine-tuned EfficientNet-B4 path; when False (default) route to Zero-Shot Gemini 1.5 Flash path
- [x] T017 [US3] Implement `check_phase_22b_milestone()` in `app/cropdoctor.py`: count IAV dataset records per disease class from manifest; return True when all target classes have ≥ `IAV_MILESTONE_SAMPLES` (500) verified samples. Activation is **automatic** — no manual operator gate *(Resolves SC-004 activation trigger)*

**Checkpoint**: User Story 3 fully functional and independently testable.

---

## Phase 6: User Story 4 - IAV Hassan II Dataset Collaboration & Schema Ingestion (Priority: P3)

**Goal**: Validate and ingest IAV Hassan II field photo datasets with ONSSA codes, severity grade (1–5), and bounding boxes; report per-class sample counts toward Phase 2.2b milestone.

**Independent Test**: `pytest tests/test_iav_disease_classifier.py -k "TestValidateIAVDatasetRecord"`

### Implementation for User Story 4

- [x] T018 [P] [US4] Add unit tests for `validate_iav_dataset_record()` in `tests/test_iav_disease_classifier.py::TestValidateIAVDatasetRecord`:
  - Valid record passes validation
  - Missing `sample_id`, `disease_onssa_code`, or `bounding_boxes` raises `ValueError`
  - `severity_index` outside 1–5 raises `ValueError`
  - Bounding box coordinates outside 0.0–1.0 normalized range raises `ValueError`
  - Invalid `crop_type` (e.g. "olive") raises `ValueError`
- [x] T019 [US4] Implement `scripts/ingest_iav_dataset.py` batch CLI tool: accept JSON batch file, validate each record via `validate_iav_dataset_record()`, report per-class counts, emit Phase 2.2b milestone progress (counts vs. 500-sample threshold per disease class)

**Checkpoint**: All user stories functional and independently testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, contract compliance, documentation sync, latency assertion (SC-001), end-to-end quickstart validation, and DEFERRED calibration ECE placeholder (SC-004).

- [x] T020 [P] Update API contracts in `specs/010-iav-disease-classifier/contracts/disease-classifier-contracts.md`: explicitly document two new response fields `calibrated_confidence` (float 0.0–1.0, temperature-scaled via `p^T`) and `fail_closed_active` (bool, True when calibrated_confidence < 0.75); add Phase 2.2a (Gemini Zero-Shot) response example alongside Phase 2.2b (EfficientNet-B4) example; update any reference from `onssa_registry.json` → `onssa_authorized_products.json` *(Resolves U4)*
- [x] T021 [P] Update `specs/010-iav-disease-classifier/quickstart.md`: correct temperature scaling formula from `z/T` → `p^T` (add equivalence note: *approximates `softmax(z/T)` for logit vectors*); add non-target crop test scenario; add latency assertion step *(Resolves I2 + quickstart drift)*
- [x] T022 [P] Add SC-001 latency assertion test in `tests/test_image_prefilter.py`: call `validate_image_quality()` on a valid 400×400px green leaf JPEG, measure wall-clock time, assert `result.latency_ms < 300.0` *(Resolves G1 — SC-001 had no latency task)*
- [x] T023 [P] Add SC-006 end-to-end triage latency smoke test in `tests/unit/test_cropdoctor.py`: call `perform_cropdoctor_triage()` with a valid green leaf image bytes and measure total elapsed time; assert < 3000ms (excluding external Gemini API call — mock Gemini in test) *(Covers new SC-006)*
- [x] T024 *(DEFERRED — Phase 2.2b)* Create calibration ECE evaluation script in `scripts/evaluate_calibration.py`: load held-out Moroccan field validation split (≥ 100 samples per disease class), compute ECE (Expected Calibration Error), assert ECE < 0.05 (corresponding to ±5% accuracy per SC-004). **Activate only when `dataset_count_per_class ≥ 500` for all target classes.** *(Resolves A2)*
- [x] T025 Execute end-to-end quickstart validation test suite `pytest tests/ -v` and confirm 100% pass rate against `specs/010-iav-disease-classifier/quickstart.md`
- [x] T026 Commit all changes with conventional commit: `git add -A && git commit -m "feat(010): post-analyze remediation — rename onssa registry, VisionClassificationResult schema, latency assertion, full disclaimer, p^T formula"`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately. T001 and T002 run in parallel.
- **Foundational (Phase 2)**: Depends on Setup completion — **BLOCKS all user stories**. T003, T004, T005 can run in parallel; T006 depends on T003.
- **User Stories (Phases 3–6)**: Depend on Foundational phase completion. US1 (P1) and US2 (P1) may begin in parallel; US3 (P2) and US4 (P3) follow.
- **Polish (Phase 7)**: Depends on all user story phases complete.

### User Story Dependencies

| Story | Priority | Depends On | Can Parallel With |
|---|---|---|---|
| US1 — Triage pipeline | P1 | Phase 2 | US2 |
| US2 — Quality Gate | P1 | Phase 2 | US1 |
| US3 — Phase 2.2b activation | P2 | Phase 2 | US4 |
| US4 — IAV ingestion | P3 | Phase 2 | US3 |

### Critical Path for Renamed Registry File

> **⚠️** T007 (rename `onssa_registry.json` → `onssa_authorized_products.json`) must complete before T008, T009, and T020 reference the file in contracts. Rename includes updating `app/cropdoctor.py`, `app/config.py`, and all test fixtures that reference the old filename.

### Parallel Opportunities

```bash
# Phase 1 (run together):
T001 — schemas.py field updates
T002 — config.py verification

# Phase 2 (run together):
T003 — VisionClassificationResult model
T004 — compute_foliage_green_ratio fix
T005 — IAVDatasetRecord model
# Then:
T006 — triage engine (depends on T003)

# Phase 3 + Phase 4 (run in parallel after Phase 2):
T007, T008 (US1 implementation) || T012, T013 (US2 quality gate)

# Phase 7 (all parallel):
T020, T021, T022, T023, T024 (all independent files)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2, Priority P1)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T006) — CRITICAL, blocks everything
3. Complete Phase 3: US1 Triage Pipeline (T007–T011)
4. Complete Phase 4: US2 Quality Gate (T012–T014)
5. **STOP and VALIDATE**: `pytest tests/ -v` — confirm 125+ tests pass
6. Demo via WhatsApp sandbox with real leaf photos

### Incremental Delivery

1. Setup + Foundational → schema and config foundation ready
2. US1 (T007–T011) → End-to-end triage with ONSSA RAG working → MVP demo
3. US2 (T012–T014) → Quality gate filtering blurry/non-leaf photos
4. US3 (T015–T017) → Phase 2.2b router and temperature scaling ready (awaiting dataset)
5. US4 (T018–T019) → IAV dataset ingestion and milestone tracking
6. Polish (T020–T026) → Contracts, quickstart, latency tests, commit

### Deferred Work (Phase 2.2b Activation)

T024 (`scripts/evaluate_calibration.py`) is explicitly DEFERRED. Activation condition: automatic when `dataset_count_per_class ≥ 500` verified samples for **all** of: TYLCV, Early Blight, Tuta Absoluta (tomatoes) + HLB, Alternaria Leaf Spot, Red Spider Mite (citrus).

---

## Notes

- `[P]` tasks operate on different files with no cross-task dependencies — safe to run in parallel
- `[Story]` label traces every task back to its user story for independent validation
- T007 (ONSSA file rename) is the highest-risk task — run `grep -r "onssa_registry.json"` post-rename to verify no stale references remain
- Constitution §III disclaimer must appear **verbatim** in every triage response — SC-002 and test assertions validate this
- Temperature scaling formula is **`p ** T`** (not `p ** (1/T)`) — T > 1 reduces confidence, T < 1 amplifies. See `app/cropdoctor.py::apply_temperature_scaling` and `tests/test_iav_disease_classifier.py::TestApplyTemperatureScaling`
