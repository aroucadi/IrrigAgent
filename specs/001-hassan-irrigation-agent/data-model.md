# Data Model Specification: Hassan Persona

**Feature**: Hassan Persona - Proactive Irrigation Agent & Leaf Photo Triage  
**Branch**: `001-hassan-irrigation-agent`  
**Date**: 2026-07-28

---

## Firestore Collections

### 1. `farm_profiles`
Stores farm manager metadata, geographic coordinates, crop profile, and language preferences.

- **Document ID**: `phone_number` (E.164 string format, e.g. `"+212600000000"`)
- **Fields**:
  | Field Name | Type | Description | Validation / Constraints |
  |---|---|---|---|
  | `phone_number` | String | E.164 phone number | Primary identifier, required |
  | `location` | Map | Geo-coordinates | `{ "latitude": Float, "longitude": Float }` |
  | `crop_type` | String | Crop grown on farm | e.g., `"tomatoes"`, `"citrus"` |
  | `acreage_hectares` | Float | Farm size in hectares | Positive number (e.g. `10.5`) |
  | `preferred_language` | String | User preferred language | `"french"` or `"darija"` (Default `"french"`) |
  | `created_at` | Timestamp | Profile creation date | ISO 8601 UTC timestamp |
  | `updated_at` | Timestamp | Last updated date | ISO 8601 UTC timestamp |

---

### 2. `irrigation_recommendations`
Stores daily recommendation logs, weather data snapshots, and user approval choices.

- **Document ID**: `rec_{phone_number}_{YYYY-MM-DD}` (e.g. `rec_+212600000000_2026-07-29`)
- **Fields**:
  | Field Name | Type | Description | Validation / Constraints |
  |---|---|---|---|
  | `recommendation_id` | String | Unique document ID | Required |
  | `phone_number` | String | Reference to `farm_profiles` | E.164 string |
  | `target_date` | String | Recommendation date | Format `YYYY-MM-DD` |
  | `forecast_weather` | Map | Ingested Open-Meteo metrics | `{ "et0": Float, "precipitation_mm": Float, "temp_max_c": Float }` |
  | `data_quality` | String | Data freshness indicator | `"fresh"` (from API) or `"estimated"` (yesterday fallback) |
  | `recommended_action` | String | Core decision output | `"approve_standard"`, `"skip_rain"`, `"adjust_water"` |
  | `recommendation_text` | String | Outgoing WhatsApp message body | Plain text in French or Darija |
  | `status` | String | Recommendation lifecycle state | `"pending"`, `"approved"`, `"skipped"`, `"modified"`, `"failed"` |
  | `user_response_raw` | String | Raw text reply from Hassan | e.g., `"1"`, `"2"`, `"3 +10 min at 05:00"` |
  | `parsed_modification` | Map | Regex-parsed modification payload | `{ "duration_delta_min": Integer, "start_time": String }` |
  | `dispatched_at` | Timestamp | Message dispatch timestamp | ISO 8601 UTC (Target 19:00 GMT+1) |
  | `responded_at` | Timestamp | User reply timestamp | Null until user responds |

---

### 3. `disease_triage_requests`
Stores CropDoctor photo triage history, vision diagnostic outputs, and regulatory disclaimer compliance.

- **Document ID**: `triage_{phone_number}_{timestamp}`
- **Fields**:
  | Field Name | Type | Description | Validation / Constraints |
  |---|---|---|---|
  | `request_id` | String | Unique document ID | Required |
  | `phone_number` | String | Reference to `farm_profiles` | E.164 string |
  | `image_id` | String | Meta WhatsApp image media ID | Meta media ID string |
  | `pathogen_identified` | String | Disease symptom identified | Standard disease key (e.g. `"tuta_absoluta"`, `"leaf_mold"`) |
  | `confidence_score` | Float | Vision model confidence ratio | Range `0.0` to `1.0` |
  | `confidence_tier` | String | Categorized confidence level | `"high"` (>=0.75), `"medium"` (0.50-0.74), `"low"` (<0.50) |
  | `onssa_product_pointer` | String | Matched ONSSA product class | Static table lookup result (null if Low confidence) |
  | `disclaimer_included` | Boolean | Regulatory compliance flag | MUST be `true` |
  | `response_text` | String | Final WhatsApp text reply | Includes diagnosis + disclaimer |
  | `created_at` | Timestamp | Interaction timestamp | ISO 8601 UTC timestamp |

---

## Static ONSSA Product Lookup Dictionary (In-Memory Python Module)

```python
ONSSA_PRODUCT_CATALOG = {
    "tomatoes": {
        "tuta_absoluta": "Bacillus thuringiensis / Spinosad (ONSSA authorized class)",
        "phytophthora_infestans": "Copper hydroxide / Azoxystrobin (ONSSA authorized class)",
        "alternaria_solani": "Difenoconazole / Mancozeb (ONSSA authorized class)",
        "powdery_mildew": "Sulfur / Penconazole (ONSSA authorized class)",
    },
    "citrus": {
        "citrus_canker": "Copper oxychloride (ONSSA authorized class)",
        "citrus_aphids": "Acetamiprid / Pyrethrin (ONSSA authorized class)",
        "spider_mites": "Abamectin / Hexythiazox (ONSSA authorized class)",
    }
}
```

---

## 4. Terraform GCP Infrastructure Resources (`infra/`)

### Module Layout
```text
infra/
├── main.tf          # Core GCP resource definitions (Cloud Run, Firestore, Scheduler, Secret Manager, IAM)
├── variables.tf     # Configurable variables (project_id, region, image_url, secrets)
└── outputs.tf       # Exported resource outputs (service_url, service_accounts)
```

### Managed Resource Specifications (`infra/main.tf`)

| Resource Type | Resource Name | Purpose | Configuration Highlights |
|---|---|---|---|
| `google_cloud_run_v2_service` | `irrigagent_app` | Serverless FastAPI web app container | Image: `gcr.io/{project_id}/irrigagent:latest`, Min 0, Max 5 instances, IAM auth required |
| `google_firestore_database` | `default` | Firestore Native Mode DB instance | Location: `nam5` / `europe-west1`, Type: `FIRESTORE_NATIVE` |
| `google_cloud_scheduler_job` | `daily_advisory_trigger` | 18:45 GMT+1 cron trigger | Schedule: `45 17 * * *` (18:45 GMT+1 in UTC), HTTP `POST /jobs/daily-recommendations`, OIDC token auth |
| `google_secret_manager_secret` | `whatsapp_token`, `verify_token`, `cron_secret` | Secret Manager containers | Automatic replication policy, versioned secrets |
| `google_service_account` | `cloudrun_sa`, `scheduler_sa` | Dedicated IAM identities | Least-privilege service accounts |
| `google_project_iam_member` | `cloudrun_firestore`, `cloudrun_secrets`, `scheduler_invoker` | Minimal role bindings | Roles: `roles/datastore.user`, `roles/secretmanager.secretAccessor`, `roles/run.invoker` |

