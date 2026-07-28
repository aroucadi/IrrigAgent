# Implementation Plan: Hassan Persona - Proactive Irrigation Agent & Leaf Photo Triage

**Branch**: `001-hassan-irrigation-agent` | **Date**: 2026-07-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-hassan-irrigation-agent/spec.md`

## Summary

Build a WhatsApp-native AI agent for small/medium Moroccan farm managers (Hassan persona).
- **IrrigAgent (Hero)**: Daily proactive evening advisory (19:00 GMT+1 / Africa/Casablanca) based on Open-Meteo weather forecast and FAO-56 ET₀ data. Supports one-tap WhatsApp replies (`1` Approve, `2` Skip, `3` Modify with narrow regex parameter parsing). Zero automated valve control (human-in-the-loop only).
- **CropDoctor (Secondary)**: Multimodal leaf photo disease triage powered by Gemini 1.5 Flash. Employs confidence-tiered safety rules and a static ONSSA product lookup table (~10–15 common tomato/citrus pathogens) to eliminate AI product hallucination risk, with a mandatory ONSSA disclaimer appended to every response.
- **Architecture**: Single Python 3.11+ FastAPI service deployed on GCP Cloud Run using `gcloud run deploy` CLI commands per PRD Section 15.11, utilizing direct Meta WhatsApp Cloud API (v20.0 Sandbox) integrations and Google Cloud Firestore storage. Post-pilot Terraform IaC migration is scheduled under Milestone M6.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI (v0.115+), Uvicorn, httpx, google-cloud-firestore, google-genai, pydantic (v2)  
**Storage**: Google Cloud Firestore (Native Mode)  
**Testing**: pytest, httpx AsyncClient test client  
**Target Platform**: GCP Cloud Run (Serverless Linux Container deployed via `gcloud run deploy`)  
**Project Type**: Web Service (API + Webhook + Batch Job)  
**Performance Goals**: <2s response time for incoming webhooks; <5s for CropDoctor vision triage  
**Constraints**: Meta WhatsApp Cloud API Sandbox tier (max 5 verified recipient numbers); $10k GCP Hackathon credit limits; strict scope cut list (no voice, no payments, no hardware valves, no physical sensors)  
**Scale/Scope**: Solo founder execution for StartGate Agri-Food Tech Incubator demo (3 pilot farmers)

## Constitution Check

*GATE: Passed prior to research. Re-verified post-design.*

- **Human-in-the-Loop Only**: ✅ Fully compliant. Zero hardware control; all irrigation recommendations require WhatsApp reply approval.
- **Rule-Based First Logic**: ✅ Fully compliant. Core recommendation decision engine and ET₀ calculations use deterministic rules. LLM used only for CropDoctor vision feature.
- **Mandatory ONSSA Disclaimer**: ✅ Fully compliant. Every CropDoctor response appends verbatim disclaimer; product pointers retrieved via static lookup table only.
- **WhatsApp Sandbox Tier**: ✅ Fully compliant. Restricted to Meta WhatsApp Cloud API sandbox endpoints (max 5 numbers).
- **Cut List Enforcement**: ✅ Fully compliant. Voice processing, billing, hardware automation, and sensors strictly excluded.
- **End-to-End Demoability**: ✅ Fully compliant. Quickstart validation suite covers runnable end-to-end scenarios.

## Project Structure

### Documentation (this feature)

```text
specs/001-hassan-irrigation-agent/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Technical research & architectural decisions
├── data-model.md        # Firestore collections & static ONSSA lookup schema
├── quickstart.md        # Runnable end-to-end validation scenarios (app + gcloud CLI deploy)
├── contracts/           # Interface contracts
│   ├── webhook-api.md   # Meta WhatsApp Cloud API webhook contract
│   └── daily-batch-job.md # 18:45 Africa/Casablanca recommendation trigger contract
├── checklists/
│   └── requirements.md  # Specification quality checklist
└── tasks.md             # Breakdown for /speckit-tasks command
```

### Source Code Layout (repository root)

```text
app/
├── __init__.py
├── main.py              # FastAPI application, webhook endpoints, batch trigger
├── config.py            # Environment variable loading & validation
├── whatsapp.py          # Meta Cloud API Graph API helper functions (send, download media)
├── weather.py           # Open-Meteo API client with short backoff retries & ET0 math
├── decision.py          # Deterministic irrigation rule-based decision logic
├── regex_parser.py      # Narrow regex parser for Option 3 ("Modify") replies
├── cropdoctor.py        # Gemini 1.5 Flash vision client & static ONSSA lookup engine
└── firestore_client.py  # Firestore DB helper methods (profiles, recommendations, triage)

tests/
├── unit/
│   ├── test_decision.py
│   ├── test_regex_parser.py
│   └── test_cropdoctor.py
└── integration/
    └── test_webhook.py

Dockerfile               # Container definition for Cloud Run deployment
requirements.txt         # Application dependencies
```

**Structure Decision**: Single project layout (`app/` + `tests/` + `Dockerfile`) optimized for FastAPI web service execution, rapid Cloud Run CLI deployment (`gcloud run deploy`), and end-to-end WhatsApp/CropDoctor validation.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | N/A | No constitution violations exist |
