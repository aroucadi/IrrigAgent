# IrrigAgent AI

> **WhatsApp-Native AI Decision Support for Smart & Sustainable Irrigation**

IrrigAgent AI is a WhatsApp-native AI agent designed to help small and medium-sized Moroccan farmers make daily, data-driven irrigation decisions without requiring complex dashboard software.

Developed for the **StartGate Agri-Food Tech Incubator** (5th Cohort, UM6P × IAV Hassan II) in alignment with Morocco's **Génération Green 2020–2030** strategy.

---

## 🌾 Core Features

### 💧 IrrigAgent (Hero Feature)
- **Daily Weather & ET₀ Integration**: Automatically ingests daily forecast and evapotranspiration data from Open-Meteo for the farm's location.
- **Decision Engine**: Calculates daily irrigation adjustments using deterministic rule-based logic (upgradeable to lightweight LLM reasoning).
- **One-Tap WhatsApp Interface**: Proactively sends daily recommendation alerts to farmers via WhatsApp:
  - `1`: Approve adjustment
  - `2`: Skip today
  - `3`: Modify parameters (free text response)

### 🍃 CropDoctor (Secondary Feature)
- **Leaf Photo Triage**: Farmers send a photo of a diseased leaf via WhatsApp.
- **Multimodal AI Diagnosis**: Uses Gemini 1.5 Flash via Vertex AI for first-pass disease triage (French/Darija pointers).
- **Regulatory Safety**: References authorized products listed on the official ONSSA register and carries a mandatory ONSSA advisory disclaimer on every response.

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

- **Messaging**: Meta WhatsApp Cloud API (Sandbox Mode)
- **Backend**: Python 3.11+, FastAPI
- **AI Models**: Gemini 1.5 Flash via Vertex AI
- **Data & Storage**: Google Cloud Firestore
- **Deployment**: GCP Cloud Run (Serverless)

---

## 🏛️ Project Governance & Spec-Driven Development

This project is built following GitHub's [spec-kit](https://github.com/github/spec-kit) spec-driven workflow:

- **Constitution**: [.specify/memory/constitution.md](.specify/memory/constitution.md)
  - **Human-in-the-loop strictly enforced** (No automated valve/hardware control in v1)
  - **Rule-based logic first** before LLM upgrades
  - **Mandatory ONSSA disclaimer** on all CropDoctor responses
  - **Sandbox messaging tier only** (Max 5 test numbers)
  - **Strict cut list** (No voice, no payments, no sensor hardware integration)

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
```

---

## 📜 License

Private Repository - Reserved for StartGate Agri-Food Tech Incubator submission.
