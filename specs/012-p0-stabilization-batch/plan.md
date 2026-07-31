# Implementation Plan: P0 Stabilization — Real Voice Transcription, Terraform Scope Resolution, Spec Status Accuracy

**Branch**: `012-p0-stabilization-batch` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/012-p0-stabilization-batch/spec.md)

**Input**: Feature specification from `specs/012-p0-stabilization-batch/spec.md`

## Summary

This P0 stabilization batch eliminates the remaining backlog items that block trust in the codebase prior to further feature work. It implements three independent fixes:
1. **BUG-001 (Real Darija Voice ASR)**: Replaces the hardcoded transcript facade in `app/decision.py`'s `parse_voice_intent()` with an active Gemini 1.5 Flash Audio ASR call via the Vertex AI SDK while preserving existing confidence gating, 60s duration cap, and 2-step confirmation loop. Adds an anti-mock regression test that fails if hardcoded mocks are returned for non-fixture inputs.
2. **BUG-003 (Terraform / IaC Scope Resolution - Option A)**: Deletes `infra/*.tf` files from the active build, updates `.specify/memory/constitution.md` to permanently record that IaC is deferred post-selection with `gcloud run deploy` remaining the sole sanctioned pre-selection deployment path, and cleans up any README/report metrics claiming completed IaC files.
3. **BUG-004 (Spec Status Metadata Accuracy)**: Updates header status from `Draft` to `Implemented` in `spec.md` files for specs 001, 002, 003, 005, 006, and 007. Maintains `Status: Blocked` for spec 008 (pending spec 011 real-imagery fix) and spec 009 (pending completion of User Story 1 of this spec).

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Vertex AI SDK (`google-cloud-aiplatform` / `google-generativeai`), `pytest`, `pytest-asyncio`

**Storage**: GCP Firestore (`pending_intents` collection, using in-memory store in unit tests)

**Testing**: `pytest` (`pytest tests/`)

**Target Platform**: GCP Cloud Run (FastAPI service)

**Project Type**: Web service & spec-driven Python codebase

**Performance Goals**: Fast unit test execution (< 3.0 seconds total), sub-second text interaction webhook response time, ASR inference < 3.0s

**Constraints**:
- Strict adherence to Section VIII (No-Facade Rule & Zero-Broken-Tests Policy) of `.specify/memory/constitution.md`
- Preserve existing `parse_voice_intent()` function signature and return tuple `(confidence_score, transcribed_text, parsed_action)`
- Preserve explicit test fixture byte strings (`b"fake_low_confidence"`, `b"garbled"`) for deterministic fallback unit testing

**Scale/Scope**: 3 targeted bug fixes spanning `app/decision.py`, `infra/`, `.specify/memory/constitution.md`, `specs/00*/spec.md`, and `tests/unit/test_voice_darija_stt.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Section I: Human-in-the-Loop Only**: PASS. Voice transcription feeds into mandatory confirmation loop (`1` Confirm, `2` Cancel, `3` Discard). Zero autonomous hardware execution.
- [x] **Section V: Strict Scope Boundary**: PASS. Deferral of IaC scope via Option A removes HCL files from active build. No cut-list features introduced.
- [x] **Section VIII: No-Facade Rule for External Integrations**: PASS. Real Vertex AI Gemini audio ASR call replaces hardcoded facade in `parse_voice_intent()`. Anti-mock unit test added to enforce dynamic behavior.
- [x] **Section VIII: Zero-Broken-Tests Policy**: PASS. All unit tests must pass with 100% rate before completion.

## Project Structure

### Documentation (this feature)

```text
specs/012-p0-stabilization-batch/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical research & ASR design decisions
├── data-model.md        # Entities, return shapes & metadata specs
├── quickstart.md        # Runnable verification guide
├── contracts/           # API and metadata contract definitions
│   └── voice_asr_api.md # Gemini Audio ASR contract & return shape
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
app/
├── decision.py          # parse_voice_intent(), process_voice_note(), process_pending_intent_reply()
├── config.py            # Vertex AI & GCP config settings
└── main.py              # FastAPI webhook routes

.specify/memory/
└── constitution.md      # Updated IaC governance rule (Option A)

infra/                   # [DELETED] Removed from active build per Option A

specs/
├── 001-hassan-irrigation-agent/spec.md  # Header updated -> Status: Implemented
├── 002-quality-security-gate/spec.md     # Header updated -> Status: Implemented
├── 003-audit-schema-coverage/spec.md     # Header updated -> Status: Implemented
├── 004-fix-critical-bugs-and-gaps/spec.md # Unchanged -> Status: Implemented
├── 005-onssa-registry-sync/spec.md       # Header updated -> Status: Implemented
├── 006-crop-etc-calculation/spec.md      # Header updated -> Status: Implemented
├── 007-image-prefilter-heuristics/spec.md# Header updated -> Status: Implemented
├── 008-sentinel-canopy-heatmaps/spec.md  # Header -> Status: Blocked
├── 009-voice-darija-stt-safety/spec.md   # Header -> Status: Blocked
├── 010-iav-disease-classifier/spec.md    # Header -> Status: Blocked / Gated
└── 011-real-sentinel-ndvi/spec.md        # In progress (real imagery fix)

tests/unit/
└── test_voice_darija_stt.py              # Anti-mock regression test & voice ASR test coverage
```

**Structure Decision**: Single Python project structure with spec metadata updates across `specs/` directories and IaC cleanup in root `infra/`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | Fully compliant with constitution principles. |
