# Tasks: Crop-Specific ETc Calculation

**Input**: Design documents from `/specs/006-crop-etc-calculation/`  
**Prerequisites**: [plan.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/006-crop-etc-calculation/plan.md), [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/006-crop-etc-calculation/spec.md), [research.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/006-crop-etc-calculation/research.md), [data-model.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/006-crop-etc-calculation/data-model.md), [contracts/etc_calculation_api.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/006-crop-etc-calculation/contracts/etc_calculation_api.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3)
- Explicit file paths in all task descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and schemas setup

- [x] T001 Define `FAO56CropEntry` and `ETcCalculationResult` Pydantic schemas in `app/schemas.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core FAO-56 lookup table engine that ALL user stories depend on

- [x] T002 [P] Create static FAO-56 crop coefficient dictionary and lookup functions in `app/fao56.py`

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Accurate Crop Water Demand Calculation (Priority: P1) 🎯 MVP

**Goal**: Transform reference grass evapotranspiration ($\text{ET}_0$) into crop-specific water demand ($\text{ET}_c = \text{ET}_0 \times K_c$) for active growth stage.

**Independent Test**: Supply daily Open-Meteo $\text{ET}_0$ values with crop type and planting date, verifying $\text{ET}_c = \text{ET}_0 \times K_c$.

### Tests for User Story 1

- [x] T003 [P] [US1] Unit tests for FAO-56 calculation engine (`ETc = ET0 * Kc`) in `tests/unit/test_fao56.py`

### Implementation for User Story 1

- [x] T004 [US1] Implement `calculate_crop_etc()` function in `app/fao56.py`
- [x] T005 [US1] Refactor `evaluate_irrigation_recommendation()` in `app/decision.py` to accept `planting_date` and compute `ETc`
- [x] T006 [US1] Update unit tests in `tests/unit/test_decision.py` for $\text{ET}_c$ recommendation output text

**Checkpoint**: User Story 1 functional and independently testable (MVP complete)

---

## Phase 4: User Story 2 - Automated Growth Stage Determination (Priority: P2)

**Goal**: Automatically calculate days elapsed since planting and apply linear stage interpolation ($K_{c,\text{ini}} \rightarrow K_{c,\text{mid}} \rightarrow K_{c,\text{end}}$).

**Independent Test**: Supply various planting dates across Initial, Dev, Mid, Late, and post-harvest periods, verifying correct $K_c$ interpolation.

### Tests for User Story 2

- [x] T007 [P] [US2] Unit tests for piecewise linear stage interpolation and boundary transitions in `tests/unit/test_fao56.py`

### Implementation for User Story 2

- [x] T008 [US2] Implement stage duration progression and linear interpolation math in `app/fao56.py`
- [x] T009 [US2] Support perennial crop stage lookup for adult citrus and olive orchards in `app/fao56.py`

**Checkpoint**: User Stories 1 AND 2 working independently

---

## Phase 5: User Story 3 - Missing Growth Stage Metadata Fallback (Priority: P3)

**Goal**: Fallback gracefully to $K_c = 1.00$ and append a profile update prompt in WhatsApp advisories when planting date metadata is missing.

**Independent Test**: Execute ETc calculation for profile with missing planting date, verifying $K_c = 1.00$ and notice prompt appended.

### Tests for User Story 3

- [x] T010 [P] [US3] Unit tests for missing planting date fallback and notice message formatting in `tests/unit/test_decision.py`

### Implementation for User Story 3

- [x] T011 [US3] Implement fallback $K_c = 1.00$ and notice generation in `app/fao56.py`
- [x] T012 [US3] Integrate fallback notice appending into WhatsApp recommendation message formatting in `app/decision.py`

**Checkpoint**: All user stories functional and independently verified

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: API wiring, documentation, and full test suite verification

- [x] T013 [P] Wire `planting_date` parameter from Firestore farm profile in `app/main.py` recommendation endpoint
- [x] T014 Execute full test suite validation (`pytest tests/ -v`) to enforce Zero-Broken-Tests policy
- [x] T015 Run validation scenarios in `specs/006-crop-etc-calculation/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 completion.
- **User Stories (Phase 3-5)**: Depend on Phase 2 completion.
- **Polish (Phase 6)**: Depends on Phase 3-5 completion.

### User Story Sequence

1. **User Story 1 (P1)**: Core math ($\text{ET}_c = \text{ET}_0 \times K_c$)
2. **User Story 2 (P2)**: Stage interpolation math
3. **User Story 3 (P3)**: Fallback logic & notice prompts

---

## Parallel Execution Opportunities

- `T002` (app/fao56.py lookup data) can run in parallel with schema creation `T001`.
- `T003` (tests/unit/test_fao56.py) and `T007` (interpolation tests) can run in parallel.
- `T010` (fallback decision tests) can run in parallel with `T013` (app/main.py endpoint wiring).

---

## Implementation Strategy (MVP First)

1. Complete Setup (T001) & Foundational (T002).
2. Complete User Story 1 (T003-T006).
3. Validate User Story 1 (`pytest tests/unit/test_fao56.py`).
4. Complete User Story 2 (T007-T009) & User Story 3 (T010-T012).
5. Run full test suite gate (`pytest tests/ -v`).
