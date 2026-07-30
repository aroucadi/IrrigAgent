# Feature Specification: Fine-Tuned Disease Classifier & IAV Hassan II Interim Roadmap

**Feature Branch**: `010-iav-disease-classifier`

**Created**: 2026-07-29

**Status**: Active

**Input**: User description: "Feature 3: Section 2.2b — Fine-Tuned Disease Classifier (IAV Hassan II Dataset Strategy & Interim Execution)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Leaf Photo Disease Triage via Interim 2-Stage Pipeline (Priority: P1)

As a farm manager in Morocco, I want to send a leaf photo of an unthrifty or diseased crop via WhatsApp so that I receive an immediate first-pass diagnostic triage, ONSSA-authorized treatment options, and clear legal guidance.

**Why this priority**: Field agronomist access is limited during sudden disease outbreaks. An immediate interim diagnostic triage powered by Zero-Shot Gemini Flash and ONSSA vector RAG provides actionable guidance without waiting for the custom fine-tuned model dataset.

**Independent Test**: Can be fully tested by submitting valid leaf photos of tomatoes or citrus crops to the endpoint, verifying that quality checks pass, receiving diagnostic advice with ONSSA-listed active ingredients, and confirming the mandatory disclaimer is included.

**Acceptance Scenarios**:

1. **Given** a clear leaf photo (width/height ≥ 400px, blur variance ≥ 100.0, foliage green hue coverage ≥ 30%), **When** the farm manager sends the photo, **Then** the system passes the quality gate and routes the image to the Zero-Shot Gemini Flash engine with ONSSA Registry RAG.
2. **Given** a successful triage analysis, **When** the response is generated, **Then** the message lists potential disease matches, references ONSSA-authorized chemical products from `data/onssa_authorized_products.json`, and appends the verbatim mandatory disclaimer: *"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."*

---

### User Story 2 - Photo Quality Feedback & Re-shoot Guidance Gate (Priority: P1)

As a farm manager, I want immediate actionable feedback if my uploaded photo is blurry, low-resolution, or off-target so that I know exactly how to take a better picture without wasting diagnostic API calls.

**Why this priority**: Poor quality photos produce inaccurate vision predictions. Catching quality issues early protects farmers from misdiagnoses and minimizes costly AI inference overhead.

**Independent Test**: Can be fully tested by submitting blurry images, non-leaf photos, or low-resolution images (< 400px) and verifying that the system immediately rejects them with specific re-shoot instructions.

**Acceptance Scenarios**:

1. **Given** an image with Laplacian variance < 100.0 (blurry), resolution < 400px, or green foliage hue coverage < 30% (HSV hue range 35 ≤ H ≤ 85 in **OpenCV 0–180 scale**, corresponding to 70°–170° standard degrees), **When** the photo is processed by the Quality Gate, **Then** the system rejects the photo from AI triage and responds immediately: *"Photo is blurry or unreadable. Please take a close-up photo of the leaf under direct light."*

---

### User Story 3 - Transition to Calibrated Fine-Tuned Model (Phase 2.2b Activation) (Priority: P2)

As a system owner, I want the system to automatically switch from Zero-Shot Gemini Flash to a custom fine-tuned vision model (EfficientNet-B4) calibrated with temperature scaling once the IAV Hassan II Moroccan dataset milestone is reached so that farmers receive highly accurate localized disease classifications.

**Why this priority**: Moroccan cultivars (e.g., Moneymaker tomatoes, Nadorcott clementines) under local solar radiation and dust exhibit visual symptoms distinct from sterile lab photos in public datasets. Fine-tuning on local field data ensures top empirical performance.

**Independent Test**: Can be tested by simulating dataset readiness (≥ 500 verified photos per disease class from IAV Hassan II), running calibrated model inference on test images, and verifying fail-closed confidence logic (< 75% confidence defaults to general category advice).

**Acceptance Scenarios**:

1. **Given** the milestone dataset (≥ 500 verified Moroccan leaf photos per target disease class annotated with ONSSA code, severity grade 1-5, and bounding boxes) is loaded, **When** fine-tuning and temperature scaling calibration are complete, **Then** the Phase 2.2b classifier is activated as the primary vision engine.
2. **Given** a fine-tuned model prediction with calibrated confidence ≥ 75%, **When** rendering diagnostic results, **Then** the system outputs the specific disease ID and ONSSA-authorized chemical product options.
3. **Given** a fine-tuned model prediction with calibrated confidence < 75%, **When** rendering diagnostic results, **Then** the system fails closed to general non-chemical cultural advice (e.g., ventilation, irrigation adjustment) without naming specific chemical active ingredients.

---

### User Story 4 - IAV Hassan II Dataset Collaboration & Schema Ingestion (Priority: P3)

As a plant pathology researcher at IAV Hassan II, I want to upload field photos with standardized annotations (ONSSA code, severity index, bounding boxes) so that the dataset can seamlessly train and evaluate Phase 2.2b models.

**Why this priority**: Standardized annotation schema ensures data integrity across field agronomists and students collecting samples in Souss-Massa and Gharb regions.

**Independent Test**: Can be tested by validating sample dataset archives against the required annotation schema file formats.

**Acceptance Scenarios**:

1. **Given** an uploaded dataset archive from IAV Hassan II, **When** ingested by the dataset pipeline, **Then** every image record is validated for mandatory fields: Primary Disease ID (ONSSA Code), Severity Index (Grade 1 to 5), and bounding box coordinates of symptomatic lesions.

---

### Edge Cases

- What happens when a photo contains multiple symptomatic leaves with conflicting symptoms? The quality gate evaluates overall foliage coverage and the vision engine identifies the predominant lesion bounding boxes.
- What happens if an image passes quality checks but depicts a non-target crop (e.g., olive or wheat)? Zero-Shot triage identifies the crop misalignment and prompts the user that target vision support currently focuses on Tomatoes and Citrus.
- What happens if the ONSSA registry database is unavailable? System defaults to non-chemical cultural practices and appends the mandatory ONSSA legal disclaimer.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST perform Phase 2.2a Quality Gate pre-filtering on all incoming leaf photos before invoking AI triage services.
- **FR-002**: Quality Gate MUST enforce three heuristic checks:
  - Laplacian Variance Blur Detection (fail if score < 100.0).
  - Foliage Green Channel Coverage (fail if < 30% of pixels fall within HSV hue range 35 ≤ H ≤ 85 **in OpenCV 0–180 scale**, corresponding to standard degrees 70°–170°).
  - Minimum Image Resolution (fail if width < 400px or height < 400px).
- **FR-003**: System MUST return immediate re-shoot guidance to the user whenever any Quality Gate check fails, skipping AI model invocation.
- **FR-004**: System MUST deploy an interim 2-stage vision pipeline (Phase 2.2a) using Zero-Shot Gemini 1.5 Flash coupled with ONSSA Registry Vector RAG while awaiting the IAV Hassan II dataset.
- **FR-005**: System MUST cross-reference all identified symptoms and chemical pointers against the official ONSSA authorized product registry (`data/onssa_authorized_products.json`).
- **FR-006**: System MUST append the verbatim mandatory ONSSA disclaimer to every triage output: *"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."*
- **FR-007**: System MUST track dataset acquisition progress against the Phase 2.2b milestone trigger (≥ 500 verified Moroccan field photos per disease class sourced from IAV Hassan II across Souss-Massa and Gharb regions).
- **FR-008**: System MUST support dataset ingestion conforming to the IAV Hassan II annotation schema: Primary Disease ID (ONSSA Code), Severity Index (Grades 1-5), and symptomatic lesion bounding box coordinates.
- **FR-009**: Upon reaching the Phase 2.2b milestone, system MUST support activating a fine-tuned vision classifier (EfficientNet-B4) calibrated via Temperature Scaling.
- **FR-010**: System MUST implement a fail-closed confidence threshold at 75% for the calibrated model: predictions below 75% confidence MUST default to general cultural/sanitary category advice without naming specific chemical active ingredients.

### Key Entities

- **Leaf Photo Upload**: Raw image payload received from user, annotated with timestamp, resolution, blur score, and green coverage percentage.
- **Quality Gate Assessment**: Evaluation result object recording pass/fail status and specific rejection reasons.
- **Disease Diagnostic Triage**: Output payload containing disease identification, raw confidence score, `calibrated_confidence` (temperature-scaled via `p^T`), `fail_closed_active` flag (True when calibrated confidence < 0.75), severity grade, recommended ONSSA products (null when fail-closed), and mandatory legal disclaimer.
- **ONSSA Product Record**: Entity in authorized database containing ONSSA registration code, trade name, active ingredients, target crop, and target disease.
- **IAV Dataset Sample**: Training record containing field photo, regional origin (Souss-Massa/Gharb), crop type (Tomato/Citrus), disease ONSSA code, severity grade (1-5), and lesion bounding box coordinates.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Quality Gate assessment completes in under 300ms and accurately filters out 100% of images that score below the heuristic thresholds (Laplacian variance < 100.0 or resolution < 400px). *Note: This guarantee applies to images that score below the threshold on the heuristic; real-world camera blur detection accuracy at these thresholds is not guaranteed for all capture conditions.*
- **SC-002**: 100% of generated triage responses contain the exact, verbatim mandatory ONSSA regulatory disclaimer.
- **SC-003**: 100% of recommended chemical active ingredients are verified against the active ONSSA authorized registry (`data/onssa_authorized_products.json`).
- **SC-004**: *(Phase 2.2b — DEFERRED)* Temperature scaling calibration ensures that fine-tuned model reported confidence scores (e.g. 85%) correspond to within ±5% empirical accuracy on a held-out Moroccan field test set. Evaluation via ECE (Expected Calibration Error) measurement on a dedicated Moroccan field validation split. **Activation trigger**: automatic when `dataset_count_per_class ≥ 500` for all target disease classes — no separate manual operator gate required.
- **SC-005**: 100% of predictions with calibrated confidence < 75% fail closed to safe general category advice without exposing specific chemical names.
- **SC-006**: End-to-end vision triage response (from photo receipt through ONSSA RAG lookup to WhatsApp message dispatch) completes in under 3.0 seconds under normal network conditions.

## Assumptions

- Target crops for initial vision triage are restricted to Tomatoes (TYLCV, Tuta Absoluta, Early Blight) and Citrus (Citrus Greening/HLB, Alternaria Leaf Spot, Red Spider Mite).
- Public datasets (e.g., PlantVillage) are unsuitable for production in Morocco due to sterile laboratory lighting and missing local cultivar representations.
- IAV Hassan II collaboration will provide field photos captured under natural solar radiation in Souss-Massa and Gharb regions.
- WhatsApp Cloud API sandbox is the primary user interaction transport for photo submissions.

## Clarifications

### Session 2026-07-29

- Q: Which file is the canonical ONSSA authorized product registry? → A: `data/onssa_authorized_products.json` is the authoritative runtime registry. `data/onssa_registry.json` is the intermediate sync output from the ONSSA sync tool (spec 102e5b02) and must be renamed to `onssa_authorized_products.json` for consistency. The `VisionClassificationResult` Pydantic model will be added to `app/schemas.py` to formalize the triage response contract.
- Q: How to handle SC-001 latency test and SC-004 calibration tasks? → A: Add a latency assertion test for SC-001 (asserting `latency_ms < 300` on `ImageQualityMetrics`). SC-004 calibration evaluation is DEFERRED with a placeholder task in tasks.md until Phase 2.2b dataset milestone is reached.
- Q: Which temperature scaling formula notation should the spec canonically use? → A: Use `p^T` (scalar probability exponentiation) as the canonical form in T014 and quickstart.md, with a clarifying note that this approximates `softmax(z/T)` for full logit vector inputs.
- Q: How to handle non-target crop edge case test gap (G2) and T001/T005 task overlap (D1)? → A: Extend T006 scope to explicitly include a non-target crop redirect test (test already partially exists in `tests/unit/test_cropdoctor.py:L91`). T001 scope = existing schema field updates (foliage ratio, calibrated_confidence, fail_closed_active); T005 scope = new `IAVDatasetRecord` Pydantic model.
- Q: How specific should HSV scale clarification and SC-001 qualifier be? → A: FR-002 and US2 Acceptance Scenario: add parenthetical `(OpenCV 0–180 scale, corresponding to 70°–170° standard)`. SC-001: add scope qualifier that the 100% guarantee applies to images scoring below the heuristic threshold, not to all real-world blurry images.
- Q: US1 Acceptance Scenario 1.2 short disclaimer vs FR-006 full text — which is authoritative? → A: Update US1 Acceptance Scenario 1.2 to use the full verbatim Constitution §III disclaimer. FR-006 is authoritative; all Acceptance Scenarios must quote the full text verbatim.
- Q: Should Key Entities “Disease Diagnostic Triage” mention calibrated_confidence and fail_closed_active? → A: Yes. Updated to include `calibrated_confidence` (temperature-scaled via `p^T`) and `fail_closed_active` flag (True when calibrated confidence < 0.75, suppresses chemical names).
- Q: Should overall triage response latency < 3.0s appear as a measurable Success Criterion in spec.md? → A: Yes. Added as SC-006: end-to-end triage response < 3.0s under normal network conditions.
- Q: What is the explicit activation trigger for SC-004 (calibration evaluation)? → A: Automatic — triggered when `dataset_count_per_class ≥ 500` for all target disease classes. No separate manual operator gate required.
- Q: Should the spec Status be updated from “Draft” to “Active” given implementation is complete? → A: Yes. Status updated to “Active”.
