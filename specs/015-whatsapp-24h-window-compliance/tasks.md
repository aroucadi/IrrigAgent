# Tasks: WhatsApp 24-hour customer service window compliance for proactive daily advisory dispatch

**Input**: Design documents from `/specs/015-whatsapp-24h-window-compliance/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks included per Constitution Principle VIII (Zero-Broken-Tests policy & automated verification).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Includes exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Infrastructure initialization for WhatsApp 24-hour window compliance testing

- [x] T001 Setup test file structure for 24-hour window compliance in `tests/test_whatsapp_24h_window.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core helpers and persistence functions required before implementing user stories

- [x] T002 [P] Add inbound timestamp storage and lookup functions in `app/firestore_client.py`
- [x] T003 [P] Implement `send_template_message()` for Meta Cloud API template dispatch in `app/whatsapp.py`
- [x] T004 [P] Implement `is_user_in_24h_window()` timestamp evaluation helper in `app/whatsapp.py`

**Checkpoint**: Core foundational helpers ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Live Verification & Window Tracking (Priority: P1) 🎯 MVP

**Goal**: Record inbound message timestamps on webhook receipt and track 24-hour customer service window expiration.

**Independent Test**: Simulate inbound webhook message, calculate elapsed time, verify window state evaluation and live Meta API error 131026 response handling.

### Tests for User Story 1

- [x] T005 [P] [US1] Unit test inbound timestamp updates and window state calculation in `tests/test_whatsapp_24h_window.py`

### Implementation for User Story 1

- [x] T006 [US1] Update webhook message handler in `app/main.py` to record `last_inbound_timestamp` via `app/firestore_client.py` on incoming messages
- [x] T007 [US1] Create standalone live verification script for 24h window state and error 131026 in `scripts/verify_whatsapp_24h_window.py`

**Checkpoint**: User Story 1 fully functional and testable independently.

---

## Phase 4: User Story 2 - Proactive Advisory Dispatch via Approved Templates (Priority: P2)

**Goal**: Format and deliver daily evening advisories using approved Meta WhatsApp Message Templates (`UTILITY` category, `fr` language code) when recipient window is closed.

**Independent Test**: Dispatch an evening advisory to a user whose 24-hour window is closed, verifying outgoing payload structure and positional parameter substitution.

### Tests for User Story 2

- [x] T008 [P] [US2] Unit test Meta template payload construction and positional parameter mapping in `tests/test_whatsapp_24h_window.py`

### Implementation for User Story 2

- [x] T009 [US2] Add template parameter formatting helper (`{{1}}` farm name, `{{2}}` ET₀, `{{3}}` duration) in `app/decision.py`
- [x] T010 [US2] Update advisory dispatch flow in `app/main.py` to route between free-form and template dispatch based on `is_user_in_24h_window()`

**Checkpoint**: User Stories 1 and 2 functional independently.

---

## Phase 5: User Story 3 - Automatic Window Fallback and Error Resilience (Priority: P3)

**Goal**: Catch Meta Cloud API error 131026 on free-form attempt, update local window state to expired, and retry delivery via template dispatch.

**Independent Test**: Simulate Meta API error 131026 response during free-form text transmission, verifying automatic window state update and template retry delivery.

### Tests for User Story 3

- [x] T011 [P] [US3] Integration test for Meta error 131026 detection and automatic template retry in `tests/test_whatsapp_24h_window.py`

### Implementation for User Story 3

- [x] T012 [US3] Implement Meta Graph API error response parser for code 131026 in `app/whatsapp.py`
- [x] T013 [US3] Implement automatic template retry fallback wrapper in `app/whatsapp.py`

**Checkpoint**: All user stories functional and resilient against Meta API window restrictions.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification and quality assurance across all user stories

- [x] T014 [P] Run full automated test suite (`pytest tests/`) ensuring 100% pass rate per Constitution Principle VIII
- [x] T015 [P] Run quickstart validation guide in `specs/015-whatsapp-24h-window-compliance/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories.
- **User Stories (Phases 3-5)**: Depend on Phase 2 completion. Proceed sequentially in priority order (P1 → P2 → P3).
- **Polish (Phase 6)**: Depends on completion of all user story tasks.

### Parallel Opportunities

- `T002`, `T003`, `T004` in Foundational Phase can be implemented in parallel across separate functions/files.
- Unit tests (`T005`, `T008`, `T011`) can be written in parallel with entity/helper updates.
- Verification script (`T007`) can be created independently.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup (Phase 1) & Foundational (Phase 2).
2. Complete User Story 1 (Phase 3).
3. Run `scripts/verify_whatsapp_24h_window.py` to confirm live behavior today.
