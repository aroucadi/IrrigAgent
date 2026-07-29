# Python Module & REST Interface Contract: Image Pre-Filter OpenCV

**Feature**: `specs/007-image-prefilter-heuristics`  
**Date**: 2026-07-29

## 1. Internal Python Interface Contract

### Package: `app.image_prefilter`

#### Function: `validate_image_quality`

```python
def validate_image_quality(
    image_bytes: bytes,
    config: Optional[PreFilterConfig] = None
) -> QualityCheckResult:
    """
    Evaluates raw image bytes against OpenCV heuristics (Laplacian variance sharpness check,
    mean grayscale luminance, dark/bright clipping ratios, and minimum resolution).

    Args:
        image_bytes (bytes): Raw binary payload of the uploaded image (JPEG, PNG, WebP).
        config (Optional[PreFilterConfig]): Optional threshold settings. Uses environment defaults if None.

    Returns:
        QualityCheckResult: Object containing `is_acceptable` (bool), `defect_reason` (QualityDefectReason),
                            `user_feedback_text` (Optional[str]), and `metrics` (ImageQualityMetrics).
    """
```

#### Function: `get_prefilter_config_from_env`

```python
def get_prefilter_config_from_env() -> PreFilterConfig:
    """
    Constructs a PreFilterConfig using environment variables:
      - PREFILTER_ENABLED (bool, default: True)
      - PREFILTER_BLUR_THRESHOLD (float, default: 100.0)
      - PREFILTER_MIN_LUMINANCE (float, default: 40.0)
      - PREFILTER_MAX_LUMINANCE (float, default: 220.0)
      - PREFILTER_MAX_DARK_RATIO (float, default: 0.40)
      - PREFILTER_MAX_BRIGHT_RATIO (float, default: 0.35)
    """
```

---

## 2. CropDoctor Integration Contract

### Integration in `app.cropdoctor.perform_cropdoctor_triage`

When `perform_cropdoctor_triage(image_bytes, crop_type, ...)` is called:

1. `validate_image_quality(image_bytes)` is executed first.
2. If `result.is_acceptable` is `False` AND `config.enabled` is `True`:
   - Immediately return a dictionary with:
     ```python
     {
         "pathogen_identified": "unreadable",
         "symptom_name": None,
         "confidence_score": 0.0,
         "confidence_tier": None,
         "onssa_product_pointer": None,
         "disclaimer_included": False,
         "is_unreadable": True,
         "response_text": result.user_feedback_text,
         "prefilter_defect": result.defect_reason.value,
         "prefilter_metrics": result.metrics.model_dump() if result.metrics else None,
     }
     ```
   - **Zero calls** are made to `google.genai` vision models.
3. If `result.is_acceptable` is `True`, proceed to Gemini 1.5 Flash disease classification as usual.

---

## 3. Optional REST API Endpoint Contract

### Endpoint: `POST /cropdoctor/prefilter`

Exposes standalone pre-filter quality validation for client-side / test validation.

- **Content-Type**: `multipart/form-data`
- **Request Body**:
  - `file`: UploadFile (required)
- **Response Format**: `200 OK`

```json
{
  "is_acceptable": false,
  "defect_reason": "BLURRY",
  "user_feedback_text": "🍃 *Photo Out of Focus*: The leaf photo is blurry. Please hold your camera steady and retake a sharp, in-focus photo.",
  "metrics": {
    "width": 1280,
    "height": 720,
    "laplacian_variance": 42.15,
    "mean_luminance": 115.4,
    "dark_pixel_ratio": 0.05,
    "bright_pixel_ratio": 0.02,
    "latency_ms": 18.4
  }
}
```
