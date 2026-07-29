# Research & Heuristic Analysis: Image Pre-Filter OpenCV

**Feature**: `specs/007-image-prefilter-heuristics`  
**Date**: 2026-07-29

## Overview

The image pre-filter acts as an immediate, low-latency, zero-cost quality gate for incoming leaf photos submitted to CropDoctor. By rejecting out-of-focus (blurry), underexposed (too dark), or overexposed (glare-heavy) photos before invoking Google Gemini 1.5 Flash vision models, the system reduces API costs, prevents inaccurate disease predictions, and provides instant actionable feedback to farmers.

---

## Technical Decisions & Trade-Offs

### 1. In-Memory Image Decoding

- **Decision**: Decode image bytes in memory using OpenCV `cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)`.
- **Rationale**: Farmers upload photos via WhatsApp or HTTP requests as raw bytes (JPEG/PNG/WebP). Decoding directly in memory avoids disk I/O latency on GCP Cloud Run ephemeral filesystems.
- **Alternatives Considered**: 
  - *Pillow (PIL)*: Good for simple image metadata, but requires extra conversion step to NumPy array for OpenCV Laplacian matrix operations.
  - *Saving to temporary file*: Unnecessary disk write overhead and risks resource leaks in serverless containers.

### 2. Sharpness / Blur Detection Heuristic

- **Decision**: Grayscale conversion (`cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)`) followed by Laplacian matrix variance calculation (`cv2.Laplacian(gray, cv2.CV_64F).var()`).
- **Threshold**: Default `100.0` (configurable via `PREFILTER_BLUR_THRESHOLD`).
- **Rationale**: Laplacian variance is the industry-standard, fast 2D focus measurement heuristic. High variance indicates sharp edges and fine leaf details (veins, spots); low variance indicates smooth, out-of-focus blur. Execution time is under 15ms.
- **Alternatives Considered**:
  - *Fast Fourier Transform (FFT) high-frequency analysis*: More computationally intensive (~80ms vs ~10ms) with marginal gain over Laplacian variance for leaf macro photos.
  - *Deep learning blur classifier*: Requires loading heavy model weights into Cloud Run RAM and increases cold-start time.

### 3. Exposure & Lighting Heuristic

- **Decision**: Compute dual exposure metrics on 8-bit grayscale matrix ($0..255$):
  1. **Mean Luminance ($\mu$)**: $\text{mean}(I_{gray})$. Acceptable band: $40.0 \le \mu \le 220.0$.
  2. **Clipped Pixel Percentages**:
     - Dark clipping ratio ($R_{dark}$): Percentage of pixels with intensity $< 15$.
     - Bright clipping ratio ($R_{bright}$): Percentage of pixels with intensity $> 245$.
  - **Rejection Rule**:
    - If $\mu < 40.0$ or $R_{dark} > 0.40$ $\rightarrow$ Reject as `TOO_DARK`.
    - If $\mu > 220.0$ or $R_{bright} > 0.35$ $\rightarrow$ Reject as `TOO_BRIGHT`.
- **Rationale**: Leaf photos taken under direct sunlight produce extreme glare ($R_{bright} > 35\%$), while photos taken inside shade or at dusk produce low mean luminance ($\mu < 40$). Checking both mean luminance and clipped histogram tails prevents false passes on high-contrast photos (e.g. dark leaf on white background).
- **Alternatives Considered**:
  - *HSV Color space V-channel alone*: Similar results to grayscale mean, but grayscale conversion is faster and standard across OpenCV pipelines.

### 4. Integration Architecture

- **Decision**: Modular pure-function package `app/image_prefilter.py` with entry point `validate_image_quality(image_bytes: bytes, config: Optional[PreFilterConfig] = None) -> QualityCheckResult`.
- **Integration with `app/cropdoctor.py`**:
  - `perform_cropdoctor_triage()` calls `validate_image_quality()` as step 0.
  - If `is_acceptable` is `False` (and `PREFILTER_ENABLED` is true), `perform_cropdoctor_triage()` immediately returns a structured `is_unreadable=True` diagnostic response with specific retake instructions without calling `google.genai`.
  - Feature flag `PREFILTER_ENABLED` (default `true`) allows emergency bypass if needed.

---

## Performance Benchmark Goals

| Metric | Target | Verification Method |
| :--- | :--- | :--- |
| **Pre-filter Latency** | $< 50$ ms average, $< 200$ ms p95 | Automated benchmark test on 4K smartphone photos |
| **Blur Detection Accuracy** | $> 95\%$ rejection on out-of-focus samples | Test suite with synthetic & real blurred test images |
| **Exposure Detection Accuracy** | $> 95\%$ rejection on dark/glare samples | Test suite with synthetic dark & overexposed images |
| **API Cost Reduction** | $100\%$ savings on rejected photos | Zero external API calls triggered on pre-filter failure |
