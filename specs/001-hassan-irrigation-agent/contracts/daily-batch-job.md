# Daily Advisory Batch Job Interface Contract

**Branch**: `001-hassan-irrigation-agent` | **Date**: 2026-07-28 | **Spec**: [spec.md](../spec.md)

## Endpoint

`POST /api/v1/jobs/daily-advisory`

Invoked by GCP Cloud Scheduler every evening at **18:45 GMT+1 (Africa/Casablanca)** to initiate next-day irrigation calculation and queue 19:00 WhatsApp dispatches.

**Headers**:
- `Authorization: Bearer <CRON_SECRET_TOKEN>`
- `Content-Type: application/json`

**Request Body**:
```json
{
  "target_date": "2026-07-29",
  "force_run": false
}
```

**Workflow Execution**:
1. Query `farm_profiles` collection for registered farmers.
2. For each farm:
   - Query Open-Meteo API for target date weather forecast & FAO-56 ET₀.
   - Retries up to 3 times with short backoffs on failure.
   - If still failing, fall back to baseline ET₀ and set `data_quality = "ESTIMATED"`.
   - Calculate recommended duration (min).
   - Write recommendation record to `irrigation_recommendations` collection in Firestore.
   - Formulate proactive WhatsApp text message (incorporating "Estimated data" notice if fallback used).
   - Transmit WhatsApp template/text message via Meta WhatsApp Cloud API.
   - If `ENABLE_DARIJA_VOICE_TEASER=true`, trigger non-blocking voice note synthesis.

**Response**:
- Status `200 OK`
```json
{
  "status": "success",
  "total_farms_processed": 3,
  "successful_dispatches": 3,
  "fallback_count": 0,
  "execution_time_ms": 1420
}
```
