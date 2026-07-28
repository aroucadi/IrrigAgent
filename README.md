# IrrigAgent AI

> **WhatsApp-Native AI Decision Support for Smart & Sustainable Irrigation**

IrrigAgent AI is a WhatsApp-native AI agent designed to help small and medium-sized Moroccan farmers make daily, data-driven irrigation decisions without requiring complex dashboard software.

Developed for the **StartGate Agri-Food Tech Incubator** (5th Cohort, UM6P × IAV Hassan II) in alignment with Morocco's **Génération Green 2020–2030** strategy.

---

## 🌾 Core Features

### 💧 IrrigAgent (Hero Feature)
- **Daily Weather & ET₀ Integration**: Automatically ingests daily forecast and evapotranspiration data from Open-Meteo for the farm's location (18:45 Africa/Casablanca batch job with short-backoff retries & yesterday ET₀ fallback).
- **Previous Evening Dispatch (19:00 Africa/Casablanca)**: Sends proactive daily recommendations the night before to match Hassan's evening WhatsApp review habits and allow calm planning before pre-06:00 AM irrigation starts.
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

## 🏗️ Technical Architecture & Infrastructure as Code

```
[ Meta WhatsApp Cloud API ] ◄──Webhook──► [ GCP Cloud Run v2 (FastAPI) ]
                                                    │
                                            ┌───────┴───────┐
                                            ▼               ▼
                                    [ Decision Logic ]  [ Firestore Native DB ]
                                            │
                           ┌────────────────┴────────────────┐
                           ▼                                 ▼
                   [ Open-Meteo ]                    [ Gemini 1.5 Flash ]
                   (Weather / ET₀)                   (Leaf Photo Triage)
```

- **Messaging**: Meta WhatsApp Cloud API (v20.0 Sandbox Mode)
- **Backend**: Python 3.11+, FastAPI web service
- **AI Vision**: Gemini 1.5 Flash via Vertex AI
- **Data & Storage**: Google Cloud Firestore (Native Mode)
- **Infrastructure as Code (IaC)**: Modular Terraform HCL under `infra/` (`main.tf`, `variables.tf`, `outputs.tf`, `cloud_run.tf`, `secrets.tf`, `scheduler.tf` set to **18:45 Africa/Casablanca**)
- **Automated CI/CD**: GitHub Actions deployment workflow ([.github/workflows/deploy.yml](.github/workflows/deploy.yml)) automating Docker build/push to GCP Artifact Registry and non-interactive `terraform apply`

---

## 🏛️ Project Governance & Spec-Driven Development

This project is built following GitHub's [spec-kit](https://github.com/github/spec-kit) spec-driven workflow:

- **Constitution**: [.specify/memory/constitution.md](.specify/memory/constitution.md)
  - **Human-in-the-loop strictly enforced** (No automated valve/hardware control in v1)
  - **Rule-based logic first** before LLM upgrades
  - **Mandatory ONSSA disclaimer** on all CropDoctor responses
  - **Sandbox messaging tier only** (Max 5 test numbers)
  - **Strict cut list** (No voice, no payments, no sensor hardware integration)
  - **Infrastructure as Code (Principle VII)**: 100% of GCP cloud resources provisioned declaratively via Terraform (0 manual GCP Console edits)

### 📁 Active Feature Design Artifacts (`001-hassan-irrigation-agent`)
- **Feature Specification**: [specs/001-hassan-irrigation-agent/spec.md](specs/001-hassan-irrigation-agent/spec.md)
- **Architecture Implementation Plan**: [specs/001-hassan-irrigation-agent/plan.md](specs/001-hassan-irrigation-agent/plan.md)
- **Actionable Task Breakdown (29 Tasks)**: [specs/001-hassan-irrigation-agent/tasks.md](specs/001-hassan-irrigation-agent/tasks.md)
- **Technical Research**: [specs/001-hassan-irrigation-agent/research.md](specs/001-hassan-irrigation-agent/research.md)
- **Data Model & ONSSA Lookup Schema**: [specs/001-hassan-irrigation-agent/data-model.md](specs/001-hassan-irrigation-agent/data-model.md)
- **Interface Contracts**: [specs/001-hassan-irrigation-agent/contracts/](specs/001-hassan-irrigation-agent/contracts/)
- **Runnable Validation Guide**: [specs/001-hassan-irrigation-agent/quickstart.md](specs/001-hassan-irrigation-agent/quickstart.md)

---

## 📋 Getting Started & Local Validation

### Prerequisites
- Python 3.11+
- HashiCorp Terraform 1.5+
- Meta Developer Account (WhatsApp Cloud API App in Sandbox)
- GCP Project with Cloud Run, Firestore, Secret Manager, Cloud Scheduler & Vertex AI enabled

### Verification Commands
```bash
# Run unit & integration test suite
pytest

# Validate Terraform IaC module syntax
terraform -chdir=infra validate

# Dry-run Terraform execution plan
terraform -chdir=infra plan -var="project_id=your-gcp-project-id"
```

---

## 📜 License

Private Repository - Reserved for StartGate Agri-Food Tech Incubator submission.
