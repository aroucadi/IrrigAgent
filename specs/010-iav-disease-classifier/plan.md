# Implementation Plan: Fine-Tuned Disease Classifier & IAV Hassan II Strategy

**Branch**: `010-iav-disease-classifier` | **Date**: 2026-07-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/010-iav-disease-classifier/spec.md`

**Plan Revision**: v2 — Post `/speckit-analyze` remediation pass (2026-07-29)

> **Revision Summary**: This plan supersedes the original v1 plan. It incorporates all 13 findings from `/speckit-analyze` and 5 targeted clarification decisions from `/speckit-clarify`. Structural changes: (1) ONSSA registry file canonical rename, (2) `VisionClassificationResult` Pydantic model added to `app/schemas.py`, (3) temperature scaling formula notation corrected to `p^T`, (4) two new tasks added (T020 latency assertion, T021 DEFERRED calibration ECE), (5) all independent test selectors updated to match actual test file locations.

## Summary

Implement the Phase 2.2b fine-tuned vision classification roadmap and IAV Hassan II dataset strategy while maintaining the Phase 2.2a interim 2-stage production pipeline (OpenCV Quality Gate + Zero-Shot Gemini 1.5 Flash + ONSSA Registry Vector RAG). The plan introduces temperature scaling calibration for PyTorch vision models (EfficientNet-B4) using the **`p^T` scalar probability approximation** (equivalent to `softmax(z/T)` for logit vectors), a 75% fail-closed confidence safety threshold, and standardized annotation schema ingestion for Moroccan field photos from IAV Hassan II.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: OpenCV (`opencv-python`), PyTorch (`torch`, `torchvision`), Google GenAI SDK (`google-genai`), FastAPI, Pydantic, pytest

**Storage**:
- `data/onssa_authorized_products.json` — **Canonical runtime ONSSA authorized product registry** (renamed from `onssa_registry.json` per C2 remediation)
- Local/cloud dataset manifests for IAV Hassan II images
- Firestore interaction logs

**Testing**: `pytest tests/` (100% passing rate enforced — currently 125/125)

**Target Platform**: GCP Cloud Run (Python 3.11 containerized web service)

**Project Type**: Web Service / ML Inference Pipeline

**Performance Goals**:
- Quality Gate heuristic evaluation < 300ms (SC-001, verified via `ImageQualityMetrics.latency_ms`)
- Overall vision triage response < 3.0s

**Constraints**:
- Temperature scaling: `calibrated = raw_confidence ** T` where T=1.25 by default
- Mandatory fail-closed threshold at < 75% calibrated confidence
- Verbatim ONSSA legal disclaimer on 100% of triage messages
- Constitution §III disclaimer: *"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."*

**Scale/Scope**: Tomatoes (TYLCV, Tuta Absoluta, Early Blight) & Citrus (Citrus Greening/HLB, Alternaria Leaf Spot, Red Spider Mite); ≥ 500 verified photos per disease class for Phase 2.2b activation.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Governance Principle | Status | Compliance Verification |
| :--- | :--- | :--- |
| **I. Human-in-the-Loop Only** | **PASS** | Triage outputs non-prescriptive recommendations to farm managers via WhatsApp; no automated hardware action. |
| **II. Rule-Based First Logic** | **PASS** | OpenCV quality pre-filter and 75% fail-closed confidence thresholds use deterministic rules. |
| **III. Mandatory ONSSA Disclaimer** | **PASS ✅ (remediated)** | Full verbatim disclaimer now enforced in FR-006, spec.md Acceptance Scenario 1.2, T008, response_text output, and contracts. Chemical pointers from `data/onssa_authorized_products.json` only. |
| **IV. WhatsApp Sandbox Tier** | **PASS** | Transport strictly bounded to sandbox tier. |
| **V. Strict Scope Boundary** | **PASS** | No solenoid control or billing logic added. |
| **VI. End-to-End Demoability** | **PASS** | Runnable test scenarios in `quickstart.md`; 125/125 tests passing. |
| **VII. Infrastructure as Code** | **PASS** | Cloud Run services defined via Terraform. |
| **VIII. Quality & Security Gates** | **PASS** | Zero-broken-tests policy enforced (`pytest tests/`). |

## Post-Analysis Remediation Registry

*Tracks all 13 findings from `/speckit-analyze` and their resolution status.*

| Finding ID | Severity | Category | Status | Resolution |
| :--- | :--- | :--- | :--- | :--- |
| **C1** | CRITICAL | Constitution | ✅ Resolved | `spec.md` FR-006 + US1 Acceptance Scenario 1.2 updated to full verbatim §III disclaimer |
| **C2** | CRITICAL | Constitution | ✅ Resolved | `onssa_registry.json` → `onssa_authorized_products.json` canonical rename (code + spec + plan) |
| **I1** | HIGH | Inconsistency | ✅ Resolved | FR-002 + US2 now include `(OpenCV 0–180 scale, corresponding to 70°–170° standard degrees)` |
| **I2** | HIGH | Inconsistency | ✅ Resolved | T014 formula updated from `z/T` to `p^T` with `≈ softmax(z/T)` equivalence note |
| **A1** | HIGH | Ambiguity | ✅ Resolved | SC-001 scope qualifier added: guarantee applies to images scoring below heuristic threshold only |
| **A2** | MEDIUM | Ambiguity | ✅ Resolved | SC-004 marked DEFERRED; T021 placeholder task added with ECE measurement scope |
| **U1** | HIGH | Underspecification | ✅ Resolved | Phase 6 independent test: `pytest tests/test_iav_disease_classifier.py -k "TestValidateIAVDatasetRecord"` |
| **U2** | MEDIUM | Underspecification | ✅ Resolved | Phase 5 independent test: `pytest tests/test_iav_disease_classifier.py::TestFailClosedBehavior` |
| **U3** | MEDIUM | Underspecification | ✅ Resolved | `VisionClassificationResult` Pydantic model added to `app/schemas.py` (new code task) |
| **U4** | LOW | Underspecification | ✅ Resolved | T018 now explicitly names `calibrated_confidence` + `fail_closed_active` fields for contract update |
| **G1** | HIGH | Coverage Gap | ✅ Resolved | T020 added: latency assertion test (`latency_ms < 300`) in `tests/test_image_prefilter.py` |
| **G2** | MEDIUM | Coverage Gap | ✅ Resolved | T006 extended to include non-target crop redirect test (olive/wheat polite redirect assertion) |
| **D1** | LOW | Duplication | ✅ Resolved | T001 scope = existing schema field updates; T005 scope = new `IAVDatasetRecord` Pydantic model |

## Project Structure

### Documentation (this feature)

```text
specs/010-iav-disease-classifier/
├── plan.md              # This file (v2 remediation)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (updated: VisionClassificationResult formalized)
├── quickstart.md        # Phase 1 output (updated: p^T formula notation, latency assertion)
├── contracts/           # Phase 1 output (updated: calibrated_confidence + fail_closed_active fields)
│   └── disease-classifier-contracts.md
└── tasks.md             # Phase 2 output (updated: T001–T021 with all remediation fixes)
```

### Source Code Layout

```text
app/
├── config.py            # Environment configurations & pre-filter parameters (TEMPERATURE_SCALING_PARAM, FAIL_CLOSED_CONFIDENCE_THRESHOLD)
├── cropdoctor.py        # Vision triage engine; apply_temperature_scaling(p^T); validate_iav_dataset_record; ONSSA registry RAG
├── image_prefilter.py   # OpenCV quality gate (blur, resolution, foliage green HSV 35–85 OpenCV scale)
├── schemas.py           # Pydantic schemas: QualityCheckResult, ImageQualityMetrics, VisionClassificationResult [NEW], IAVDatasetRecord [NEW]
├── main.py              # FastAPI Webhook & Diagnostic endpoints
└── whatsapp.py          # WhatsApp message formatter & transport

data/
└── onssa_authorized_products.json  # Canonical ONSSA authorized chemical index (renamed from onssa_registry.json)

scripts/
└── ingest_iav_dataset.py            # IAV Hassan II batch ingestor with milestone check
                                     # (DEFERRED) evaluate_calibration.py — Phase 2.2b ECE measurement

tests/
├── test_cropdoctor.py                  # Unit tests: triage, confidence tiers, legal disclaimers, non-target crop redirect
├── test_iav_disease_classifier.py      # Tests: temperature scaling (p^T), IAV record validation, fail-closed behavior
├── test_image_prefilter.py             # OpenCV heuristic + T020 latency assertion (latency_ms < 300)
└── unit/test_cropdoctor.py             # Updated: medium confidence fail-closed behavior
```

**Structure Decision**: Single project layout extending existing `app/`, `data/`, and `tests/` directories. No new top-level directories required.

## Phase 0: Research Decisions

*Already resolved — see `research.md`. Summarized for plan completeness.*

| Decision | Rationale | Alternatives Considered |
| :--- | :--- | :--- |
| **Canonical ONSSA file**: `onssa_authorized_products.json` | Single authoritative runtime file; sync tool writes to this canonical name | `onssa_registry.json` (intermediate sync output — renamed) |
| **Temperature scaling formula**: `calibrated = p ** T` | Scalar approximation of `softmax(z/T)` for already-softmax'd model outputs; correct direction (T>1 reduces confidence) | `p ** (1/T)` — wrong direction (amplifies overconfidence) |
| **Foliage hue range**: 35–85 in OpenCV 0–180 scale | Covers plant green at H≈60; config values are already in OpenCV scale and must NOT be divided by 2 | Standard degree scale (70°–170°) with `/2` conversion — caused bug, now removed |
| **VisionClassificationResult**: formal Pydantic model in `app/schemas.py` | Explicit contract; currently triage returns a plain dict — Pydantic model enforces field types for future API stability | Keep as plain dict; add TypedDict annotation |

## Phase 1: Design Artifacts

### Updated Data Model Changes

**New entity to add to `data-model.md`**:

`VisionClassificationResult` — formal Pydantic response model (currently returned as plain dict from `perform_cropdoctor_triage`):

| Field | Type | Description | Validation |
| :--- | :--- | :--- | :--- |
| `pathogen_identified` | string | Disease key or `unreadable` | Required |
| `symptom_name` | string / null | French/Darija descriptive name | Null if unreadable |
| `confidence_score` | float | Raw uncalibrated model output | Range 0.0–1.0 |
| `calibrated_confidence` | float | `raw_confidence ** T` temperature-scaled | Range 0.0–1.0 |
| `confidence_tier` | string / null | `high` (≥0.75), `medium` (0.50–0.74), `low` (<0.50) | Null if unreadable |
| `fail_closed_active` | boolean | True if calibrated_confidence < 0.75 | Suppresses chemical names |
| `onssa_product_pointer` | string / null | ONSSA authorized product | Null when `fail_closed_active` |
| `disclaimer_included` | boolean | Verbatim §III disclaimer present | Always True on diagnosis |
| `is_unreadable` | boolean | True if photo rejected | |
| `response_text` | string | Full WhatsApp-formatted message | Required |

**Updated entity in `data-model.md`**:

`LeafPhotoQualityMetrics` — add `latency_ms` field (already present in `ImageQualityMetrics` Pydantic model, needs to appear explicitly in data-model):

| Field | Type | Description | Validation |
| :--- | :--- | :--- | :--- |
| `latency_ms` | float | Quality Gate wall-clock evaluation time | `< 300.0` per SC-001 |

### Contract Updates Required

**`disease-classifier-contracts.md`** needs two additions:
1. Response example must add `calibrated_confidence` and `fail_closed_active` to the failed-quality-gate response (currently missing from that variant)
2. Add a Phase 2.2a (Gemini Zero-Shot) response example alongside the existing Phase 2.2b (EfficientNet-B4) example
3. Rename `onssa_registry.json` → `onssa_authorized_products.json` in any contract narrative references

### Quickstart Updates Required

**`quickstart.md`** needs:
1. Update temperature scaling formula from `z/T` → `p^T` with equivalence note
2. Add latency assertion step: verify `metrics.latency_ms < 300` in prefilter response
3. Add non-target crop test scenario: submit olive/wheat image → verify polite redirect

## Implementation Task Map

*All tasks in `tasks.md` — summary of code changes required:*

| Task ID | File(s) Modified | Type | Finding(s) |
| :--- | :--- | :--- | :--- |
| T001 | `app/schemas.py` | Update existing models | D1 (scope clarified) |
| T002 | `app/config.py` | No change needed (already correct) | — |
| T003 | `app/image_prefilter.py` | Bug fix (hue `/2` removed ✅ done) | I1 |
| T004 | `app/cropdoctor.py` | Formula fix (`p^T` ✅ done) | I2 |
| T005 | `app/schemas.py` | Add `IAVDatasetRecord` Pydantic model | D1 (scope clarified) |
| T006 | `tests/unit/test_cropdoctor.py` | Add non-target crop assert | G2 |
| T007 | `app/cropdoctor.py` | File rename: `onssa_authorized_products.json` | C2 |
| T008 | `app/cropdoctor.py` | Full disclaimer text | C1 |
| T013 | `tests/test_iav_disease_classifier.py` | Selector updated ✅ done | U2 |
| T014 | `app/cropdoctor.py` | `p^T` notation docs | I2 |
| T016 | `tests/test_iav_disease_classifier.py` | Selector updated ✅ done | U1 |
| **T018** | `contracts/disease-classifier-contracts.md` | Add new fields explicitly | U4 |
| **T020** [NEW] | `tests/test_image_prefilter.py` | Latency assertion `< 300ms` | G1 |
| **T021** [NEW/DEFERRED] | `scripts/evaluate_calibration.py` | ECE measurement script | A2 |
| U3 | `app/schemas.py` | Add `VisionClassificationResult` model | U3 |

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| :--- | :--- | :--- |
| *None* | N/A | No violations of constitution principles exist after remediation. |
