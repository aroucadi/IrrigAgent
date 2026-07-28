# Quickstart Validation Guide: Hassan Persona

**Feature**: Hassan Persona - Proactive Irrigation Agent & Leaf Photo Triage  
**Branch**: `001-hassan-irrigation-agent`  
**Date**: 2026-07-28

---

## 🚀 Environment Setup & Prerequisites

1. **Python Environment**: Python 3.11+
2. **Environment File**: Create `.env` in the root directory:
   ```env
   WHATSAPP_TOKEN=EAAG...
   WHATSAPP_PHONE_NUMBER_ID=1000...
   VERIFY_TOKEN=my_secure_webhook_token_123
   GRAPH_API_VERSION=v20.0
   GCP_PROJECT_ID=irrigagent-dev
   JOB_SECRET_TOKEN=my_batch_job_secret_456
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Application**:
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```

---

## 🧪 Runnable Validation Scenarios

### Scenario 1: Webhook Verification Handshake (GET `/webhook`)
Verify Meta Graph API handshake protocol.

```bash
curl -X GET "http://localhost:8080/webhook?hub.mode=subscribe&hub.verify_token=my_secure_webhook_token_123&hub.challenge=CHALLENGE_ACCEPTED"
```
**Expected Outcome**: Returns HTTP 200 with body `CHALLENGE_ACCEPTED`.

---

### Scenario 2: Simulate Incoming One-Tap Reply (`1` Approve)
Simulate Hassan replying `1` to approve tomorrow's irrigation recommendation.

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
            "from": "+212600000000",
            "id": "wamid_test_1",
            "timestamp": "1774782000",
            "text": { "body": "1" },
            "type": "text"
          }]
        }
      }]
    }]
  }'
```
**Expected Outcome**: Returns `{"status": "ok"}`. Logs state update in Firestore to `"approved"`, and sends WhatsApp confirmation `"Approved. Irrigation adjustment applied for tomorrow."`.

---

### Scenario 3: Trigger Daily Proactive Recommendation Batch (`POST /jobs/daily-recommendations`)
Simulate the 18:45 Africa/Casablanca Cloud Scheduler batch run.

```bash
curl -X POST "http://localhost:8080/jobs/daily-recommendations" \
  -H "Authorization: Bearer my_batch_job_secret_456"
```
**Expected Outcome**: Returns `{"status": "success", "dispatched_count": ...}`. Sends WhatsApp advisory messages for next-day planning to all registered farm profiles.

---

### Scenario 4: CropDoctor Regulatory Compliance Validation
Verify that EVERY CropDoctor triage output includes the mandatory ONSSA disclaimer verbatim.

1. Send leaf photo via WhatsApp sandbox or mock webhook endpoint.
2. Verify reply body contains:
   > *"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."*
3. For low-confidence photos (<50%), verify reply contains NO chemical/product names.

---

### Scenario 5: GCP Cloud Run Deployment (`gcloud CLI`)
Verify application container deployment via Google Cloud SDK CLI per PRD Section 15.11.

```bash
gcloud run deploy irrigagent \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars WHATSAPP_TOKEN=...,WHATSAPP_PHONE_NUMBER_ID=...,VERIFY_TOKEN=...,GCP_PROJECT_ID=...,JOB_SECRET_TOKEN=...
```
**Expected Outcome**: Cloud Run service deploys successfully and provides public HTTPS callback URL for Meta WhatsApp Cloud API webhooks (`https://<service-url>/webhook`). *(Note: Declarative Terraform IaC migration will occur post-selection under Milestone M6).*
