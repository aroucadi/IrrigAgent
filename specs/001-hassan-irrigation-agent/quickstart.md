# Quickstart & Runnable Validation Guide

**Branch**: `001-hassan-irrigation-agent` | **Date**: 2026-07-28 | **Spec**: [spec.md](spec.md)

## Prerequisites

- **Python**: Python 3.11 or higher
- **GCP Service Account**: Valid GCP credentials set in `GOOGLE_APPLICATION_CREDENTIALS` with access to Firestore and Cloud Text-to-Speech API (`ar-MA`).
- **Meta WhatsApp Cloud API Sandbox**: Registered test phone number and access token.

---

## Environment Setup

Create or update `.env` in repository root:

```bash
# Core Configuration
PORT=8080
LOG_LEVEL=INFO

# WhatsApp Cloud API Credentials
WHATSAPP_TOKEN="EAAG..."
WHATSAPP_PHONE_ID="123456789"
WHATSAPP_VERIFY_TOKEN="irrigagent_secret_token_2026"

# GCP Credentials & Project
GCP_PROJECT_ID="irrigagent-prod"

# Voice Teaser Feature Flag (Opt-in Demo Mode)
ENABLE_DARIJA_VOICE_TEASER=true
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Unit & Integration Testing

Run full test suite:

```bash
pytest tests/ -v
```

Run specific module tests:

```bash
# Test deterministic decision engine & rainfall fallback
pytest tests/unit/test_decision.py -v

# Test narrow regex parser for Option 3 ("Modify") replies
pytest tests/unit/test_regex_parser.py -v

# Test CropDoctor multimodal vision triage & ONSSA disclaimer enforcement
pytest tests/unit/test_cropdoctor.py -v

# Test Open-Meteo weather retries & baseline fallback
pytest tests/unit/test_weather.py -v

# Test Google TTS ar-MA voice synthesis wrapper
pytest tests/unit/test_tts_voice.py -v
```

---

## Local Webhook Validation

Start FastAPI local server:

```bash
uvicorn app.main:app --reload --port 8080
```

### 1. Test Webhook Verification GET Request

```bash
curl -X GET "http://localhost:8080/webhook?hub.mode=subscribe&hub.verify_token=irrigagent_secret_token_2026&hub.challenge=123456"
```
Expected output: `123456`

### 2. Test Inbound Webhook Option 1 Approval (Sub-Second SLA)

```bash
curl -X POST "http://localhost:8080/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{
      "changes": [{
        "value": {
          "messaging_product": "whatsapp",
          "messages": [{
            "from": "212600000000",
            "id": "wamid.123",
            "timestamp": "1722180000",
            "text": {"body": "1"},
            "type": "text"
          }]
        }
      }]
    }]
  }'
```
Expected response: `{"status":"ok"}` in <1.0 second.
If `ENABLE_DARIJA_VOICE_TEASER=true`, observe background task log for `ar-MA` OGG OPUS voice note synthesis and transmission.

---

## Production Cloud Run Deployment

Deploy backend to GCP Cloud Run per PRD Section 15.11:

```bash
gcloud run deploy irrigagent \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID="irrigagent-prod",WHATSAPP_VERIFY_TOKEN="irrigagent_secret_token_2026",ENABLE_DARIJA_VOICE_TEASER="true"
```
