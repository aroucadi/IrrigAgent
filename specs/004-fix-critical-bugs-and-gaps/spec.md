# Feature Specification: Critical Bug Fixes and Spec Alignment

**Feature Branch**: `004-fix-critical-bugs-and-gaps`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "Fix CropDoctor JPEG signature mock detection collision, resolve Darija voice teaser scope deviation, tighten Arabizi regex for clock-time shapes, align FarmProfile schema validation, eliminate silent crop catalog fallback to tomatoes for unsupported crops, and refine README safety claims."

## Clarifications

### Session 2026-07-29
- Q: How should `lookup_onssa_product()` handle unsupported crop types outside the pilot scope (tomatoes, citrus)? → A: Fail-closed. If `crop_type` is not in `ONSSA_STATIC_CATALOG`, `lookup_onssa_product()` returns `None` and uses the existing unlisted pathogen response path ("Consult an ONSSA-authorized retailer..."). No new crops are added in this pass.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reliable Crop Disease Photo Diagnosis (Priority: P1)

As a farmer taking photos of diseased crop leaves in the field, I want my submitted photos to always undergo genuine AI vision analysis rather than returning a canned mock diagnosis, so that I receive accurate, real-time advice for my specific crop condition.

**Why this priority**: Real-world JPEG photo uploads from mobile devices/WhatsApp must not be misidentified as test fixtures. Misdiagnosing real crop diseases with hardcoded mock responses compromises crop yield and user trust.

**Independent Test**: Upload a genuine JPEG photo of a plant leaf via WhatsApp and confirm the system processes the image through AI vision analysis rather than returning a static test response.

**Acceptance Scenarios**:

1. **Given** a farmer uploads a real JPEG leaf photo via WhatsApp, **When** CropDoctor processes the image, **Then** it performs dynamic vision analysis and returns diagnosis results specific to the uploaded image.
2. **Given** automated test fixtures are being executed, **When** test-specific mock payloads are sent, **Then** mock responses are triggered only by explicit test flags or exact mock byte payloads, never by standard JPEG file headers.

---

### User Story 2 - Accurate Language Detection without Clock-Time Misclassifications (Priority: P2)

As a farmer receiving or sending messages containing clock times (such as irrigation schedules like "07h00" or "19h00"), I want these numbers and time indicators to be recognized correctly as time strings rather than triggering Arabizi language detection, so that my preferred communication language remains stable.

**Why this priority**: Spurious language switching caused by routine time format strings disrupts user experience during critical daily dispatches and schedule modifications.

**Independent Test**: Send messages containing clock times (e.g., "07h00", "19h00") and confirm language preference is preserved without unwanted fallback switches.

**Acceptance Scenarios**:

1. **Given** an incoming or outgoing message contains clock-time strings formatted with hours and minutes (e.g. `\dh\d` patterns like `07h00`), **When** language detection evaluates the message, **Then** the clock-time string is excluded from Arabizi trigger patterns and does not alter user language state.

---

### User Story 3 - Voice Teaser Feature Governance & Gated Rollout (Priority: P3)

As a project stakeholder, I want the optional Darija voice teaser (TTS audio output) retained behind an explicit feature flag (`ENABLE_DARIJA_VOICE_TEASER=true`) and governed by strict demo-readiness conditions, so that optional voice polish does not compromise core farmer interaction priorities or constitution rules.

**Why this priority**: Voice output is a demo enhancement that must be sequenced after the core text loop and CropDoctor are pilot-validated. Voice input (transcription/ASR) remains strictly out of scope.

**Independent Test**: Verify feature flag `ENABLE_DARIJA_VOICE_TEASER` controls audio output synthesis, and verify that text/button messaging operates with sub-second performance independently of voice module status.

**Acceptance Scenarios**:

1. **Given** the core text recommendation loop and CropDoctor AI vision are fully working and pilot-validated, **When** `ENABLE_DARIJA_VOICE_TEASER=true` is enabled, **Then** voice output acknowledgments are synthesized and delivered via WhatsApp audio.
2. **Given** TTS audio synthesis produces an `ar-MA` audio file, **When** evaluating for demo inclusion, **Then** the audio must be subjectively verified to sound natural (not formal/robotic Arabic) and WhatsApp audio delivery (OGG/OPUS via media upload API) must be verified end-to-end to a verified sandbox recipient.
3. **Given** voice input (transcription or speech-to-text) is received, **When** processed by the system, **Then** voice input remains explicitly unhandled and out of scope for Phase 1.

---

### User Story 4 - Verified Farm Profile Data Schema Validation (Priority: P2)

As a system operator, I want incoming and updated farm profile data (phone number, location, crop type, acreage, preferred language) to be validated against an active schema before persistence, so that incomplete or invalid profile data is rejected cleanly.

**Why this priority**: Spec and implementation must align on data integrity guarantees to ensure robust error handling and accurate reporting.

**Independent Test**: Submit valid and invalid farm profile updates via WhatsApp commands and confirm invalid fields are rejected with descriptive guidance while valid profiles pass validation and persist correctly.

**Acceptance Scenarios**:

1. **Given** a farmer submits a profile update (e.g., updating crop type or acreage), **When** the system processes the update, **Then** it validates all profile fields against the active profile schema (matching actual field names: `phone_number`, `location`, `crop_type`, `acreage_hectares`, `preferred_language`) prior to saving.
2. **Given** a farmer submits malformed profile data (e.g., invalid acreage format), **When** validation executes, **Then** a helpful bilingual error response is returned without corrupting existing profile records.

---

### User Story 5 - Strict Crop Catalog Fallback Elimination & Accurate Safety Claims (Priority: P1)

As a farmer growing a crop outside the pilot's supported catalog (e.g. olives, wheat), I want CropDoctor to never return tomato/citrus chemical recommendations for my crop, so that I am not given incorrect product advice for unsupported crops.

**Why this priority**: Silently substituting tomato products for unsupported crops undermines safety intent and risks delivering harmful treatment advice to farmers.

**Independent Test**: Perform a CropDoctor triage request with `crop_type="olives"` and confirm `onssa_product_pointer` returns `None` without suggesting tomato products even on High confidence diagnoses.

**Acceptance Scenarios**:

1. **Given** a farm profile has a `crop_type` not explicitly present in `ONSSA_STATIC_CATALOG` (e.g., `"olives"`), **When** `lookup_onssa_product()` is called, **Then** it returns `None` instead of falling back to `"tomatoes"`.
2. **Given** `lookup_onssa_product()` returns `None` for an unsupported crop, **When** CropDoctor constructs the diagnosis payload, **Then** no chemical product name is included, the response directs the user to "Consult an ONSSA-authorized retailer for suitable products", and the mandatory ONSSA disclaimer is appended across all confidence tiers.
3. **Given** project documentation (`README.md`) describes CropDoctor safety features, **When** describing product recommendations, **Then** it explicitly states that lookup tables are strictly scoped to pilot crops (tomatoes, citrus) and that model confidence scores are uncalibrated self-reports.

---

### Edge Cases

- What happens when a phone uploads a JPEG photo with non-standard EXIF metadata headers?
- How does the system handle language detection when a message contains both clock times and legitimate Arabizi numerals?
- What happens when a user attempts to update a profile field with missing or out-of-bounds numerical values?
- How does CropDoctor handle a pathogen lookup for an unsupported crop with High confidence (>=75%)? (Must omit product pointer and direct user to authorized retailer).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST process all standard mobile JPEG leaf photos through AI vision diagnosis, isolating test/mock fixture behavior strictly to explicit environment/test flags or exact byte matches.
- **FR-002**: Language detection MUST ignore time-formatted strings (specifically hours-and-minutes notation like `07h00` or `19h00`) when scanning for Arabizi character/digit combinations.
- **FR-003**: System MUST gate Darija Voice Output (TTS) behind `ENABLE_DARIJA_VOICE_TEASER=true` and enforce demo readiness criteria (sequenced after core loop, audio quality check, end-to-end OGG/OPUS WhatsApp media upload validation). Voice input (transcription/ASR) MUST remain strictly out of scope.
- **FR-004**: System MUST validate all farm profile read/write representations against a unified data schema using standard field names (`phone_number`, `location`, `crop_type`, `acreage_hectares`, `preferred_language`).
- **FR-005**: All error fallbacks for CropDoctor image analysis MUST return clear, actionable user guidance requesting a clearer leaf photo rather than falling back to static diagnosis data.
- **FR-006**: `lookup_onssa_product()` MUST return `None` when `crop_type` is not listed in `ONSSA_STATIC_CATALOG` (e.g., `"olives"`), eliminating silent fallback to tomatoes.
- **FR-007**: When `lookup_onssa_product()` returns `None` due to an unsupported crop type or unlisted pathogen, the CropDoctor response MUST omit product names and recommend consulting a licensed agronomist / ONSSA retailer across all confidence tiers (including High confidence).
- **FR-008**: Documentation in `README.md` MUST accurately scope safety claims regarding ONSSA lookup tables, stating that product recommendations are restricted to verified pilot crops (tomatoes, citrus) without fabricating or substituting treatments for unsupported crops.

### Key Entities

- **FarmProfile**: Representation of farmer attributes including contact phone number (`phone_number`), geographic location/region (`location`), primary crop type (`crop_type`), field size in hectares (`acreage_hectares`), and preferred communication language (`preferred_language`).
- **CropDiagnosisRequest**: Payload containing raw photo input, sender details, and contextual metadata evaluated by AI vision services.
- **LanguageContext**: Contextual language detection object containing text tokens, script confidence, and excluded time patterns.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of real JPEG photo uploads pass through to AI vision analysis without triggering test mock diagnostic shortcuts.
- **SC-002**: 0% false-positive Arabizi language switches triggered by standard clock-time strings (`\dh\d`).
- **SC-003**: 100% alignment between schema validation definitions and actual profile data fields used during profile view/update flows.
- **SC-004**: Zero unapproved architectural deviations or unverified specification claims in active feature documentation.
- **SC-005**: 100% of triage requests for unsupported crop types (e.g. `"olives"`) return `onssa_product_pointer: None` and general retailer guidance regardless of confidence tier.

## Assumptions

- Test environments provide explicit dev/test flags or unique test tokens to distinguish mock test calls from real user traffic.
- Clock times in WhatsApp interaction flows follow common time representations (e.g. `HHhMM`, `HH:MM`).
- Profile fields updated via WhatsApp text parsing map directly to standard agricultural profile metrics (crop type, area in hectares, location, preferred language).
- `ONSSA_STATIC_CATALOG` strictly supports pilot crops (`"tomatoes"`, `"citrus"`). Unlisted crops require agronomist / retailer consultation.
