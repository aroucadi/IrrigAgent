# Feature Specification: P0 Stabilization — Real Voice Transcription, Terraform Scope Resolution, Spec Status Accuracy

**Feature Branch**: `012-p0-stabilization-batch`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "Create a new feature spec for a P0 stabilization batch — do not modify or duplicate the already-specified Sentinel real-imagery feature (that spec independently covers BUG-002 and should remain its own feature). This spec covers the three remaining P0 items from backlog.md: BUG-001, BUG-003, and BUG-004."

## Clarifications

### Session 2026-07-30

- Q: How should `infra/*.tf` files be handled to resolve IaC scope drift once and for all? → A: Option A (Delete `infra/*.tf` entirely from the active build until explicitly reopened post-selection).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Real Darija voice transcription (Priority: P1)

As Hassan, when I send a WhatsApp voice note, I want the system to actually transcribe what I said, so that the confirmation prompt reflects my real request instead of a fixed default response regardless of what I actually said.

**Why this priority**: Resolves BUG-001. Currently `parse_voice_intent()` returns hardcoded transcript ("Zid 15 dqiqa f l-sqi ghadan") and 0.88 confidence for all real audio, creating a fake facade. Restoring real ASR is essential for trust and safety in the voice interaction path.

**Independent Test**: Can be tested independently by calling `parse_voice_intent()` with different realistic audio inputs (with Vertex AI SDK mocked) and verifying distinct dynamic transcriptions/confidence scores are returned, while preserving existing confidence gating, 60s cap, and confirmation loops.

**Acceptance Scenarios**:

1. **Given** a farmer sends a real WhatsApp voice note requesting a specific irrigation adjustment, **When** transcription confidence is >= 0.80, **Then** the confirmation prompt reflects that specific adjustment rather than a hardcoded default.
2. **Given** the Vertex AI Gemini ASR API call fails (timeout, auth error, or malformed response), **When** voice note processing occurs, **Then** the system degrades to the standard low-confidence fallback menu and writes no pending intent.
3. **Given** two different realistic voice notes with distinct spoken content, **When** both are processed through `parse_voice_intent()`, **Then** the system produces two distinct transcripts (anti-mock regression test passing).

---

### User Story 2 - Terraform/IaC scope resolved explicitly, once (Priority: P2)

As the project maintainer, I want one final, explicit, documented decision on whether `infra/*.tf` files are active or deferred, so this stops silently reappearing as scope creep across specifications.

**Why this priority**: Resolves BUG-003. Infrastructure scope ambiguity has recurred three times across spec passes, creating contradictions between project constitution governance and generated metrics/documentation.

**Independent Test**: Can be tested by verifying that `infra/*.tf` files are deleted from the active build, the project constitution explicitly records the finalized Terraform policy, and no README or report files contain contradictory completion claims (such as "7 IaC Files ✅").

**Acceptance Scenarios**:

1. **Given** Option A is selected for Terraform scope resolution, **When** the stabilization batch is executed, **Then** `infra/*.tf` files are removed from the active build and `memory/constitution.md` is updated to record that IaC scope is deferred post-selection.
2. **Given** existing README or generated report documentation contains claims counting deferred Terraform files as completed metrics, **When** documentation is audited during this batch, **Then** all contradictory statements are aligned with the constitutional rule.

---

### User Story 3 - Spec status metadata accuracy (Priority: P3)

As anyone reading this repository, I want each specification's Status header to accurately reflect its real implementation state, so "Draft" does not coexist with 100% completed tasks, and "Implemented" is not applied to specs with open P0 bugs against them.

**Why this priority**: Resolves BUG-004. Inaccurate spec header status undermines trust in specification metadata and project tracking.

**Independent Test**: Can be tested by inspecting `spec.md` headers across all numbered specs (`specs/001` through `specs/011`) and confirming that only fully verified specs without open backlog bugs are marked `Status: Implemented`.

**Acceptance Scenarios**:

1. **Given** specs 001, 002, 003, 005, 006, and 007 are verified complete with no open P0 backlog items against them, **When** metadata accuracy is updated, **Then** their header status transitions from `Draft` to `Implemented`.
2. **Given** spec 008 (Sentinel canopy heatmaps) and spec 009 (voice STT) have active open bugs tracking them (BUG-002 and BUG-001 respectively), **When** metadata accuracy is updated, **Then** spec 008 remains `Status: Blocked` (until spec 011 merges) and spec 009 remains `Status: Blocked` (until User Story 1 of this spec completes).

---

### Edge Cases

- **ASR Service Outage or Network Timeout**: Vertex AI Gemini API endpoint is unreachable or returns a non-200 status code. The system must catch the exception cleanly, log a warning, and fall back to the standard text interaction menu without writing a pending intent.
- **Garbled or Non-Speech Audio**: Voice audio contains background noise or unparseable audio. Vertex AI ASR returns low confidence (< 0.80). System routes to the standard text fallback menu.
- **Audio Over 60 Seconds**: Input audio exceeds the 60-second limit. System enforces existing duration cap check before initiating ASR.
- **Documentation Contradictions**: Future reports generated from automated scripts scanning `infra/*.tf`. Standard metrics reporting MUST check constitution status before declaring IaC completeness.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST replace hardcoded transcript and confidence values in `parse_voice_intent()` with an active Gemini 1.5 Flash Audio ASR call using the Vertex AI SDK per `specs/009-voice-darija-stt-safety/research.md`.
- **FR-002**: System MUST preserve the existing `parse_voice_intent()` function signature and return tuple `(confidence_score, transcribed_text, parsed_action)`.
- **FR-003**: The Gemini ASR prompt MUST constrain intent extraction strictly to the existing data model actions (`MODIFY_IRRIGATION`, `INCREASE_IRRIGATION`, `DECREASE_IRRIGATION`, `SKIP_IRRIGATION`) plus numeric adjustments, refusing open-ended extraction.
- **FR-004**: Any real ASR API error (timeout, authentication failure, malformed payload) MUST degrade to the existing low-confidence fallback path (standard text menu, no pending intent persisted).
- **FR-005**: `parse_voice_intent()` MUST NOT return hardcoded responses for any input other than explicitly preserved test fixture byte strings (`b"fake_low_confidence"`, `b"garbled"`).
- **FR-006**: System MUST resolve IaC scope explicitly by deleting `infra/*.tf` files entirely from the active build until explicitly reopened post-selection, eliminating ambiguity and automated report false-positives.
- **FR-007**: System MUST update `.specify/memory/constitution.md` to permanently record the chosen Terraform scope decision.
- **FR-008**: System MUST correct all README and generated project reports so that deferred/inert Terraform files are not counted as positive completion metrics.
- **FR-009**: System MUST update spec header statuses to `Status: Implemented` for specs 001, 002, 003, 005, 006, and 007 in their respective `spec.md` files.
- **FR-010**: System MUST maintain `Status: Blocked` header status for spec 008 (pending spec 011 real-imagery fix) and spec 009 (pending completion of User Story 1 in this spec).
- **FR-011**: System MUST preserve existing status for spec 004 (already verified accurate).
- **FR-012**: System MUST add an anti-mock regression unit test in `tests/unit/test_voice_darija_stt.py` verifying that two distinct realistic audio inputs produce distinct transcripts/confidence scores when the Vertex AI SDK is mocked.

### Key Entities *(include if feature involves data)*

- **VoiceIntentResult**: Tuple containing `(confidence_score: float, transcribed_text: str, parsed_action: dict)` returned by `parse_voice_intent()`.
- **SpecMetadataHeader**: The top-level frontmatter/header lines of `specs/NNN-*/spec.md` containing `Status: Draft | Implemented | Blocked`.
- **ConstitutionTerraformPolicy**: Governance clause in `memory/constitution.md` defining the active vs. inert status of `infra/*.tf` files.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `parse_voice_intent()` executes live Gemini 1.5 Flash Audio ASR via Vertex AI SDK; anti-mock regression test in `tests/unit/test_voice_darija_stt.py` passes.
- **SC-002**: A single explicit decision deleting `infra/*.tf` files from the active build is ratified in `memory/constitution.md`, and 100% of README and generated report statements match this policy without contradiction.
- **SC-003**: 100% of spec header statuses in `specs/` accurately match implementation state — zero specs are marked `Implemented` while an open P0 bug against them remains in `backlog.md`.
- **SC-004**: Full existing test suite (`pytest tests/`) passes with 100% success rate and zero regressions.

## Assumptions

- **Vertex AI SDK Availability**: Google Cloud Vertex AI SDK (`google-generativeai` or `google-cloud-aiplatform`) credentials/environment are configured for Gemini 1.5 Flash audio inference.
- **Fixture Byte String Preservation**: Test fixture byte strings (`b"fake_low_confidence"`, `b"garbled"`) remain reserved for deterministic unit testing of low-confidence fallbacks.
- **Non-Goal Boundaries**: Sentinel real-imagery (spec 011 / BUG-002), CropDoctor logic, Open-Meteo weather/ET₀ rules, and IAV disease dataset sync (spec 010) remain strictly out of scope for this stabilization batch.
