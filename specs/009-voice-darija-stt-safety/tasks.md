# Tasks: Voice-to-Intent Darija STT (Tier 1 Safety Policy & Confirmation Prompts)

**Input**: Design documents from `/specs/009-voice-darija-stt-safety/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/whatsapp_voice_intent.json, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Configure data models and schema definitions for voice intent processing

- [x] T001 Configure `pending_voice_intent` Pydantic models in `app/schemas.py`
- [x] T002 [P] Verify contract schema definitions in `specs/009-voice-darija-stt-safety/contracts/whatsapp_voice_intent.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement core Firestore storage helpers and test harness required by all user stories

**⚠️ CRITICAL**: Must complete before starting User Story tasks

- [x] T003 Implement Firestore `pending_intents` collection CRUD and expiration query helpers in `app/firestore_client.py`
- [x] T004 [P] Initialize unit test fixture harness in `tests/unit/test_voice_darija_stt.py`

**Checkpoint**: Core storage helpers and test harness ready.

---

## Phase 3: User Story 1 - Voice Note Intent Extraction with High Confidence (Priority: P1) 🎯 MVP

**Goal**: Extract Darija voice intent with confidence $\ge 0.80$, store draft pending intent in Firestore, and send a 2-step WhatsApp confirmation prompt requiring farmer validation ('1' to Confirm, '2' to Cancel).

**Independent Test**: Send a simulated voice note with confidence $\ge 0.80$. Verify pending intent is saved in Firestore, confirmation prompt is sent via WhatsApp, and no schedule modification occurs until option '1' is sent.

### Implementation for User Story 1

- [x] T005 [P] [US1] Unit test high-confidence voice note processing and pending intent creation in `tests/unit/test_voice_darija_stt.py`
- [x] T006 [US1] Implement ASR transcription & confidence score evaluation ($\ge 0.80$) in `app/decision.py`
- [x] T007 [US1] Implement 2-step WhatsApp confirmation prompt generator (with optional `ENABLE_DARIJA_VOICE_TEASER` TTS check) in `app/whatsapp.py`
- [x] T008 [US1] Implement confirmation reply handler for '1' (Confirm) and '2' (Cancel) in `app/decision.py`
- [x] T009 [US1] Route incoming WhatsApp voice notes to decision engine in `app/main.py`

**Checkpoint**: User Story 1 fully functional and testable independently (MVP ready).

---

## Phase 4: User Story 2 - Low Confidence or Unparseable Voice Fallback (Priority: P2)

**Goal**: Degrade low confidence ($< 0.80$) or unparseable voice notes gracefully to standard text menu without writing DB records.

**Independent Test**: Send a voice note with confidence $< 0.80$ or $>60$ seconds duration. Verify no Firestore record is written and system responds with standard text fallback menu.

### Implementation for User Story 2

- [x] T010 [P] [US2] Unit test low-confidence fallback and audio duration bound logic in `tests/unit/test_voice_darija_stt.py`
- [x] T011 [US2] Implement confidence score $< 0.80$ fallback to static text menu in `app/decision.py`
- [x] T012 [US2] Implement 60-second audio duration cap pre-validation check in `app/whatsapp.py`

**Checkpoint**: User Story 2 complete and verified independently.

---

## Phase 5: User Story 3 - Pending Intent Expiration Lifecycle (Priority: P3)

**Goal**: Enforce 15-minute TTL expiration for pending intents and handle non-numeric reply re-prompting ('1' Confirm, '2' Cancel, '3' Discard).

**Independent Test**: Create a pending intent older than 15 minutes. Send reply '1'. Verify reply is rejected as expired.

### Implementation for User Story 3

- [x] T013 [P] [US3] Unit test 15-minute TTL expiration and non-numeric reply re-prompting in `tests/unit/test_voice_darija_stt.py`
- [x] T014 [US3] Implement 15-minute TTL expiration check and status update to `EXPIRED` in `app/firestore_client.py` and `app/decision.py`
- [x] T015 [US3] Implement non-numeric reply router offering option '3' (Discard & open menu) in `app/whatsapp.py`

**Checkpoint**: All user stories functional and testable independently.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Execute full test suite and validate runnable quickstart scenarios

- [x] T016 [P] Run full unit test suite `pytest tests/unit/test_voice_darija_stt.py`
- [x] T017 Validate end-to-end scenarios per `quickstart.md`

---

## Dependencies & Execution Order

1. **Setup (Phase 1)** $\rightarrow$ Can start immediately.
2. **Foundational (Phase 2)** $\rightarrow$ Depends on Setup. Blocks User Stories.
3. **User Story 1 (Phase 3)** $\rightarrow$ Depends on Foundational. Delivers MVP.
4. **User Story 2 (Phase 4)** $\rightarrow$ Depends on Foundational. Can run parallel to US1.
5. **User Story 3 (Phase 5)** $\rightarrow$ Depends on Foundational. Can run parallel to US1/US2.
6. **Polish (Phase 6)** $\rightarrow$ Depends on US1, US2, US3 completion.

---

## Implementation Strategy

### MVP First (User Story 1)
1. Complete Setup & Foundational phases.
2. Implement User Story 1 (T005 - T009).
3. Validate independent test criteria for US1.
