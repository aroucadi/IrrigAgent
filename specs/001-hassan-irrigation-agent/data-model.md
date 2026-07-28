# Data Model & Schema Specification: Hassan Persona & Darija Voice Teaser

**Branch**: `001-hassan-irrigation-agent` | **Date**: 2026-07-28 | **Spec**: [spec.md](spec.md)

## Firestore Collections

### 1. `farm_profiles` Collection
Stores registered farm metadata per WhatsApp phone number.

```json
{
  "user_id": "phone_212600000000",
  "phone_number": "+212600000000",
  "location": {
    "latitude": 30.4278,
    "longitude": -9.5981,
    "region": "Souss-Massa, Morocco"
  },
  "crop_type": "tomatoes",
  "acreage_ha": 8.5,
  "preferred_language": "darija",
  "created_at": "2026-07-28T14:00:00Z",
  "updated_at": "2026-07-28T16:00:00Z"
}
```

---

### 2. `irrigation_recommendations` Collection
Stores daily proactive irrigation advisories and Hassan's responses.

```json
{
  "recommendation_id": "rec_212600000000_20260729",
  "phone_number": "+212600000000",
  "target_date": "2026-07-29",
  "et0_mm": 5.4,
  "recommended_duration_min": 45,
  "status": "APPROVED",
  "data_quality": "FRESH",
  "response_payload": {
    "reply_raw": "1",
    "parsed_modification": null,
    "received_at": "2026-07-28T19:05:12Z"
  },
  "created_at": "2026-07-28T18:45:00Z"
}
```

---

### 3. `disease_triage_requests` Collection
Stores CropDoctor multimodal leaf photo triage interactions.

```json
{
  "request_id": "triage_212600000000_1722180000",
  "phone_number": "+212600000000",
  "image_url": "https://mmg.whatsapp.net/...",
  "identified_pathogen": "Tomato Yellow Leaf Curl Virus (TYLCV)",
  "confidence_score": 0.85,
  "onssa_product_pointer": {
    "category": "Authorized Insecticides (Whitefly Vector Control)",
    "active_ingredients": ["Acetamiprid", "Pyriproxyfen"],
    "verbatim_disclaimer": "This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."
  },
  "created_at": "2026-07-28T15:30:00Z"
}
```

---

## Static ONSSA Lookup Schema

Hardcoded static mapping dictionary in `app/cropdoctor.py` (~10–15 common tomato/citrus pathogens to ONSSA authorized classes).

```python
ONSSA_LOOKUP_TABLE = {
    "Tomato Late Blight (Phytophthora infestans)": {
        "class": "Fungicide - Copper / Metalaxyl",
        "active_ingredients": ["Mancozeb", "Copper Hydroxide"],
        "onssa_reference": "ONSSA Register Class F-04",
    },
    "Tomato Yellow Leaf Curl Virus (TYLCV)": {
        "class": "Insecticide (Vector Whitefly Control)",
        "active_ingredients": ["Acetamiprid", "Pyriproxyfen"],
        "onssa_reference": "ONSSA Register Class I-12",
    },
    "Citrus Red Mite (Panonychus citri)": {
        "class": "Acaricide",
        "active_ingredients": ["Aquinocel", "Spirodiclofen"],
        "onssa_reference": "ONSSA Register Class A-02",
    },
}
```

---

## Voice Teaser Audio Payload Schema

In-memory and background task payload for generating Moroccan Darija voice notes.

```json
{
  "payload_id": "voice_212600000000_1722180500",
  "phone_number": "+212600000000",
  "english_intent": "APPROVED_IRRIGATION_45_MIN",
  "arabic_script_darija": "مزيان، صافي غدا غادي تسقي 45 دقيقة كيفما متفقين.",
  "audio_encoding": "OGG_OPUS",
  "language_code": "ar-MA",
  "staging_file_path": "/tmp/voice_212600000000_1722180500.ogg",
  "whatsapp_media_id": "media_9876543210",
  "latency_ms": 1840,
  "status": "DELIVERED"
}
```
