# Implementation Plan: Hassan Persona - Proactive Irrigation Agent & Leaf Photo Triage

**Branch**: `001-hassan-irrigation-agent` | **Date**: 2026-07-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-hassan-irrigation-agent/spec.md`

## Summary

Build a WhatsApp-native AI agent for small/medium Moroccan farm managers (Hassan persona).
- **IrrigAgent (Hero)**: Daily proactive evening advisory (19:00 GMT+1) based on Open-Meteo weather forecast and FAO-56 ET₀ data. Supports one-tap WhatsApp replies (`1` Approve, `2` Skip, `3` Modify with narrow regex parameter parsing). Zero automated valve control (human-in-the-loop only).
- **CropDoctor (Secondary)**: Multimodal leaf photo disease triage powered by Gemini 1.5 Flash. Employs confidence-tiered safety rules and a static ONSSA product lookup table (~10–15 common tomato/citrus pathogens) to eliminate AI product hallucination risk, with a mandatory ONSSA disclaimer appended to every response.
- **Architecture**: Single Python 3.11+ FastAPI service deployed on GCP Cloud Run, utilizing direct Meta WhatsApp Cloud API (v20.0 Sandbox) integrations and Google Cloud Firestore storage. All GCP cloud infrastructure (Cloud Run, Firestore Native, Cloud Scheduler 18:45 Africa/Casablanca trigger, Secret Manager, IAM service accounts) is fully defined and managed via declarative Terraform HCL under `infra/` (`main.tf`, `variables.tf`, `outputs.tf`, `cloud_run.tf`, `secrets.tf`, `scheduler.tf`) per Constitution Principle VII. Continuous Deployment is automated via `.github/workflows/deploy.yml`.

## Technical Context

**Language/Version**: Python 3.11+, Terraform HCL v1.5+  
**Primary Dependencies**: FastAPI (v0.115+), Uvicorn, httpx, google-cloud-firestore, google-genai, pydantic (v2), HashiCorp Terraform Google Provider (`hashicorp/google` v5.0+), GitHub Actions (`actions/checkout@v4`, `google-github-actions/auth@v2`, `hashicorp/setup-terraform@v3`)  
**Storage**: Google Cloud Firestore (Native Mode)  
**Testing**: pytest, httpx AsyncClient test client, `terraform validate` / `terraform plan`  
**Target Platform**: GCP Cloud Run (Serverless Linux Container) provisioned via Terraform IaC & GitHub Actions CI/CD  
**Project Type**: Web Service (API + Webhook + Batch Job) + Infrastructure Module + CI/CD Workflow  
**Performance Goals**: <2s response time for incoming webhooks; <5s for CropDoctor vision triage  
**Constraints**: Meta WhatsApp Cloud API Sandbox tier (max 5 verified recipient numbers); $10k GCP Hackathon credit limits; strict scope cut list (no voice, no payments, no hardware valves, no physical sensors); strict IaC rule (0 manual GCP Console edits)  
**Scale/Scope**: Solo founder execution for StartGate Agri-Food Tech Incubator demo (3 pilot farmers)

## Constitution Check

*GATE: Passed prior to research. Re-verified post-design.*

- **Human-in-the-Loop Only**: ✅ Fully compliant. Zero hardware control; all irrigation recommendations require WhatsApp reply approval.
- **Rule-Based First Logic**: ✅ Fully compliant. Core recommendation decision engine and ET₀ calculations use deterministic rules. LLM used only for CropDoctor vision feature.
- **Mandatory ONSSA Disclaimer**: ✅ Fully compliant. Every CropDoctor response appends verbatim disclaimer; product pointers retrieved via static lookup table only.
- **WhatsApp Sandbox Tier**: ✅ Fully compliant. Restricted to Meta WhatsApp Cloud API sandbox endpoints (max 5 numbers).
- **Cut List Enforcement**: ✅ Fully compliant. Voice processing, billing, hardware automation, and sensors strictly excluded.
- **End-to-End Demoability**: ✅ Fully compliant. Quickstart validation suite covers runnable end-to-end scenarios.
- **Infrastructure as Code (Principle VII)**: ✅ Fully compliant. 100% of GCP resources (Cloud Run, Firestore Native, Cloud Scheduler, Secret Manager, IAM Service Accounts) declared in `infra/` using Terraform HCL (`main.tf`, `variables.tf`, `outputs.tf`, `cloud_run.tf`, `secrets.tf`, `scheduler.tf`); zero manual console clicks.

## Project Structure

### Documentation (this feature)

```text
specs/001-hassan-irrigation-agent/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Technical research & architectural decisions
├── data-model.md        # Firestore collections, static ONSSA lookup schema & Terraform GCP resource definitions
├── quickstart.md        # Runnable end-to-end validation scenarios (app + terraform)
├── contracts/           # Interface contracts
│   ├── webhook-api.md   # Meta WhatsApp Cloud API webhook contract
│   ├── daily-batch-job.md # 18:45 Africa/Casablanca recommendation trigger contract
│   └── infra-contract.md  # Terraform GCP IaC module & CI/CD pipeline input/output contract
├── checklists/
│   └── requirements.md  # Specification quality checklist
└── tasks.md             # Breakdown for /speckit-tasks command
```

### Source Code Layout (repository root)

```text
.github/workflows/
└── deploy.yml           # GitHub Actions CI/CD deployment pipeline (Docker build/push + terraform apply)

infra/                   # Modular Terraform HCL Infrastructure-as-Code Module
├── main.tf              # Provider configuration, required versions & Firestore Native database
├── variables.tf         # Project ID, region, container image, and secret variable declarations
├── outputs.tf           # Provisioned Cloud Run service URL and IAM service account emails
├── cloud_run.tf         # Cloud Run v2 service resource & public webhook IAM invoker binding
├── secrets.tf           # Secret Manager secrets & versions (WHATSAPP_TOKEN, VERIFY_TOKEN, CRON_SECRET)
└── scheduler.tf         # Cloud Scheduler job (18:45 Africa/Casablanca) & IAM service account bindings

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
```

**Structure Decision**: Single project layout (`app/` + `infra/` + `tests/`) optimized for Cloud Run containerization, Terraform IaC provisioning, and rapid solo execution.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | N/A | No constitution violations exist |
