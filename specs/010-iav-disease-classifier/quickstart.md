# Quickstart Validation Guide: Fine-Tuned Disease Classifier & IAV Hassan II Roadmap

**Feature**: `010-iav-disease-classifier`

## Prerequisites
- Python 3.11+ virtual environment with `pytest`, `numpy`, `opencv-python`.
- Active repository root `d:\rouca\DVM\workPlace\IrrigAgent`.

## Runnable Validation Scenarios

### Scenario 1: Quality Gate Image Pre-Filter Rejection & Latency Assertion (< 300ms)
Validates that blurry (< 100.0 variance), low-resolution (< 400px), or non-foliage photos are rejected instantly before AI vision model invocation, and asserts Quality Gate execution completes in < 300ms.

```bash
pytest tests/test_image_prefilter.py -v
```
**Expected Outcome**: Image quality check returns `is_acceptable=False` for sub-threshold images and outputs feedback message: *"Photo is blurry or unreadable. Please take a close-up photo of the leaf under direct light."* Valid images complete Quality Gate evaluation with `latency_ms < 300.0`.

---

### Scenario 2: Phase 2.2a Interim Triage (Zero-Shot Gemini Flash + ONSSA RAG) & Non-Target Crop Redirect
Validates interim 2-stage triage when processing acceptable quality photos and checks non-target crop handling (e.g. olives, wheat).

```bash
pytest tests/unit/test_cropdoctor.py -v
```
**Expected Outcome**: Triage returns disease diagnostic message referencing ONSSA authorized chemical classes from `data/onssa_authorized_products.json` and appends the verbatim disclaimer: *"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."* Unsupported crops return: *"target vision support currently focuses on Tomatoes and Citrus."* End-to-end response completes in < 3.0 seconds (SC-006).

---

### Scenario 3: Temperature Scaling Calibration (`p^T`) & Fail-Closed Confidence Threshold (< 75%)
Validates temperature scaling calibration (`calibrated = raw ** T`, approximating `softmax(z/T)` for logit vectors) and enforces that predictions with calibrated confidence < 75% fail closed by withholding specific active ingredient names.

```bash
pytest tests/test_iav_disease_classifier.py::TestFailClosedBehavior tests/test_iav_disease_classifier.py::TestApplyTemperatureScaling -v
```
**Expected Outcome**: Calibrated confidence score softening is confirmed (`p ** T < p` when T=1.25). Output text for confidence < 75% provides general cultural management advice, sets `fail_closed_active=True`, sets `onssa_product_pointer=None`, and includes the mandatory ONSSA legal disclaimer.

---

### Scenario 4: IAV Hassan II Dataset Schema Validation
Validates that incoming dataset batches conform to mandatory annotation fields (`disease_onssa_code`, `severity_index` 1–5, `bounding_boxes`, `region`).

```bash
pytest tests/test_iav_disease_classifier.py::TestValidateIAVDatasetRecord -v
```
**Expected Outcome**: Batch validator accepts valid records and flags records missing required ONSSA disease codes or invalid severity indices.

---

### Full Test Suite Run
Execute all 125+ automated unit and integration tests across the project:

```bash
py -m pytest tests/ -v
```
**Expected Outcome**: 100% passing test rate (0 failures).
