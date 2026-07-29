# Quickstart & Validation Guide: Image Pre-Filter OpenCV

**Feature**: `specs/007-image-prefilter-heuristics`  
**Date**: 2026-07-29

## Prerequisites & Installation

1. Ensure the Python 3.11 virtual environment is activated.
2. Install required dependencies (`opencv-python-headless` and `numpy`):
   ```bash
   pip install opencv-python-headless>=4.8.0 numpy>=1.24.0
   ```

---

## Runnable Validation Commands

### 1. Execute Unit Test Suite

Run the dedicated pre-filter test suite:

```bash
pytest tests/test_image_prefilter.py -v
```

Expected output:
- `test_sharp_image_passes`: Sharp synthetic image passes pre-filter.
- `test_blurry_image_rejected`: Blurry synthetic image (Gaussian blurred) is rejected with `BLURRY` defect.
- `test_dark_image_rejected`: Dark image (low pixel values) is rejected with `TOO_DARK` defect.
- `test_bright_image_rejected`: Bright image (high pixel values/glare) is rejected with `TOO_BRIGHT` defect.
- `test_corrupt_bytes_rejected`: Corrupt byte stream is rejected with `CORRUPT_OR_INVALID` defect.
- `test_cropdoctor_integration_bypasses_gemini`: Verify `perform_cropdoctor_triage()` returns early without calling Gemini API when image is blurry.

### 2. Run Full Integration Test Suite

Verify that all existing project tests continue to pass (Zero-Broken-Tests policy):

```bash
pytest tests/ -v
```

---

## Manual Verification via REST Endpoint

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

Use `curl` or Postman to test image pre-filtering:

```bash
curl -X POST "http://localhost:8000/cropdoctor/prefilter" \
  -F "file=@path/to/test_leaf.jpg"
```

Sample Response:
```json
{
  "is_acceptable": true,
  "defect_reason": "NONE",
  "user_feedback_text": null,
  "metrics": {
    "width": 1920,
    "height": 1080,
    "laplacian_variance": 342.8,
    "mean_luminance": 128.5,
    "dark_pixel_ratio": 0.08,
    "bright_pixel_ratio": 0.04,
    "latency_ms": 22.1
  }
}
```
