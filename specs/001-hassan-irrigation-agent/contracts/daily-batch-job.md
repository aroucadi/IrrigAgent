# Interface Contract: Daily Batch Recommendation Endpoint

**Endpoint**: `https://<service-url>/jobs/daily-recommendations`  
**Method**: `POST`  
**Trigger**: GCP Cloud Scheduler (Cron `45 18 * * *` / 18:45 GMT+1 daily)  
**Security**: Bearer token header (`Authorization: Bearer <JOB_SECRET_TOKEN>`)

---

## Behavior & Workflow

1. Queries Firestore `farm_profiles` collection for all registered farms.
2. For each farm:
   - Fetches Open-Meteo weather forecast & ET₀ data for `(latitude, longitude)`.
   - Executes retries (up to 3 attempts with 10s/30s/60s backoff).
   - Evaluates rule-based irrigation recommendation (Approve baseline, Skip rain, Adjust).
   - Saves recommendation document to Firestore (`irrigation_recommendations`).
   - Dispatches proactive WhatsApp message to farm manager via Graph API.
3. Target completion before 19:00 GMT+1.

---

## Response Structure

### Success (200 OK)
```json
{
  "status": "success",
  "dispatched_count": 3,
  "failed_count": 0,
  "data_quality_summary": {
    "fresh": 3,
    "estimated": 0
  },
  "timestamp": "2026-07-28T18:46:12Z"
}
```

### Unauthorized (401 Unauthorized)
Returned if `Authorization` token is invalid or missing.
