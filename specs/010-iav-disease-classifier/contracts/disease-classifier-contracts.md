# Vision Classifier & IAV Ingestion Contracts

## 1. CropDoctor Vision Diagnostic Endpoint / Internal API

### Request
```json
{
  "image_bytes": "<base64_encoded_image_or_binary_payload>",
  "crop_type": "tomatoes",
  "pipeline_mode": "auto"
}
```

### Response (Phase 2.2a Interim Zero-Shot - Gemini 1.5 Flash + ONSSA RAG)
```json
{
  "is_acceptable": true,
  "vision_engine": "gemini-1.5-flash-zeroshot",
  "pathogen_identified": "phytophthora_infestans",
  "symptom_name": "Mildiou de la tomate (Phytophthora infestans)",
  "confidence_score": 0.85,
  "calibrated_confidence": 0.85,
  "confidence_tier": "high",
  "fail_closed_active": false,
  "onssa_product_pointer": "Copper hydroxide / Azoxystrobin (ONSSA authorized class)",
  "disclaimer_included": true,
  "is_unreadable": false,
  "response_text": "🍃 *CropDoctor Diagnosis (High Confidence)*\nIdentified issue: Mildiou de la tomate (Phytophthora infestans)\nSuggested treatment class: Copper hydroxide / Azoxystrobin (ONSSA authorized class)\n\n⚠️ This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."
}
```

### Response (Phase 2.2b - Calibrated EfficientNet-B4, High Confidence ≥ 75%)
```json
{
  "is_acceptable": true,
  "vision_engine": "efficientnet-b4-calibrated",
  "pathogen_identified": "phytophthora_infestans",
  "symptom_name": "Mildiou de la tomate (Phytophthora infestans)",
  "confidence_score": 0.88,
  "calibrated_confidence": 0.853,
  "confidence_tier": "high",
  "fail_closed_active": false,
  "onssa_product_pointer": "Copper hydroxide / Azoxystrobin (ONSSA authorized class)",
  "disclaimer_included": true,
  "is_unreadable": false,
  "response_text": "🍃 *CropDoctor Diagnosis (High Confidence)*\nIdentified issue: Mildiou de la tomate (Phytophthora infestans)\nSuggested treatment class: Copper hydroxide / Azoxystrobin (ONSSA authorized class)\n\n⚠️ This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."
}
```

### Response (Low/Medium Calibrated Confidence - Fail Closed Threshold < 75%)
```json
{
  "is_acceptable": true,
  "vision_engine": "efficientnet-b4-calibrated",
  "pathogen_identified": "phytophthora_infestans",
  "symptom_name": "Mildiou de la tomate (Phytophthora infestans)",
  "confidence_score": 0.72,
  "calibrated_confidence": 0.665,
  "confidence_tier": "medium",
  "fail_closed_active": true,
  "onssa_product_pointer": null,
  "disclaimer_included": true,
  "is_unreadable": false,
  "response_text": "🍃 *CropDoctor Diagnosis (Likely Issue)*\nLikely issue: Mildiou de la tomate (Phytophthora infestans)\nFocus on cultural practices (improving airflow, reducing surface wetness) and consult a local agronomist for authorized treatment options.\n\n⚠️ This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."
}
```

### Response (Failed Quality Gate)
```json
{
  "is_acceptable": false,
  "vision_engine": "none",
  "defect_reason": "BLURRY",
  "user_feedback_text": "Photo is blurry or unreadable. Please take a close-up photo of the leaf under direct light.",
  "calibrated_confidence": 0.0,
  "fail_closed_active": false,
  "response_text": "Photo is blurry or unreadable. Please take a close-up photo of the leaf under direct light.",
  "metrics": {
    "width": 640,
    "height": 480,
    "laplacian_variance": 42.5,
    "mean_luminance": 115.0,
    "dark_pixel_ratio": 0.05,
    "bright_pixel_ratio": 0.02,
    "foliage_pixel_ratio": 0.45,
    "latency_ms": 12.4
  }
}
```

---

## 2. IAV Hassan II Dataset Sample Record Validation Contract

Dataset records ingested via `scripts/ingest_iav_dataset.py` MUST conform to the `IAVDatasetRecord` schema:

```json
{
  "sample_id": "IAV-SM-2026-0042",
  "image_path": "data/iav_samples/IAV-SM-2026-0042.jpg",
  "crop_type": "tomatoes",
  "disease_onssa_code": "ONSSA-TOM-TYLCV-01",
  "severity_index": 3,
  "region": "Souss-Massa",
  "cultivar": "Moneymaker",
  "bounding_boxes": [
    {
      "xmin": 0.22,
      "ymin": 0.15,
      "xmax": 0.45,
      "ymax": 0.38
    }
  ]
}
```

ONSSA authorized product pointers are resolved dynamically against `data/onssa_authorized_products.json` with fallback to `ONSSA_STATIC_CATALOG`.
