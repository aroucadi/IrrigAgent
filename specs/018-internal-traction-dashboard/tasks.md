# Tasks: Internal Engagement & Traction Dashboard

**Input**: Design documents from `specs/018-internal-traction-dashboard/`

**Prerequisites**: [plan.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/018-internal-traction-dashboard/plan.md) (required), [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/018-internal-traction-dashboard/spec.md) (required), [research.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/018-internal-traction-dashboard/research.md), [quickstart.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/018-internal-traction-dashboard/quickstart.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Script entrypoint initialization and basic folder structure setup

- [x] T001 Initialize script entrypoint structure and CLI argument parsing in [scripts/generate_engagement_report.py](file:///d:/rouca/DVM/workPlace/IrrigAgent/scripts/generate_engagement_report.py)
- [x] T002 Configure local output directory creation (`output/`) in [scripts/generate_engagement_report.py](file:///d:/rouca/DVM/workPlace/IrrigAgent/scripts/generate_engagement_report.py)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core read-only Firestore data loading routines required by all reporting views

- [x] T003 Implement read-only data fetching for `farm_profiles`, `irrigation_recommendations`, and `disease_triage_requests` collections in [scripts/generate_engagement_report.py](file:///d:/rouca/DVM/workPlace/IrrigAgent/scripts/generate_engagement_report.py)

**Checkpoint**: Data layer ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Read-only engagement summary from existing Firestore data (Priority: P1) 🎯 MVP

**Goal**: Aggregate registered farms count, 7d/30d active farm counts, advisory response rates, and outcome-feedback distribution from Firestore read-only records, applying small-sample directional data labels when active farms < 5.

**Independent Test**: Run script against mocked Firestore data with known record counts and verify exact metric totals, response rate percentages, and the presence of the `[Early / Directional Data (Sample Size < 5)]` warning tag.

### Implementation for User Story 1

- [x] T004 [US1] Implement aggregation math for registered farms, 7d/30d active farms, response rates, and outcome feedback distribution in [scripts/generate_engagement_report.py](file:///d:/rouca/DVM/workPlace/IrrigAgent/scripts/generate_engagement_report.py)
- [x] T005 [US1] Implement small-sample threshold evaluator (< 5 active farms) and directional warning label injection in [scripts/generate_engagement_report.py](file:///d:/rouca/DVM/workPlace/IrrigAgent/scripts/generate_engagement_report.py)
- [x] T006 [P] [US1] Implement automated unit tests for aggregation math, small-sample warnings, and empty datasets in [tests/test_engagement_report.py](file:///d:/rouca/DVM/workPlace/IrrigAgent/tests/test_engagement_report.py)

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Exportable report for post-meeting leave-behinds (Priority: P2)

**Goal**: Export summary report as static high-resolution PNG image and standalone static HTML page using project visualization dependencies (`matplotlib`).

**Independent Test**: Execute report generation and verify that `output/engagement_report_<YYYYMMDD>.png` and `output/engagement_report_<YYYYMMDD>.html` are cleanly created on local disk.

### Implementation for User Story 2

- [x] T007 [US2] Implement matplotlib chart figure generation (response rate trend line & feedback distribution bars) and PNG export in [scripts/generate_engagement_report.py](file:///d:/rouca/DVM/workPlace/IrrigAgent/scripts/generate_engagement_report.py)
- [x] T008 [US2] Implement static HTML page rendering and file output in [scripts/generate_engagement_report.py](file:///d:/rouca/DVM/workPlace/IrrigAgent/scripts/generate_engagement_report.py)
- [x] T009 [P] [US2] Add automated unit tests for file export generation in [tests/test_engagement_report.py](file:///d:/rouca/DVM/workPlace/IrrigAgent/tests/test_engagement_report.py)

**Checkpoint**: Both User Stories 1 AND 2 are complete and exportable.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Code quality, test suite verification, and validation against quickstart scenarios.

- [x] T010 Run full test suite (`pytest tests/`) to ensure 100% pass rate across the codebase
- [x] T011 Execute [quickstart.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/018-internal-traction-dashboard/quickstart.md) validation script run and verify output artifacts in `output/`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion.
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion.
- **User Story 2 (Phase 4)**: Depends on US1 aggregation logic.
- **Polish (Phase 5)**: Depends on completion of all user story tasks.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1 & 2.
2. Complete Phase 3 (US1).
3. Validate US1 aggregation math & directional labeling via `pytest tests/test_engagement_report.py`.
4. Proceed to Phase 4 (US2) for chart & HTML file export.
