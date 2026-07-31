# Implementation Plan: Pre-Demo Critical Fixes — Template-Based Daily Advisory, Dependency Fix, Mock-ID Backdoor Closure

**Branch**: `016-pre-demo-critical-fixes` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/016-pre-demo-critical-fixes/spec.md)

**Input**: Feature specification from `specs/016-pre-demo-critical-fixes/spec.md`

## Summary

Pre-demo stabilization batch addressing three critical backlog items:
1. **CRIT-005**: Live verification of WhatsApp 24-hour window restrictions, implementing `send_template_message()` for proactive daily advisories (`irrigagent_daily_advisory`) with 3 embedded Quick Reply buttons (`Approve`, `Skip`, `Modify`), and parsing `button_reply` webhook payloads.
2. **CRIT-006**: Adding `python-multipart>=0.0.12` to `requirements.txt` to resolve FastAPI `UploadFile` boot blocker.
3. **CRIT-007**: Removing `"mock_img_1"` and `"mock_audio_1"` production default fallback strings in `app/main.py`, logging raw missing media ID failures internally, and returning polite farmer-facing retry messages without surfacing raw errors or executing mock data paths.

## Technical Context

**Language/Version**: Python 3.11+ / 3.13  
**Primary Dependencies**: FastAPI 0.115.0, `python-multipart>=0.0.12`, `httpx==0.27.2`, `google-genai>=0.1.0`  
**Storage**: Google Cloud Firestore (Farm profiles, pending intents, triage records, recommendations)  
**Testing**: pytest 8.3.3, `pytest-asyncio`  
**Target Platform**: GCP Cloud Run (Linux container environment)  
**Project Type**: Python Web Service (FastAPI REST API / Meta Webhook)  
**Performance Goals**: < 1.0 second webhook response time for inbound messages  
**Constraints**: Sub-second deterministic execution, zero broken tests, no hardcoded secrets  
**Scale/Scope**: Pre-demo stabilization batch covering 3 critical backlog items (CRIT-005, CRIT-006, CRIT-007)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle I: Human-in-the-Loop Only**: All advisories require WhatsApp user response/confirmation. No hardware actuation.
- [x] **Principle II: Rule-Based First Logic**: Daily advisories and recommendation status updates follow deterministic rule-based evaluation.
- [x] **Principle III: Mandatory ONSSA Regulatory Disclaimer**: CropDoctor triage responses retain verbatim ONSSA disclaimers.
- [x] **Principle IV: WhatsApp Cloud API Sandbox Tier Only**: Uses Meta Graph API sandbox endpoints.
- [x] **Principle V: Strict Scope Boundary & Cut List Enforcement**: No cut-list features introduced. UX-001, UX-002, UX-005 explicitly excluded to separate follow-up specs.
- [x] **Principle VI: End-to-End Demoability**: Full end-to-end demoability on real WhatsApp test numbers.
- [x] **Principle VII: Infrastructure Management & Deployment Path**: No Terraform added; deploys via `gcloud run deploy`.
- [x] **Principle VIII: Quality, Security & Automated Verification Gates**:
  - Zero-Broken-Tests Policy enforced (`pytest`).
  - No secrets in code.
  - **No-Ambiguous-Mock-Fallback Rule (CRIT-007)**: Fallback default strings `"mock_img_1"` / `"mock_audio_1"` in `app/main.py` removed; missing media IDs fail loudly/log internally and return polite farmer guidance.

## Project Structure

### Documentation (this feature)

```text
specs/016-pre-demo-critical-fixes/
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical research & 24h window verification log
├── data-model.md        # Template JSON payload & Quick Reply schemas
├── quickstart.md        # Run & validation commands
├── contracts/           # Meta Graph API template contract
│   └── whatsapp_templates_api.md
└── checklists/
    └── requirements.md  # Spec quality validation checklist
```

### Source Code Layout

```text
app/
├── main.py              # Webhook receiver, mock-ID backdoor fix, daily job template dispatcher
├── whatsapp.py          # send_template_message(), extract_incoming_message() button_reply parsing
├── decision.py          # Recommendation status updates, pending intent routing
├── schemas.py           # DailyAdvisoryJobResponse schema
└── ...

requirements.txt         # Added python-multipart>=0.0.12

tests/
├── unit/
│   ├── test_whatsapp.py # Template payload & button_reply extraction unit tests
│   └── test_decision.py
└── integration/
    ├── test_webhook.py  # Missing media ID, button click postback integration tests
    └── test_daily_batch_multi_farm.py # Template daily advisory job integration tests
```

**Structure Decision**: Single project layout using standard `app/` and `tests/` directories.

## Complexity Tracking

*No constitution violations. Complexity tracking empty.*
