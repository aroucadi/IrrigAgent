# Implementation Plan: Voice-to-Intent Darija STT (Tier 1 Safety Policy & Confirmation Prompts)

**Branch**: `009-voice-darija-stt-safety` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/009-voice-darija-stt-safety/spec.md)

**Input**: Feature specification from `specs/009-voice-darija-stt-safety/spec.md`

## Summary

Implement the Tier 1 Safety Policy & 2-Step Confirmation Loop for Moroccan Darija voice notes received over WhatsApp. Voice note inputs are treated strictly as draft intent proposals and NEVER trigger direct hardware/schedule modifications. Incoming audio notes (max 60 seconds) are transcribed via Gemini 1.5 Flash Audio ASR. Transcriptions with confidence $\ge 0.80$ persist a 15-minute TTL pending intent in Firestore and emit a WhatsApp confirmation prompt requiring explicit numeric confirmation ('1' to Confirm, '2' to Cancel, '3' to Discard). Speech confidence $< 0.80$ or unparseable audio degrades gracefully to the standard fallback text menu.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Google Cloud Firestore, Vertex AI SDK (Gemini 1.5 Flash Audio ASR), Google Cloud Text-to-Speech (`ar-MA`)

**Storage**: GCP Firestore (`pending_intents` collection, document ID `pending_{phone_number}`)

**Testing**: Pytest (`tests/unit/test_voice_darija_stt.py`)

**Target Platform**: GCP Cloud Run (Docker containerized Python web service)

**Project Type**: Web service / REST API (Meta WhatsApp Cloud API webhook handler)

**Performance Goals**: $<3.0$ seconds total turnaround from audio reception to WhatsApp confirmation prompt issuance

**Constraints**:
- Zero Direct Execution Policy (100% human confirmation requirement)
- 60-second maximum voice note audio duration limit
- 15-minute Time-To-Live (TTL) for pending intents
- Voice teaser output gated behind `ENABLE_DARIJA_VOICE_TEASER=true`

**Scale/Scope**: Solo founder pilot tier (WhatsApp Sandbox max 5 recipient numbers)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Human-in-the-Loop Only**: PASS. Raw voice inputs never trigger direct irrigation schedule changes or valve commands. Every parsed intent emits a mandatory 2-step numeric confirmation prompt requiring farmer validation ('1' or '2').
- **Principle II: Rule-Based First Logic**: PASS. Decision logic uses strict deterministic confidence score checks ($\ge 0.80$) and TTL window comparisons. Low confidence degrades directly to the static rule-based text menu.
- **Principle IV: WhatsApp Cloud API Sandbox**: PASS. All messaging interactions use the Meta Cloud API Sandbox tier.
- **Principle V: Scope Boundary & Voice Note**: PASS. Voice input processing enforces strict safety confirmation loop without autonomous control. Voice output (TTS acknowledgment) is gated behind `ENABLE_DARIJA_VOICE_TEASER=true` as permitted by Constitution Principle V Note.
- **Principle VIII: Quality & Security Gates**: PASS. 100% unit test coverage planned for confidence thresholds, 60s duration caps, TTL expiration, and numeric reply choices. Zero hardcoded secrets.

## Project Structure

### Documentation (this feature)

```text
specs/009-voice-darija-stt-safety/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan output)
├── research.md          # Technical decisions & rationale (/speckit-plan output)
├── data-model.md        # Firestore schema & state diagram (/speckit-plan output)
├── quickstart.md        # Runnable verification guide (/speckit-plan output)
└── contracts/
    └── whatsapp_voice_intent.json # Contract JSON Schema (/speckit-plan output)
```

### Source Code (repository root)

```text
app/
├── main.py              # FastAPI webhook endpoint router
├── whatsapp.py          # WhatsApp message parser & response dispatcher
├── decision.py          # State machine logic & pending intent router
├── firestore_client.py   # Firestore pending_intents CRUD & TTL helpers
├── tts_voice.py         # Google Cloud TTS helper (ENABLE_DARIJA_VOICE_TEASER)
└── schemas.py           # Pydantic schemas for pending intent payloads

tests/
└── unit/
    └── test_voice_darija_stt.py # Unit tests for safety policy, TTL & state transitions
```

**Structure Decision**: Single Python web service application layout within `app/` and corresponding unit tests in `tests/unit/`.

## Complexity Tracking

*No violations of Constitution principles or unwarranted architectural complexity.*
