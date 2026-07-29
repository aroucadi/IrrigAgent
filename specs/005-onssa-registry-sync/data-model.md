# Phase 1 Data Model: ONSSA Phytosanitary Registry Sync Tool

**Branch**: `005-onssa-registry-sync` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/005-onssa-registry-sync/spec.md)

## Schema Definitions

### 1. Product Entry Schema (`PhytosanitaryProductEntry`)

Represents a single plant protection product authorized by ONSSA.

```json
{
  "id": "A1234",
  "commercial_name": "COPPER SUPER 50 WP",
  "active_substances": ["Cuivre (sous forme d'oxychloride) 50%"],
  "authorized_crops": ["Tomate", "Agrumes"],
  "targeted_pests": ["Mildiou", "Bactériose"],
  "dosage": "250 g/hL",
  "pre_harvest_interval_days": 15,
  "max_applications": 3,
  "toxicity_class": "Nocif (Xn)",
  "distributor": "AGRO-CHEMICALS MOROCCO SA",
  "homologation_validity_date": "2028-12-31",
  "source_page": 4
}
```

#### Field Attributes & Types

| Field Name | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `string` | Yes | Unique index key or registration/homologation number | `"F02-3-019"` |
| `commercial_name` | `string` | Yes | Commercial product name | `"COPPER SUPER 50 WP"` |
| `active_substances` | `array[string]` | Yes | List of active chemical/biological substances | `["Cuivre 50%"]` |
| `authorized_crops` | `array[string]` | Yes | List of authorized crops | `["Tomate", "Agrumes"]` |
| `targeted_pests` | `array[string]` | Yes | Targeted diseases, fungi, or pests | `["Mildiou"]` |
| `dosage` | `string` | Yes | Application dosage string | `"250 g/hL"` |
| `pre_harvest_interval_days` | `integer` or `null` | Yes | PHI in days (Délai Avant Récolte - DAR) | `15` |
| `max_applications` | `integer` or `null` | No | Maximum permitted treatments per season | `3` |
| `toxicity_class` | `string` | No | Toxicological classification | `"Xn - Nocif"` |
| `distributor` | `string` | No | Authorized distributor / holder | `"AGRI-DEV SARL"` |
| `homologation_validity_date` | `string` | No | Expiration date of homologation (YYYY-MM-DD or raw) | `"2028-12-31"` |
| `source_page` | `integer` | Yes | Result page index from which entry was scraped | `12` |

---

### 2. Committed Dataset Container (`data/onssa_registry.json`)

File structure for persisted sync output.

```json
{
  "_metadata": {
    "extraction_timestamp": "2026-07-29T14:30:00Z",
    "source_url": "https://eservice.onssa.gov.ma/IndPesticide.aspx",
    "mode": "commit",
    "total_entries": 4720,
    "total_pages": 472,
    "user_agent": "IrrigAgent-ONSSA-Sync/1.0 (+https://github.com/aroucadi/IrrigAgent)",
    "failed_rows_count": 2,
    "failed_rows": [
      {
        "page": 104,
        "row_index": 3,
        "raw_text": "MALFORMED_ROW_DATA...",
        "error": "Missing commercial name column"
      }
    ]
  },
  "entries": [
    /* Array of PhytosanitaryProductEntry objects */
  ]
}
```

---

### 3. Execution Progress Checkpoint Schema (`data/onssa_registry.checkpoint.json`)

Intermediate progress state saved to disk after every 5 pages during a commit run.

```json
{
  "extraction_timestamp": "2026-07-29T14:15:00Z",
  "last_completed_page": 120,
  "total_pages_detected": 472,
  "accumulated_entries_count": 1200,
  "failed_rows": [],
  "entries": [
    /* Array of PhytosanitaryProductEntry objects collected so far */
  ]
}
```

---

### 4. CropDoctor Runtime In-Memory Catalog Index (`app/cropdoctor.py`)

Structure produced by `_load_onssa_catalog()` in `app/cropdoctor.py`:

```python
# Indexed dict structure for sub-millisecond lookup
{
  "by_crop_and_pest": {
    ("tomate", "mildiou"): [
      {
        "commercial_name": "COPPER SUPER 50 WP",
        "active_substances": ["Cuivre (oxychloride) 50%"],
        "phi_days": 15,
        "dosage": "250 g/hL",
        "toxicity_class": "Nocif (Xn)"
      }
    ]
  },
  "raw_count": 4720,
  "source": "data/onssa_registry.json" # or "ONSSA_STATIC_CATALOG"
}
```
