# Implementation Plan: Image Pre-Filter OpenCV Heuristics

**Branch**: `007-image-prefilter-heuristics` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/007-image-prefilter-heuristics/spec.md)

**Input**: Feature specification from `/specs/007-image-prefilter-heuristics/spec.md`

## Summary

Build a high-performance image pre-filtering quality gate using OpenCV heuristics (`app/image_prefilter.py`) that evaluates incoming crop leaf photos for sharpness (Laplacian variance), exposure (mean luminance and clipping ratios), file validity, and minimum resolution. The pre-filter intercepts blurry or improperly exposed photos in `perform_cropdoctor_triage()` before invoking Gemini 1.5 Flash vision models, delivering sub-second retake feedback to farm managers over WhatsApp while eliminating unnecessary AI API token costs.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: OpenCV (`opencv-python-headless`), NumPy, FastAPI, Pydantic, `google-genai`

**Storage**: In-memory byte array processing; Firestore for interaction logging

**Testing**: `pytest`, `pytest-asyncio`

**Target Platform**: GCP Cloud Run (Linux container) / Local Windows virtual environment

**Project Type**: Web service (FastAPI) & Image processing module

**Performance Goals**: Sub-200ms p95 evaluation latency per photo (target < 50ms average)

**Constraints**: Zero AI token cost on rejected photos; 100% test pass rate under `pytest tests/`; sub-second end-to-end WhatsApp response

**Scale/Scope**: All incoming leaf photos submitted to CropDoctor disease triage pipeline

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Human-in-the-Loop Only**: PASS. Triage feedback is sent to farm manager via WhatsApp. No hardware/solenoid automation.
- **II. Rule-Based First Logic**: PASS. Pre-filter quality checks use deterministic OpenCV mathematical formulas (Laplacian variance, mean grayscale intensity) prior to LLM invocation.
- **III. Mandatory ONSSA Regulatory Disclaimer**: PASS. CropDoctor responses retain regulatory disclaimers.
- **IV. WhatsApp Cloud API Sandbox**: PASS. Execution fits within sandbox payload limits and latency windows.
- **V. Strict Scope Boundary**: PASS. Pre-filtering is strictly limited to leaf photo quality validation for CropDoctor triage.
- **VI. End-to-End Demoability**: PASS. Can be demonstrated end-to-end with blurry/dark/sharp leaf photos.
- **VII. Infrastructure as Code**: PASS. Uses standard GCP Cloud Run environment variables for configurable thresholds.
- **VIII. Quality, Security & Automated Verification Gates**: PASS. Unit test suite enforces deterministic test coverage for blur and exposure calculations.

*All Constitution Gates: PASSED.*

## Project Structure

### Documentation (this feature)

```text
specs/007-image-prefilter-heuristics/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical analysis & heuristic choices
├── data-model.md        # Quality metrics & configuration schemas
├── quickstart.md        # Runnable validation guide & curl examples
├── contracts/           # API and python module contracts
│   └── image-prefilter-contract.md
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
app/
├── image_prefilter.py   # [NEW] OpenCV heuristic evaluation engine
├── cropdoctor.py        # [MODIFY] Integrate pre-filter quality gate in perform_cropdoctor_triage
├── main.py              # [MODIFY] Expose optional POST /cropdoctor/prefilter endpoint
├── schemas.py           # [MODIFY] Export QualityCheckResult & PreFilterConfig models
└── config.py            # [MODIFY] Load pre-filter threshold environment variables

requirements.txt         # [MODIFY] Add opencv-python-headless & numpy

tests/
└── test_image_prefilter.py  # [NEW] Comprehensive unit tests for blur, exposure, and cropdoctor bypass
```

**Structure Decision**: Single project layout consistent with `app/` and `tests/` backend microservice structure on GCP Cloud Run.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations. System adheres to rule-based first principles and modular FastAPI/Pytest standards.*
