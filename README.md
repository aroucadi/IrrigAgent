# IrrigAgent AI

> **WhatsApp-Native AI Decision Support for Smart & Sustainable Irrigation**

IrrigAgent AI is a WhatsApp-native AI agent designed to help small and medium-sized Moroccan farmers make daily, data-driven irrigation decisions without requiring complex dashboard software.

Developed for the **StartGate Agri-Food Tech Incubator** (5th Cohort, UM6P × IAV Hassan II) in alignment with Morocco's **Génération Green 2020–2030** strategy.

---

## 🌾 Core Features

### 💧 IrrigAgent (Hero Feature)
- **Daily Weather & ET₀ Integration**: Automatically ingests daily forecast and evapotranspiration data from Open-Meteo for the farm's location (18:45 GMT+1 batch job with short-backoff retries & yesterday ET₀ fallback).
- **Previous Evening Dispatch (19:00 GMT+1)**: Sends proactive daily recommendations the night before to match Hassan's evening WhatsApp review habits and allow calm planning before pre-06:00 AM irrigation starts.
- **Deterministic Decision Engine**: Calculates daily irrigation adjustments using rule-based thresholds (upgradeable to lightweight LLM reasoning).
- **One-Tap WhatsApp Interface**: Proactively sends alerts with 3 clear options:
  - `1`: Approve adjustment
  - `2`: Skip today
  - `3`: Modify parameters (parsed via narrow regex `[+-]\d+\s*min` / `\d{1,2}:\d{2}` with raw text fallback)
- **Zero-Friction Language Handling**: Dual-language (French + Darija Arabizi) initial greeting with automatic language preference detection (`3`, `7`, `9` Arabizi digit heuristic).

### 🍃 CropDoctor (Secondary Feature)
- **Leaf Photo Triage**: Farmers send a photo of a diseased leaf via WhatsApp.
- **Multimodal Vision Diagnosis**: Uses Gemini 1.5 Flash via Vertex AI for first-pass symptom identification.
- **Confidence-Tiered Safety Rules**:
  - *High / Medium Confidence (>=50%)*: Primary diagnosis + ONSSA product pointer + mandatory disclaimer.
  - *Low Confidence (<50%)*: Cautious observation + request for clearer photo + mandatory disclaimer (**NO chemical or product names provided**).
- **Zero AI Product Hallucination**: Product pointers are retrieved strictly from a static Python lookup table (~10–15 common tomato/citrus pathogens mapped to ONSSA-authorized active ingredients).
- **Mandatory ONSSA Regulatory Disclaimer**: Every response appends:
  > *"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."*

---

## 🏗️ Technical Architecture

```
[ WhatsApp (Meta Cloud API — Sandbox) ] ◄──Webhook──► [ FastAPI on GCP Cloud Run ]
                                                             │
                                                     ┌───────┴───────┐
                                                     ▼               ▼
                                             [ Decision Logic ]  [ Firestore DB ]
                                             (Rule-based logic)  (Farm profiles & logs)
                                                     │
                                   ┌─────────────────┴─────────────────┐
                                   ▼                                   ▼
                            [ Open-Meteo ]                     [ Gemini 1.5 Flash ]
                            (Weather / ET₀)                    (Leaf Photo Triage)
```

- **Messaging**: Meta WhatsApp Cloud API (v20.0 Sandbox Mode)
- **Backend**: Python 3.11+, FastAPI web service
- **AI Vision**: Gemini 1.5 Flash via Vertex AI
- **Data & Storage**: Google Cloud Firestore (Native Mode)
- **Deployment**: GCP Cloud Run (Serverless Container)

---

## 🏛️ Project Governance & Spec-Driven Development

This project is built following GitHub's [spec-kit](https://github.com/github/spec-kit) spec-driven workflow:

- **Constitution**: [.specify/memory/constitution.md](.specify/memory/constitution.md)
  - **Human-in-the-loop strictly enforced** (No automated valve/hardware control in v1)
  - **Rule-based logic first** before LLM upgrades
  - **Mandatory ONSSA disclaimer** on all CropDoctor responses
  - **Sandbox messaging tier only** (Max 5 test numbers)
  - **Strict cut list** (No voice, no payments, no sensor hardware integration)

### 📁 Active Feature Design Artifacts (`001-hassan-irrigation-agent`)
- **Feature Specification**: [specs/001-hassan-irrigation-agent/spec.md](specs/001-hassan-irrigation-agent/spec.md)
- **Architecture Implementation Plan**: [specs/001-hassan-irrigation-agent/plan.md](specs/001-hassan-irrigation-agent/plan.md)
- **Actionable Task Breakdown (23 Tasks)**: [specs/001-hassan-irrigation-agent/tasks.md](specs/001-hassan-irrigation-agent/tasks.md)
- **Technical Research**: [specs/001-hassan-irrigation-agent/research.md](specs/001-hassan-irrigation-agent/research.md)
- **Data Model & ONSSA Lookup Schema**: [specs/001-hassan-irrigation-agent/data-model.md](specs/001-hassan-irrigation-agent/data-model.md)
- **Interface Contracts**: [specs/001-hassan-irrigation-agent/contracts/](specs/001-hassan-irrigation-agent/contracts/)
- **Runnable Validation Guide**: [specs/001-hassan-irrigation-agent/quickstart.md](specs/001-hassan-irrigation-agent/quickstart.md)

---

## 📋 Getting Started

### Prerequisites
- Python 3.11+
- Meta Developer Account (WhatsApp Cloud API App in Sandbox)
- GCP Project with Cloud Run & Vertex AI enabled

### Environment Configuration
Copy `.env.example` to `.env` and fill in the required credentials:
```bash
WHATSAPP_TOKEN=<your_meta_access_token>
WHATSAPP_PHONE_NUMBER_ID=<your_sandbox_phone_number_id>
VERIFY_TOKEN=<your_webhook_verification_token>
GCP_PROJECT_ID=<your_gcp_project_id>
JOB_SECRET_TOKEN=<your_batch_job_secret>
```

---

## 📜 License

Private Repository - Reserved for StartGate Agri-Food Tech Incubator submission.
