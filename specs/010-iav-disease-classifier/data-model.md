# Data Model: Fine-Tuned Disease Classifier & IAV Hassan II Strategy

**Feature**: `010-iav-disease-classifier`
**Status**: Complete

## Core Entities

### 1. LeafPhotoQualityMetrics
Extends existing pre-filter metrics with foliage color coverage analysis.

| Field | Type | Description | Validation |
| :--- | :--- | :--- | :--- |
| `width` | integer | Image width in pixels | `≥ 400` |
| `height` | integer | Image height in pixels | `≥ 400` |
| `laplacian_variance` | float | Laplacian blur score | `≥ 100.0` for pass |
| `foliage_pixel_ratio` | float | Fraction of pixels in HSV green hue range (35°–85°) | `≥ 0.30` for pass |
| `is_acceptable` | boolean | Overall quality check result | True if all criteria pass |
| `defect_reason` | string | Code representing quality failure reason | Enum value or `NONE` |

---

### 2. IAVDatasetRecord
Schema for ingested Moroccan field leaf photos provided by IAV Hassan II.

| Field | Type | Description | Validation |
| :--- | :--- | :--- | :--- |
| `sample_id` | string | Unique record ID | Required |
| `image_path` | string | Path to field photo file | Required |
| `crop_type` | string | Crop category (`tomatoes`, `citrus`) | Enum (`tomatoes`, `citrus`) |
| `disease_onssa_code` | string | ONSSA primary disease identifier | Valid ONSSA code |
| `severity_index` | integer | Disease severity rating | Integer `1` to `5` |
| `bounding_boxes` | list[dict] | Lesion coordinates `[xmin, ymin, xmax, ymax]` | Normalized float values 0.0–1.0 |
| `region` | string | Geographical collection region | `Souss-Massa` or `Gharb` |
| `cultivar` | string | Moroccan crop variety | e.g. `Moneymaker`, `Nadorcott` |

---

### 3. VisionClassificationResult
Representation of disease diagnosis payload from interim (Zero-Shot Gemini) or Phase 2.2b (Fine-Tuned) model.

| Field | Type | Description | Validation |
| :--- | :--- | :--- | :--- |
| `vision_engine` | string | Active engine identifier | `gemini-1.5-flash-zeroshot` or `efficientnet-b4-calibrated` |
| `pathogen_identified` | string | Disease key / ONSSA code | Required |
| `symptom_name_fr` | string | French/Darija descriptive name | Required |
| `raw_confidence` | float | Uncalibrated model output score | Range 0.0 to 1.0 |
| `calibrated_confidence` | float | Temperature-scaled confidence score | Range 0.0 to 1.0 |
| `confidence_tier` | string | Tier classification | `high` (≥0.75), `medium` (0.50–0.74), `low` (<0.50) |
| `fail_closed_active` | boolean | True if <0.75 confidence suppressed chemical names | Boolean |
| `onssa_product_pointer` | string / null | Recommended ONSSA chemical product | Null if `fail_closed_active` is True |
| `disclaimer_included` | boolean | Verification of verbatim disclaimer presence | Must be True |

---

### 4. VisionPipelineConfig
System configuration governing engine selection and milestone triggers.

| Field | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `phase_2_2b_active` | boolean | Toggle for fine-tuned EfficientNet model | `False` (defaults to interim 2.2a) |
| `dataset_count_per_class` | map[string, int] | Current count of verified IAV samples per disease | Required |
| `milestone_threshold` | integer | Min verified samples required per class to activate 2.2b | `500` |
| `confidence_fail_closed_threshold` | float | Minimum calibrated confidence to specify chemical active ingredient | `0.75` |
