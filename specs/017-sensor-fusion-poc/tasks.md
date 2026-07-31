# Tasks: Closed-Loop Sensor Fusion Telemetry & Decision Calibration

**Input**: Design documents from `/specs/017-sensor-fusion-poc/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Maps to spec user stories (e.g. US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and feature setup

- [x] T001 Create feature spec directory structure per implementation plan in `specs/017-sensor-fusion-poc/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schema and data access helpers required before user story endpoints and decision math can be implemented

- [x] T002 Add `SensorTelemetryPayload` Pydantic v2 schema in `app/schemas.py`
- [x] T003 Add `update_farm_sensor_state()` and `get_farm_sensor_state()` persistence helpers in `app/firestore_client.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Simulated Soil Sensor Telemetry Ingestion API (Priority: P1) 🎯 MVP

**Goal**: Expose `POST /telemetry/sensor` REST API endpoint to ingest and validate volumetric water content ($\text{VWC}\%$) telemetry.

**Independent Test**: Run `pytest tests/unit/test_schemas.py` and `pytest tests/integration/test_sensor_fusion.py` to verify payload validation, persistence, and HTTP 200/422 response handling.

### Implementation for User Story 1

- [x] T004 [P] [US1] Unit test for telemetry schema validation in `tests/unit/test_schemas.py`
- [x] T005 [US1] Implement `POST /telemetry/sensor` endpoint route in `app/main.py`
- [x] T006 [P] [US1] Integration test for telemetry ingestion route in `tests/integration/test_sensor_fusion.py`

**Checkpoint**: At this point, User Story 1 is fully functional and telemetry can be posted and stored independently.

---

## Phase 4: User Story 2 - Closed-Loop Sensor Fusion Irrigation Recommendation Calibration (Priority: P1)

**Goal**: Calibrate FAO-56 $ET_c$ irrigation recommendations using live soil moisture readings, appending `"📡 Données Capteur Sol"` badges to WhatsApp advisories and falling back gracefully to weather math when telemetry is stale ($> 24\text{h}$).

**Independent Test**: Run `pytest tests/unit/test_decision.py` verifying sensor-based calibration and fallback behavior.

### Implementation for User Story 2

- [x] T007 [P] [US2] Unit tests for decision sensor fusion calibration & fallback in `tests/unit/test_decision.py`
- [x] T008 [US2] Implement `calculate_fused_irrigation_recommendation()` in `app/decision.py`
- [x] T009 [US2] Update WhatsApp daily advisory generator to include sensor badge string in `app/main.py`

**Checkpoint**: User Story 1 and User Story 2 both work independently and together to produce sensor-fused WhatsApp advisories.

---

## Phase 5: User Story 3 - CLI Telemetry Simulator Utility for Live Demos (Priority: P2)

**Goal**: Provide `scripts/simulate_sensor.py` CLI script to fire mock telemetry payloads to local or Cloud Run endpoints in under 15 seconds.

**Independent Test**: Run `python scripts/simulate_sensor.py --farm "+212600000000" --vwc 14.5` and verify API ingestion output.

### Implementation for User Story 3

- [x] T010 [P] [US3] Create CLI telemetry simulator utility script in `scripts/simulate_sensor.py`

**Checkpoint**: All user stories are independently functional and executable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification and documentation updates

- [x] T011 [P] Verify full test suite pass rate (`pytest tests/`) with zero regressions
- [x] T012 [P] Run quickstart validation scenarios in `specs/017-sensor-fusion-poc/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Telemetry API Endpoint
  - User Story 2 (P1): Decision Engine Calibration (can run parallel or sequential to US1)
  - User Story 3 (P2): CLI Telemetry Simulator (depends on US1 API endpoint)
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- T004 [US1] (schema tests) can run in parallel with T007 [US2] (decision tests)
- T010 [US3] (CLI simulator) can be created independently once T002 schema is ready
- T011 and T012 polish tasks can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 & 2)
1. Complete Phase 1 & Phase 2 (Setup & Foundational)
2. Complete Phase 3 (US1: Ingestion API)
3. Complete Phase 4 (US2: Sensor Fusion Calibration)
4. Validate end-to-end telemetry ingestion & WhatsApp advisory flow
