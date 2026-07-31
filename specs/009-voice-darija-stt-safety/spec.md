# Feature Specification: Voice-to-Intent Darija STT Safety Policy & Confirmation Prompts

**Feature Branch**: `009-voice-darija-stt-safety`

**Created**: 2026-07-29

**Status**: Implemented

**Input**: User description: "Feature 2: Section 3.2 — Voice-to-Intent Darija STT (Tier 1 Safety Policy & Confirmation Prompts)"

## Clarifications

### Session 2026-07-29

- Q: What format should be used for the 2-step confirmation prompt? → A: Primary WhatsApp text confirmation by default, with an optional Darija TTS voice note attachment when `ENABLE_DARIJA_VOICE_TEASER=true`.
- Q: How are non-numeric text replies handled while awaiting confirmation? → A: Keep pending intent active and send a reminder prompt offering `1` (Confirm), `2` (Cancel), or `3` (Discard & open main menu).
- Q: What is the maximum acceptable audio duration for voice notes? → A: 60-second maximum limit; audio exceeding 60 seconds triggers a fallback prompt asking for a shorter voice note or text.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Voice Note Intent Extraction with High Confidence (Priority: P1)

A farm manager sends a Moroccan Darija voice note via WhatsApp requesting an irrigation adjustment (e.g. "Zid 15 minutes f l'arrosage stp"). Speech transcription yields a confidence score of 0.80 or higher. The system saves the extracted intent as a temporary pending draft (expiring in 15 minutes) and emits a 2-step confirmation prompt back to the farmer via WhatsApp (e.g. "I heard: Increase irrigation by +15 min tomorrow. Reply 1 to CONFIRM or 2 to CANCEL."). No irrigation state modification occurs until explicit confirmation is received.

**Why this priority**: Implements the Tier 1 Safety Policy (Zero Direct Execution), preventing misheard speech from triggering crop-damaging schedule modifications without human validation.

**Independent Test**: Send a voice note with simulated transcription confidence >= 0.80. Verify that a pending intent document is stored in the database, a WhatsApp confirmation prompt is sent to the sender, and no hardware command or schedule state change occurs until option 1 is sent.

**Acceptance Scenarios**:

1. **Given** a farmer sends an audio voice note, **When** speech transcription produces confidence >= 0.80, **Then** a pending intent with a 15-minute expiration timer is saved in the database, and a WhatsApp confirmation prompt detailing the action is delivered with numeric reply options (1 to Confirm, 2 to Cancel).
2. **Given** a high-confidence pending intent is awaiting response, **When** the farmer replies '1' via WhatsApp, **Then** the pending intent is marked as confirmed and the requested irrigation adjustment is committed.
3. **Given** a high-confidence pending intent is awaiting response, **When** the farmer replies '2' via WhatsApp, **Then** the pending intent is canceled and no irrigation schedule modification occurs.

---

### User Story 2 - Low Confidence or Unparseable Voice Fallback (Priority: P2)

A farm manager sends a voice note recorded in a noisy field environment or using heavy regional dialect (Souss, Gharb, Oriental), resulting in a transcription confidence score below 0.80 or an unparseable audio file. The system refrains from guessing intent or creating pending database records, and instead degrades gracefully by sending a standard text menu prompt to the farmer.

**Why this priority**: Eliminates fatal failure modes where poor speech recognition misinterprets requests (e.g., mistaking "keep same time" for "cut water").

**Independent Test**: Send a voice note with transcription confidence < 0.80 or garbled audio. Verify that no pending intent document is created and the system immediately responds with the standard text menu ("I couldn't hear clearly. Please reply: 1 - Approve (+15 min), 2 - Skip today, 3 - Modify").

**Acceptance Scenarios**:

1. **Given** a farmer sends a voice note, **When** speech transcription confidence is < 0.80 or text cannot be parsed into an action, **Then** no pending intent record is created, and the farmer receives a clear fallback text menu.
2. **Given** the fallback menu is received, **When** the farmer selects a numeric option (1, 2, or 3), **Then** the system executes the corresponding standard text menu workflow.

---

### User Story 3 - Pending Intent Expiration Lifecycle (Priority: P3)

A pending intent created from a high-confidence voice note remains unconfirmed by the farmer for longer than 15 minutes. The system automatically marks the pending intent as expired and ignores any late confirmation responses.

**Why this priority**: Prevents obsolete voice intent proposals from executing unexpectedly hours or days later.

**Independent Test**: Create a pending intent document with a timestamp older than 15 minutes. Send reply '1' via WhatsApp. Verify the system rejects the late confirmation, marks the status as expired, and notifies the user that the proposal has expired.

**Acceptance Scenarios**:

1. **Given** a pending intent awaiting confirmation, **When** 15 minutes elapse without farmer response, **Then** the pending intent status changes to expired.
2. **Given** an expired pending intent, **When** the farmer sends reply '1' or '2', **Then** the system informs the farmer that the intent has expired and requires a new request.

---

### Edge Cases

- What happens when a farmer sends a new voice note while a previous intent is still pending confirmation? (The previous pending intent is superseded/canceled, and the new intent replaces it).
- How does the system handle mixed language audio containing French and Darija code-switching? (Transcription handles code-switching terms; if confidence is >= 0.80, intent is extracted; otherwise it falls back to text menu).
- What happens if audio media download fails due to network or Meta API errors? (The system sends a user-friendly error message requesting a re-send or text input).
- What happens if the farmer sends an invalid text reply (e.g. "maybe") to a confirmation prompt? (The system keeps the pending intent active and prompts the farmer with options: '1' to Confirm, '2' to Cancel, or '3' to Discard & open main menu).
- What happens if a voice note exceeds 60 seconds in duration? (The system rejects the audio before Speech-to-Text transcription and prompts the farmer to send a shorter voice note under 60 seconds or a text message).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST process all incoming WhatsApp audio voice notes strictly as draft intent proposals and NEVER trigger direct irrigation state modifications upon Speech-to-Text transcription.
- **FR-002**: System MUST evaluate speech transcription confidence scores against a Tier 1 safety threshold of 0.80.
- **FR-003**: System MUST create a temporary pending intent record with a 15-minute Time-To-Live (TTL) when transcription confidence is >= 0.80.
- **FR-004**: System MUST emit a 2-step confirmation prompt via WhatsApp (text by default, with optional TTS audio attachment when `ENABLE_DARIJA_VOICE_TEASER=true`) summarizing the parsed intent and requiring explicit numeric confirmation ('1' to Confirm, '2' to Cancel) before committing any irrigation changes.
- **FR-005**: System MUST degrade gracefully to a standard fallback text menu without saving pending intents or executing actions when transcription confidence is < 0.80 or audio is unparseable.
- **FR-006**: System MUST reject confirmation attempts for pending intents older than 15 minutes and mark their status as expired.
- **FR-007**: System MUST record pending intent data including unique intent ID, phone reference, raw transcript text, extracted action parameters, confidence score, status, creation timestamp, and 15-minute expiration timestamp.
- **FR-008**: System MUST enforce a maximum audio duration threshold of 60 seconds for incoming voice notes, rejecting longer recordings prior to Speech-to-Text transcription with a user notification.

### Key Entities

- **Pending Intent**: Represents an unconfirmed irrigation modification proposal extracted from a speech input. Attributes include intent ID, farmer phone identifier, raw speech transcript, parsed intent parameters (action type, duration delta, scheduled date), confidence score, status (pending, confirmed, canceled, expired), creation timestamp, and expiration timestamp.
- **Voice Confirmation Session**: Represents the active 2-step confirmation state associated with a farmer's phone number, linking incoming WhatsApp reply messages to the active pending intent.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero (0%) direct execution of irrigation state changes directly from voice note inputs without prior human numeric confirmation.
- **SC-002**: 100% of voice notes with transcription confidence >= 0.80 generate a WhatsApp confirmation prompt within 3 seconds of audio processing.
- **SC-003**: 100% of voice notes with transcription confidence < 0.80 or garbled audio route directly to the standard fallback text menu without creating executable intent records.
- **SC-004**: 100% of pending intent proposals unconfirmed after 15 minutes transition to expired status and reject late confirmation attempts.

## Assumptions

- Incoming WhatsApp audio files are delivered in standard supported audio encodings (e.g., .ogg opus).
- Speech recognition services return transcribed text accompanied by a normalized confidence score between 0.0 and 1.0.
- System time synchronization uses standard UTC timestamps for 15-minute TTL calculation.
- Primary farmer communication channel remains Meta WhatsApp Cloud API text/audio messaging.
