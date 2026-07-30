# Tasks: Real Sentinel Imagery Discovery and NDVI Computation

**Input**: Design documents from `/specs/011-real-sentinel-ndvi/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Explicit file paths included in all descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Update project dependencies and base schemas

- [x] T001 Update requirements.txt to add `rasterio>=1.3.0` for COG band windowed HTTP Range reads in `requirements.txt`
- [x] T002 [P] Update CanopyHealthReport schema in `app/schemas.py` to add `is_available: bool = True` and `no_data_reason: Optional[str] = None`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core constants and metadata data structures in `app/sentinel.py`

- [x] T003 Define named constants (`MAX_CLOUD_COVER_PERCENT = 20.0`, `SEARCH_RECENCY_DAYS = 30`) and `SentinelSceneMetadata` dataclass in `app/sentinel.py`

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Real Scene Discovery for Farm Parcel (Priority: P1) 🎯 MVP

**Goal**: Query Element84 STAC API for Sentinel-2 scenes with isolated fallback to Copernicus STAC API and select the single most recent scene below the 20% cloud cover threshold.

**Independent Test**: Run `pytest tests/unit/test_sentinel_canopy_heatmap.py -k "test_real_sentinel_discovery"` with mocked STAC responses.

### Implementation for User Story 1

- [x] T004 [P] [US1] Create STAC discovery test fixtures and unit tests for Element84 success and Copernicus fallback in `tests/unit/test_sentinel_canopy_heatmap.py`
- [x] T005 [US1] Implement Element84 STAC search query logic in `discover_sentinel2_scene` in `app/sentinel.py`
- [x] T006 [US1] Implement Copernicus STAC search fallback with isolated per-source try/except blocks and timeouts in `app/sentinel.py`

**Checkpoint**: User Story 1 scene discovery fully functional and testable with mocked STAC APIs

---

## Phase 4: User Story 2 - Real NDVI Computation from Actual Satellite Bands (Priority: P1)

**Goal**: Retrieve Red (B04) and NIR (B08) COG band pixels via `rasterio` windowed reads, apply parcel polygon mask, compute real NDVI, and render canopy health report with true capture date and cloud cover percentage.

**Independent Test**: Run `pytest tests/unit/test_sentinel_canopy_heatmap.py -k "test_sentinel2_bands_retrieval or test_generate_canopy_report"`.

### Implementation for User Story 2

- [x] T007 [P] [US2] Create COG band pixel array test fixtures and band retrieval unit tests in `tests/unit/test_sentinel_canopy_heatmap.py`
- [x] T008 [US2] Implement windowed COG band pixel extraction using `rasterio.open("/vsicurl/" + url)` in `fetch_sentinel2_bands` in `app/sentinel.py`
- [x] T009 [US2] Integrate scene discovery, real band retrieval, polygon NDVI calculation, and actual metadata into `generate_canopy_report` in `app/sentinel.py`
- [x] T010 [P] [US2] Add deterministic test asserting two distinct mock inputs yield non-synthetic, distinct NDVI results (satisfying SC-003) in `tests/unit/test_sentinel_canopy_heatmap.py`

**Checkpoint**: User Story 1 AND User Story 2 complete - real scene discovery and band NDVI pipeline fully operational

---

## Phase 5: User Story 3 - Fail-Closed When No Usable Real Imagery Exists (Priority: P2)

**Goal**: Return an explicit fail-closed response without heatmaps or recommendations when zero clear scenes exist.

**Independent Test**: Run `pytest tests/unit/test_sentinel_canopy_heatmap.py -k "test_real_sentinel_fail_closed"`.

### Implementation for User Story 3

- [x] T011 [P] [US3] Create fail-closed test assertions for zero clear scenes in `tests/unit/test_sentinel_canopy_heatmap.py`
- [x] T012 [US3] Implement fail-closed report builder when discovery returns `None` in `generate_canopy_report` in `app/sentinel.py`

**Checkpoint**: Fail-closed protocol complete and verified

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification and full test suite enforcement

- [x] T013 [P] Verify 100% test pass rate across full suite by executing `pytest tests/`
- [x] T014 Run validation scenarios documented in `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Phase 2
- **User Story 2 (Phase 4)**: Depends on Phase 3 (scene discovery needed before band retrieval)
- **User Story 3 (Phase 5)**: Depends on Phase 3 (discovery result handling)
- **Polish (Phase 6)**: Depends on Phases 1–5

### Parallel Opportunities

- `T001` and `T002` can run in parallel
- `T004` (US1 test fixture) and `T005` (US1 discovery implementation) can start in parallel
- `T007` (US2 test fixture) and `T008` (US2 band retrieval implementation) can start in parallel
- `T010` (SC-003 test) and `T011` (US3 fail-closed test) can run in parallel
- `T013` (Full pytest verification) runs after code completion

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational)
2. Complete Phase 3 (US1 Scene Discovery)
3. Complete Phase 4 (US2 Band NDVI Math & Report)
4. Validate with `pytest tests/unit/test_sentinel_canopy_heatmap.py`
5. MVP complete: Real satellite discovery & real band math replace synthetic generator

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. Add STAC discovery -> Element84 & Copernicus fallback working
3. Add COG band math -> Real reflectance heatmaps working
4. Add fail-closed protocol -> Graceful handling of zero clear imagery
