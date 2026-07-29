# Implementation Plan: Critical Bug Fixes and Spec Alignment

**Branch**: `004-fix-critical-bugs-and-gaps` | **Date**: 2026-07-29 | **Spec**: [`spec.md`](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/004-fix-critical-bugs-and-gaps/spec.md)

**Input**: Feature specification from `/specs/004-fix-critical-bugs-and-gaps/spec.md`

## Summary

Fix the CropDoctor JPEG signature mock-detection collision, eliminate silent crop catalog fallback to tomatoes for unsupported crops (`olives`, `wheat`), refine Arabizi regex tokenization to ignore clock-time strings (`\dh\d`), align `FarmProfile` Pydantic schema validation with actual profile fields, update `README.md` safety claims, and enforce Constitution v1.4.0 voice output governance rules (gated behind `ENABLE_DARIJA_VOICE_TEASER=true` and sequenced after core text loop validation).

## Technical Context

**Language/Version**: Python 3.13 / FastAPI deployed on GCP Cloud Run  
**Primary Dependencies**: FastAPI, Pydantic, google-genai, google-cloud-texttospeech, requests, pytest  
**Storage**: Firestore (collections: `farm_profiles`, `daily_dispatches`, `interaction_logs`)  
**Testing**: pytest (`pytest tests/`)  
**Target Platform**: GCP Cloud Run / Meta WhatsApp Cloud API Sandbox  
**Project Type**: Web service  
**Performance Goals**: Sub-second text/button WhatsApp responses; asynchronous background TTS execution  
**Constraints**: Zero unhandled exceptions; 100% test pass rate; zero hardcoded credentials  
**Scale/Scope**: 5 verified WhatsApp sandbox recipients  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Human-in-the-Loop Only (NON-NEGOTIABLE)**: PASS. Advisories transmitted via WhatsApp for human review; no automated hardware control.
- **II. Rule-Based First Logic**: PASS. Decision logic remains rule-based; LLMs used only for optional vision triage.
- **III. Mandatory ONSSA Regulatory Disclaimer**: PASS. Disclaimers preserved on CropDoctor responses.
- **IV. WhatsApp Cloud API Sandbox Tier Only**: PASS. Sandbox mode maintained.
- **V. Strict Scope Boundary & Cut List Enforcement (NON-NEGOTIABLE)**: PASS. Voice output (TTS) permitted strictly as optional feature flag `ENABLE_DARIJA_VOICE_TEASER=true` after core loop pilot validation per Constitution v1.4.0. Voice input (transcription/ASR) remains strictly out of scope.
- **VI. End-to-End Demoability**: PASS. End-to-end sandbox testing required for all changes.
- **VII. Infrastructure as Code (NON-NEGOTIABLE)**: PASS. GCP infrastructure managed via Terraform.
- **VIII. Quality, Security & Automated Verification Gates (NON-NEGOTIABLE)**: PASS. Zero broken tests policy and pre-commit checks enforced.

## Project Structure

### Documentation (this feature)

```text
specs/004-fix-critical-bugs-and-gaps/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical research & decisions
├── data-model.md        # Entities & schema models
├── quickstart.md        # Runnable validation guide
├── contracts/           # Interface contracts
│   └── whatsapp-webhook.md
└── checklists/          # Quality checklist
    └── requirements.md
```

### Source Code

```text
app/
├── main.py              # Webhook entrypoint & routing
├── cropdoctor.py        # Gemini AI vision triage module (strict ONSSA catalog lookup)
├── schemas.py           # Pydantic data validation models (FarmProfile)
├── firestore_client.py  # Firestore persistence & Arabizi language detection
├── tts_voice.py         # Google Cloud TTS voice teaser module
├── weather.py           # Open-Meteo weather & ET0 integration
├── decision.py          # Irrigation recommendation engine
└── whatsapp.py          # Meta WhatsApp Cloud API client

tests/
├── integration/         # Integration test suite
│   └── test_webhook.py
└── unit/                # Unit test suite
    ├── test_cropdoctor.py
    ├── test_decision.py
    ├── test_firestore_client.py
    ├── test_regex_parser.py
    ├── test_schemas.py
    ├── test_tts_voice.py
    └── test_weather.py
```

**Structure Decision**: Single Python project layout using `app/` and `tests/`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | *Fully compliant with Constitution v1.4.0* | *N/A* |
