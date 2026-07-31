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
- **Zero-Friction Language Handling**: Dual-language (French + Darija Arabizi) initial greeting with automatic language preference detection (`3`, `7`, `9` Arabizi digit heuristic, excluding clock-time strings like `07h00` or `19h00`).
- **Profile View & Update**: Natural bilingual commands (`profile`, `update crop tomatoes`, `update area 8 ha`, `update language darija`) strictly validated against `FarmProfile` Pydantic models.

### 🍃 CropDoctor (Secondary Feature)
- **Leaf Photo Triage**: Farmers send a photo of a diseased leaf via WhatsApp.
- **Multimodal Vision Diagnosis**: Uses Gemini 1.5 Flash via Vertex AI for first-pass symptom identification (isolating test mock signatures to explicit fixture tokens).
- **Confidence-Tiered Safety Rules**:
  - *High / Medium Confidence (>=50%)*: Primary diagnosis + ONSSA product pointer + mandatory disclaimer.
  - *Low Confidence (<50%)*: Cautious observation + request for clearer photo + mandatory disclaimer (**NO chemical or product names provided**).
- **Constrained Product Recommendations**: Product recommendations are retrieved from the official ONSSA phytosanitary registry dataset (`data/onssa_registry.json` generated via offline sync tooling), with a static human-verified fallback catalog (`ONSSA_STATIC_CATALOG`) if the dataset file is absent. The model can identify a likely pathogen from a constrained list, but cannot generate, fabricate, or substitute a treatment recommendation for an unsupported crop. (Note: Self-reported model confidence scores are uncalibrated self-reports and serve solely as internal heuristic thresholds).
- **Offline ONSSA Phytosanitary Registry Sync Tool**: Standalone CLI & importable Python module (`scripts/sync_onssa_registry.py`) that extracts Morocco's official ONSSA catalog (~4,700+ entries across ~470 pagination pages) into a structured local dataset, respecting site `robots.txt`, enforcing a 2.5s politeness delay, handling ASP.NET WebForms session postbacks, and supporting dry-runs, exponential retries, and checkpoint progress resilience.

- **Mandatory ONSSA Regulatory Disclaimer**: Every response appends:
  > *"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."*

### 🎙️ Optional Voice Teaser (Demo Enhancement)
- **Darija Audio Synthesis**: Optional voice note output (`ENABLE_DARIJA_VOICE_TEASER=true`) using Google Cloud Text-to-Speech (`ar-MA` Moroccan Arabic) sequenced asynchronously after sub-second text responses.
- **WhatsApp Audio Delivery**: Transmits native OGG/OPUS audio messages via Meta Graph API media upload endpoint.

### 🛡️ Quality & Security Gate Module
- **Automated Pre-Commit Hooks**: 3-stage local verification gate enforcing Secret Scanning (Meta tokens, GCP keys, Firestore credentials), Code Linting & Formatting (`ruff`, `black`), and Fast Unit Tests (`pytest tests/` with 100% pass rate under 3 seconds).
- **Cross-Platform Scripting**: Dual POSIX shell (`.sh`) and Windows PowerShell (`.ps1`) scripts for 1-command developer setup and execution.

---

## 🏗️ Technical Architecture & Infrastructure as Code

```
[ Meta WhatsApp Cloud API ] ◄──Webhook──► [ GCP Cloud Run v2 (FastAPI) ]
                                                    │
                                            ┌───────┴───────┐
                                            ▼               ▼
                                    [ Decision Logic ]  [ Firestore Native DB ]
                                            │
                            ┌───────────────┼───────────────┐
                            ▼               ▼               ▼
                    [ Open-Meteo ]  [ Gemini 1.5 Flash ] [ Cloud TTS ]
                    (Weather / ET₀) (Leaf Photo Triage) (Darija Voice)
                                            │
                                            ▼
                                [ ONSSA Registry Sync ]
                                (Offline Data Extractor)
```

- **Messaging**: Meta WhatsApp Cloud API (v20.0 Sandbox Mode)
- **Backend**: Python 3.11+, FastAPI web service
- **AI Vision**: Gemini 1.5 Flash via Vertex AI
- **Audio Output**: Google Cloud Text-to-Speech (`ar-MA` Moroccan Arabic, OGG/OPUS)
- **Data & Storage**: Google Cloud Firestore (Native Mode) + Local ONSSA Registry Dataset JSON
- **Deployment Path**: GCP Cloud Run CLI (`gcloud run deploy`) per PRD Section 15.11 (Declarative Terraform IaC deferred post-selection per Constitution v1.6.0)

---

## 🏛️ Project Governance & Spec-Driven Development

This project is built following GitHub's [spec-kit](https://github.com/github/spec-kit) spec-driven workflow:

- **Constitution (v1.6.0)**: [.specify/memory/constitution.md](.specify/memory/constitution.md)
  - **Human-in-the-loop strictly enforced** (No automated valve/hardware control in v1)
  - **Rule-based logic first** before LLM upgrades
  - **Mandatory ONSSA disclaimer** on all CropDoctor responses
  - **Sandbox messaging tier only** (Max 5 test numbers)
  - **Voice Scope Note**: Optional TTS voice output permitted behind feature flag `ENABLE_DARIJA_VOICE_TEASER=true` sequenced after core text loop validation; voice ASR input wired in spec 012
  - **Deployment Path (Principle VII)**: All v1 pilot deployments executed via `gcloud run deploy` CLI; Terraform IaC deferred post-selection (Option A)
  - **Quality & Security Gates (Principle VIII)**: Zero-broken-tests policy, deterministic calculation/parsing test coverage, zero secrets in code, No-Facade rule for API calls, and mandatory pre-commit hooks

### 📁 Feature Design Artifacts

#### Feature 001: IrrigAgent Core (`001-hassan-irrigation-agent`)
- **Specification**: [specs/001-hassan-irrigation-agent/spec.md](specs/001-hassan-irrigation-agent/spec.md)
- **Implementation Plan**: [specs/001-hassan-irrigation-agent/plan.md](specs/001-hassan-irrigation-agent/plan.md)
- **Tasks**: [specs/001-hassan-irrigation-agent/tasks.md](specs/001-hassan-irrigation-agent/tasks.md)

#### Feature 002: Quality & Security Gate Module (`002-quality-security-gate`)
- **Specification**: [specs/002-quality-security-gate/spec.md](specs/002-quality-security-gate/spec.md)
- **Implementation Plan**: [specs/002-quality-security-gate/plan.md](specs/002-quality-security-gate/plan.md)
- **Tasks (Completed)**: [specs/002-quality-security-gate/tasks.md](specs/002-quality-security-gate/tasks.md)
- **Quickstart & Verification**: [specs/002-quality-security-gate/quickstart.md](specs/002-quality-security-gate/quickstart.md)

#### Feature 004: Critical Bug Fixes & Spec Alignment (`004-fix-critical-bugs-and-gaps`)
- **Specification**: [specs/004-fix-critical-bugs-and-gaps/spec.md](specs/004-fix-critical-bugs-and-gaps/spec.md)
- **Implementation Plan**: [specs/004-fix-critical-bugs-and-gaps/plan.md](specs/004-fix-critical-bugs-and-gaps/plan.md)
- **Tasks (Completed)**: [specs/004-fix-critical-bugs-and-gaps/tasks.md](specs/004-fix-critical-bugs-and-gaps/tasks.md)
- **Research & Decisions**: [specs/004-fix-critical-bugs-and-gaps/research.md](specs/004-fix-critical-bugs-and-gaps/research.md)
- **Quickstart & Verification**: [specs/004-fix-critical-bugs-and-gaps/quickstart.md](specs/004-fix-critical-bugs-and-gaps/quickstart.md)

#### Feature 005: ONSSA Phytosanitary Registry Sync Tool (`005-onssa-registry-sync`)
- **Specification**: [specs/005-onssa-registry-sync/spec.md](specs/005-onssa-registry-sync/spec.md)
- **Implementation Plan**: [specs/005-onssa-registry-sync/plan.md](specs/005-onssa-registry-sync/plan.md)
- **Tasks (Completed)**: [specs/005-onssa-registry-sync/tasks.md](specs/005-onssa-registry-sync/tasks.md)
- **Research & Decisions**: [specs/005-onssa-registry-sync/research.md](specs/005-onssa-registry-sync/research.md)
- **Quickstart & Verification**: [specs/005-onssa-registry-sync/quickstart.md](specs/005-onssa-registry-sync/quickstart.md)


---

## 📋 Getting Started & Local Validation

### Prerequisites
- Python 3.11+
- Meta Developer Account (WhatsApp Cloud API App in Sandbox)
- GCP Project with Cloud Run, Firestore, Secret Manager, Cloud Scheduler, Vertex AI & Cloud Text-to-Speech enabled

### 1. Developer Git Pre-Commit Hook Setup
Install the automated Quality & Security pre-commit hook with one command:

**POSIX / Linux / macOS / Git Bash**:
```bash
bash scripts/install-hooks.sh
```

**Windows PowerShell**:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/install-hooks.ps1
```

### 2. Verification Commands
```bash
# Run full automated test suite
pytest

# Manually trigger pre-commit gate check
bash scripts/pre-commit.sh
# Or on Windows PowerShell:
powershell -ExecutionPolicy Bypass -File scripts/pre-commit.ps1

# Pilot Deployment via Cloud Run CLI
gcloud run deploy irrigagent --source . --region europe-west1
```


---

## 📜 License

Private Repository - Reserved for StartGate Agri-Food Tech Incubator submission.
