# Implementation Plan: Hassan Persona - Proactive Irrigation Agent & Leaf Photo Triage (Darija Voice Teaser Extension)

**Branch**: `001-hassan-irrigation-agent` | **Date**: 2026-07-28 | **Spec**: [spec.md](spec.md)

**Input**: Updated feature specification from `specs/001-hassan-irrigation-agent/spec.md` with Darija Voice Teaser module requirements.

## Summary

Build a WhatsApp-native AI agent for small/medium Moroccan farm managers (Hassan persona).
- **IrrigAgent (Hero)**: Daily proactive evening advisory (19:00 GMT+1 / Africa/Casablanca) based on Open-Meteo weather forecast and FAO-56 ET₀ data. Supports one-tap WhatsApp replies (`1` Approve, `2` Skip, `3` Modify with narrow regex parameter parsing). Recommendation persistence uses direct Firestore collection queries to guarantee stateless reliability on Cloud Run. Zero automated valve control (human-in-the-loop only).
- **CropDoctor (Secondary)**: Multimodal leaf photo disease triage powered by Gemini 1.5 Flash. Employs safe exception handling (`is_unreadable = True`, `confidence_score = 0.0`, `onssa_product_pointer = None`), confidence-tiered safety rules, and a static ONSSA product lookup table (~10–15 common tomato/citrus pathogens) to eliminate AI product hallucination risk, with a mandatory ONSSA disclaimer appended to every response.
- **Darija Voice Teaser Module (Demo Extension)**: Opt-in Moroccan Arabic (`ar-MA`) voice response powered by Google Cloud Text-to-Speech (`google-cloud-texttospeech`) generating native `OGG_OPUS` audio notes. Runs non-blockingly as an asynchronous task under feature flag `ENABLE_DARIJA_VOICE_TEASER=true`, preserving sub-second deterministic text/button execution as the core path. Pre-translates Latin Arabizi to Arabic script prior to TTS synthesis.
- **Architecture**: Single Python 3.11+ FastAPI service deployed on GCP Cloud Run using `gcloud run deploy` CLI commands per PRD Section 15.11, utilizing direct Meta WhatsApp Cloud API (v20.0 Sandbox) integrations and Google Cloud Firestore storage. Post-pilot Terraform IaC migration is scheduled under Milestone M6.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI (v0.115+), Uvicorn, httpx, google-cloud-firestore, google-cloud-texttospeech, google-genai, pydantic (v2)  
**Storage**: Google Cloud Firestore (Native Mode)  
**Testing**: pytest, httpx AsyncClient test client  
**Target Platform**: GCP Cloud Run (Serverless Linux Container deployed via `gcloud run deploy`)  
**Project Type**: Web Service (API + Webhook + Batch Job + Asynchronous Voice Synthesis)  
**Performance Goals**: <1.0s response time for primary incoming text webhooks; <2.5s for asynchronous Darija voice synthesis (SC-007); <5.0s for CropDoctor vision triage  
**Constraints**: Meta WhatsApp Cloud API Sandbox tier (max 5 verified recipient numbers); $10k GCP Hackathon credit limits; strict scope cut list (no hardware valves, no payments, no physical sensors)  
**Scale/Scope**: Solo founder execution for StartGate Agri-Food Tech Incubator demo (3 pilot farmers)

## Constitution Check

*GATE: Passed post-design (Constitution v1.2.0).*

- **Human-in-the-Loop Only**: ✅ Fully compliant. Zero hardware control; all irrigation recommendations require WhatsApp reply approval.
- **Rule-Based First Logic**: ✅ Fully compliant. Core recommendation decision engine and ET₀ calculations use deterministic rules. LLM used only for CropDoctor vision feature and Arabizi pre-translation.
- **Mandatory ONSSA Disclaimer**: ✅ Fully compliant. Every CropDoctor response appends verbatim disclaimer; product pointers retrieved via static lookup table only. Exception/unreadable falls back to low-confidence observation with zero chemical product names.
- **WhatsApp Sandbox Tier**: ✅ Fully compliant. Restricted to Meta WhatsApp Cloud API sandbox endpoints (max 5 numbers).
- **Scope Boundary & Cut List**: ✅ Fully compliant. Hardware automation, payments, and physical sensors strictly excluded. Opt-in Darija Voice Teaser (`ar-MA` OGG OPUS output) explicitly permitted by Constitution v1.2.0 as an asynchronous, non-blocking demo enhancement under feature flag `ENABLE_DARIJA_VOICE_TEASER=true`.
- **End-to-End Demoability**: ✅ Fully compliant. Quickstart validation suite covers runnable end-to-end scenarios (text + voice note).
- **Stateless Cloud Run Storage**: ✅ Fully compliant. Firestore queries replace in-memory lookups for latest recommendation states.

## Project Structure

### Documentation (this feature)

```text
specs/001-hassan-irrigation-agent/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Technical research & architectural decisions
├── data-model.md        # Firestore collections, ONSSA lookup & Voice payload schemas
├── quickstart.md        # Runnable end-to-end validation scenarios (app + gcloud CLI deploy)
├── contracts/           # Interface contracts
│   ├── webhook-api.md   # Meta WhatsApp Cloud API webhook contract
│   ├── daily-batch-job.md # 18:45 Africa/Casablanca recommendation trigger contract
│   └── tts-voice-wrapper.md # GCP TTS ar-MA and WhatsApp audio contract
├── checklists/
│   └── requirements.md  # Specification quality checklist
└── tasks.md             # Breakdown for /speckit-tasks command
```

### Source Code Layout (repository root)

```text
app/
├── __init__.py
├── main.py              # FastAPI application, webhook endpoints, batch trigger, async voice tasks
├── config.py            # Environment variable loading & validation (ENABLE_DARIJA_VOICE_TEASER)
├── whatsapp.py          # Meta Cloud API Graph API helper functions (send text, send_audio_message, upload media)
├── weather.py           # Open-Meteo API client with short backoff retries & ET0 math
├── decision.py          # Deterministic irrigation rule-based decision logic
├── regex_parser.py      # Narrow regex parser for Option 3 ("Modify") replies
├── cropdoctor.py        # Gemini 1.5 Flash vision client, exception fallback & static ONSSA engine
├── tts_voice.py         # Google Cloud TTS ar-MA wrapper & Arabizi pre-translation
└── firestore_client.py  # Firestore DB helper methods (profiles, recommendation queries, triage, Arabizi)

tests/
├── unit/
│   ├── test_decision.py
│   ├── test_regex_parser.py
│   ├── test_cropdoctor.py
│   ├── test_weather.py
│   └── test_tts_voice.py
└── integration/
    └── test_webhook.py

Dockerfile               # Container definition for Cloud Run deployment
requirements.txt         # Application dependencies (including google-cloud-texttospeech)
```

**Structure Decision**: Single project layout (`app/` + `tests/` + `Dockerfile`) optimized for FastAPI web service execution, rapid Cloud Run CLI deployment (`gcloud run deploy`), and end-to-end WhatsApp/CropDoctor/Voice validation.
