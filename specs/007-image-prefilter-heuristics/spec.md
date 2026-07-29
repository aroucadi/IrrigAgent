# Feature Specification: Image Pre-Filter OpenCV Heuristics

**Feature Branch**: `007-image-prefilter-heuristics`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "Build an image pre-filter using OpenCV heuristics (Laplacian variance blur check and exposure validation) to reject poor photos before submission to the disease classifier."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fast Rejection of Blurry Photos (Priority: P1)

As a farm manager submitting crop leaf photos via WhatsApp for disease diagnosis, I want immediate feedback if my photo is out of focus or blurry, so that I don't receive inaccurate disease diagnoses or wait for AI analysis on unreadable images.

**Why this priority**: Out-of-focus leaf photos are the most common source of false disease predictions. Catching them instantly saves AI model cost and gives farmers immediate feedback to retake the shot.

**Independent Test**: Upload a intentionally blurry leaf photo (e.g., motion blurred or out of focus). The system must reject the image in sub-second time without invoking external AI vision services, returning clear guidance to retake a clear photo.

**Acceptance Scenarios**:

1. **Given** a user uploads a leaf photo with Laplacian variance below the sharpness threshold, **When** the pre-filter processes the image, **Then** the system rejects the photo, logs a blur failure result, and sends immediate retake feedback to the user explaining that the photo is out of focus.
2. **Given** a user uploads a sharp, well-focused leaf photo, **When** the pre-filter processes the image, **Then** the blur check passes and the image proceeds to subsequent validation checks.

---

### User Story 2 - Validation of Extreme Exposure and Lighting (Priority: P2)

As a farm manager taking leaf photos under harsh sunlight or in low light, I want the system to check whether my photo is underexposed (too dark) or overexposed (glare/washed out), so that I know to adjust my camera angle or lighting before requesting diagnosis.

**Why this priority**: Poor lighting obscures leaf lesions, veins, and discoloration, leading to misdiagnoses or inconclusive AI results.

**Independent Test**: Upload an underexposed photo (near black) and an overexposed photo (glare-heavy/washed out). The pre-filter must detect extreme brightness distribution issues and notify the user with specific retake instructions.

**Acceptance Scenarios**:

1. **Given** a photo with mean luminance below the dark threshold or above the bright threshold, **When** exposure validation runs, **Then** the photo is rejected with specific exposure guidance (e.g., "Photo too dark" or "Too much glare/bright light").
2. **Given** a photo with balanced luminance and histogram spread within normal limits, **When** exposure validation runs, **Then** the exposure check passes.

---

### User Story 3 - Comprehensive Quality Gate & Diagnostic Logging (Priority: P3)

As a system operator, I want all image pre-filtering checks (sharpness, exposure, corruption/dimensions) to yield structured diagnostic scores and failure reasons, so that quality metrics can be audited and fine-tuned over time.

**Why this priority**: Provides observability into crop photo rejection rates, allowing operators to adjust quality thresholds based on real field data without breaking user flows.

**Independent Test**: Process a batch of valid and invalid sample images through the pre-filter pipeline. Verify that each image returns a deterministic structured report containing pass/fail status, numeric sharpness score, mean luminance, and error categories.

**Acceptance Scenarios**:

1. **Given** any uploaded image, **When** pre-filtering completes, **Then** a structured diagnostic payload is produced recording sharpness variance, luminance metrics, validation decision, and execution latency.
2. **Given** a photo that passes all heuristic checks, **When** pre-filtering completes, **Then** the image is approved for submission to downstream disease classification services.

---

### Edge Cases

- What happens when an uploaded file is corrupted, zero-byte, or not a valid image format?
  - System MUST intercept file decoding errors before OpenCV evaluation and reject with an "invalid file format" message without crashing.
- What happens when a photo has dark leaf spots on a bright background (high contrast)?
  - Exposure validation MUST evaluate overall image luminance distribution and avoid false rejections on healthy/diseased leaves with natural contrast.
- What happens when multiple quality issues occur simultaneously (e.g., blurry AND dark)?
  - Pre-filter MUST report the primary quality defect or a combined actionable recommendation so the user gets complete feedback in a single message.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST perform an automated image quality pre-filter on all incoming crop photos before passing them to downstream disease classification services.
- **FR-002**: System MUST evaluate image sharpness using Laplacian variance analysis, rejecting images below a configurable blur threshold.
- **FR-003**: System MUST evaluate image exposure by checking luminance statistics (mean intensity and extreme pixel percentages), rejecting images that are underexposed (too dark) or overexposed (extreme glare).
- **FR-004**: System MUST intercept unreadable, truncated, or invalid image files prior to heuristic execution and return an explicit error result.
- **FR-005**: System MUST execute the entire pre-filter quality evaluation in under 500 milliseconds for standard smartphone photos.
- **FR-006**: When an image fails pre-filter validation, system MUST halt processing before invoking external vision/LLM APIs and generate user-friendly feedback indicating the specific retake reason.
- **FR-007**: System MUST provide configurable threshold parameters for sharpness variance and luminance limits so quality tolerance can be tuned per environment without code changes.
- **FR-008**: System MUST generate structured diagnostic metadata for every evaluation, recording sharpness metrics, luminance values, pass/fail status, and processing duration.

### Key Entities *(include if feature involves data)*

- **ImageQualityRequest**: Represents an incoming image payload to be evaluated, containing raw image bytes, filename/content type, and optional user/farm context.
- **QualityCheckResult**: The outcome of pre-filter evaluation, including an overall Boolean `is_acceptable` flag, primary rejection reason code (if failed), human-readable retake feedback message, and detailed numerical metrics.
- **ImageQualityMetrics**: Diagnostic measurements computed during pre-filter execution, including Laplacian variance (sharpness score), mean luminance, dark pixel percentage, bright pixel percentage, image width, image height, and total execution latency in milliseconds.
- **PreFilterConfig**: Operational settings defining numeric thresholds for minimum sharpness variance, minimum mean luminance, maximum mean luminance, and maximum allowed percentage of clipped dark/bright pixels.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of out-of-focus blurry images and extreme dark/glare photos are rejected before reaching external disease classification APIs.
- **SC-002**: Image pre-filtering completes with an average latency of under 200 milliseconds per photo, and never exceeds 500 milliseconds.
- **SC-003**: 0% external AI/vision token cost is incurred for photos rejected by the pre-filter.
- **SC-004**: 100% of pre-filter evaluations produce structured diagnostic records containing sharpness and exposure metrics for continuous quality monitoring.

## Assumptions

- **Target Image Format**: Incoming images via WhatsApp or REST API are standard formats (JPEG, PNG, WebP) up to 10MB in size.
- **Default Sharpness Threshold**: A baseline Laplacian variance threshold of 100.0 is used as default for blur detection, subject to field tuning via configuration.
- **Default Exposure Limits**: Baseline mean luminance range of 40 to 220 (on an 8-bit scale 0-255) is assumed for acceptable exposure.
- **Feedback Language**: User feedback messages follow default system language settings (French / Arabic Darija plain text tips for retaking clear crop photos).
- **Fallback Behavior**: In case of non-fatal unexpected pre-filter processing exceptions, system defaults to safe rejection with guidance to re-upload, avoiding silent execution crashes.
