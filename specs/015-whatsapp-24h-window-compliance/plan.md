# Implementation Plan: WhatsApp 24-hour customer service window compliance for proactive daily advisory dispatch

**Branch**: `015-whatsapp-24h-window-compliance` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/015-whatsapp-24h-window-compliance/spec.md)

**Input**: Feature specification from `/specs/015-whatsapp-24h-window-compliance/spec.md`

## Summary

This feature implements compliance for Meta WhatsApp Cloud API's 24-hour customer service window policy. Outbound free-form text messages (`"type": "text"`) are only allowed within 24 hours of a farmer's last inbound message; outside this window, Meta rejects free-form messages with error code `131026`. We track inbound message timestamps in Firestore per user, evaluate window status before dispatching proactive evening advisories, and use pre-approved Meta WhatsApp Message Templates (`"type": "template"`, `UTILITY` category, French `fr` language code) when sending outside the 24-hour window, with automatic error 131026 fallback resilience.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, httpx, Pydantic v2, google-cloud-firestore

**Storage**: GCP Firestore (`farms/{phone_number}` document tracking `last_inbound_timestamp`)

**Testing**: pytest (`tests/test_whatsapp_24h_window.py`)

**Target Platform**: GCP Cloud Run (FastAPI service)

**Project Type**: Python Web Service & Messaging Dispatch Engine

**Performance Goals**: Sub-second window check (<10ms local evaluation); zero delay in webhook processing

**Constraints**: Meta WhatsApp Cloud API Sandbox tier only (max 5 verified recipient numbers); zero hardcoded secrets; 100% test pass rate

**Scale/Scope**: Pilot farm recipients (max 5 verified numbers); daily evening advisory dispatch at 19:00

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Human-in-the-Loop Only (PASS)**: All recommendations transmitted via WhatsApp for human review/approval. No automated hardware control.
- **Principle II: Rule-Based First Logic (PASS)**: Window status evaluated deterministically (`now - last_inbound < 86400s`). No LLM dependency for transport selection.
- **Principle IV: WhatsApp Cloud API Sandbox Tier Only (PASS)**: Strictly uses Meta WhatsApp Cloud API in sandbox mode.
- **Principle V: Strict Scope Boundary & Cut List (PASS)**: No cut list capabilities (no hardware control, payment billing, etc.).
- **Principle VI: End-to-End Demoability (PASS)**: Demoable end-to-end with real WhatsApp test recipient number.
- **Principle VII: Infrastructure Management (PASS)**: Deploys to GCP Cloud Run via CLI (`gcloud run deploy`).
- **Principle VIII: Quality, Security & Automated Verification Gates (PASS)**: 100% test suite pass rate required; zero secrets in code; No-Facade rule satisfied by handling real Meta error 131026 payload structures.

## Project Structure

### Documentation (this feature)

```text
specs/015-whatsapp-24h-window-compliance/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 research findings
├── data-model.md        # Phase 1 data model & state transition definitions
├── quickstart.md        # Phase 1 validation & quickstart guide
└── contracts/           # Phase 1 interface contracts
    └── whatsapp-dispatch-contract.md
```

### Source Code Layout

```text
app/
├── whatsapp.py          # Extended with send_template_message() & error 131026 detection
├── firestore_client.py   # Extended to store and query last_inbound_timestamp
├── main.py              # Inbound webhook updates last_inbound_timestamp on receipt
├── decision.py          # Advisory builder formats template parameters
└── config.py            # Environment configuration

tests/
├── test_whatsapp_24h_window.py # Unit & integration tests for window state and templates
```

**Structure Decision**: Single project layout leveraging existing `app/` modules and `tests/`.

## Complexity Tracking

> **No violations present.** All implementation details conform strictly to IrrigAgent Constitution v1.6.1.
