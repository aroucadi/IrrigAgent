# Feature Specification: Pre-Conversation Production Readiness Verification

**Feature Branch**: `019-production-readiness-verification`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "Create a new feature spec — this is verification/hardening work, not new farmer-facing functionality. Do not add any new feature, message, or data field as part of this spec. The goal is confidence that everything claimed 'implemented' in the v1.0 sprint actually works end-to-end against real WhatsApp infrastructure, ahead of an external stakeholder conversation next week."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Confirm the 24-Hour Window / Template Behavior with Real Evidence (Priority: P1)

As the maintainer, I want documented, real evidence of whether daily advisory dispatches via WhatsApp Cloud API successfully deliver outside an active 24-hour messaging window, so that I can speak with confidence regarding product reliability during upcoming stakeholder discussions.

**Why this priority**: High risk of undisclosed failure. In previous development cycles, functionality marked "complete" was later found to rely on synthetic data or mocks. Validating 24-hour window compliance against live Meta WhatsApp infrastructure is critical to ensure real farmers receive proactive daily advisories.

**Independent Test**: Can be tested by executing a live daily advisory job run targeting a real verified WhatsApp sandbox number that has had zero inbound activity for over 25 hours, recording the raw API request and response payload.

**Acceptance Scenarios**:

1. **Given** CRIT-005's live 24-hour verification test status is unconfirmed, **When** a manual verification run is conducted against a real verified WhatsApp sandbox number following a 25+ hour period of silence, **Then** the actual Meta API response is captured, evaluated, and documented with exact timestamps.
2. **Given** template-based messaging was implemented for daily advisory dispatch, **When** the automated daily job runs against a real registered farm profile outside the 24-hour window, **Then** a template message successfully delivers to the device (or an explicit Meta API error such as 131026 is returned and recorded).
3. **Given** any delivery failure or unapproved Meta template status is identified, **When** the verification test concludes, **Then** the finding is immediately flagged as a high-priority discovery in the verification log rather than being fixed silently or ignored.

---

### User Story 2 - End-to-End Interactive Button Round-Trip Verification (Priority: P1)

As the maintainer, I want to verify that tapping interactive buttons (Approve, Skip, Modify, Confirm, Cancel) on a physical WhatsApp client correctly triggers the exact downstream workflow and Firestore state mutations as typing manual replies, confirming the literacy-accessibility solution works in live practice.

**Why this priority**: Interactive buttons are the primary accessibility interface for low-literacy farmers. Verification must confirm that button payload callbacks correctly route through webhook handlers to state transitions in Firestore without relying on simulated webhook events.

**Independent Test**: Can be tested by receiving live daily advisories and voice-note confirmation prompts on a physical device, tapping each button option sequentially across test runs, and asserting the resulting state in Firestore and outgoing acknowledgment messages.

**Acceptance Scenarios**:

1. **Given** a real daily advisory message received on a physical sandbox device, **When** the user taps "Approve", **Then** the system records the recommendation approval in Firestore and dispatches the confirmation message to the recipient.
2. **Given** a real daily advisory message received on a physical sandbox device, **When** the user taps "Skip", **Then** the system updates the daily action status to skipped in Firestore without triggering irrigation duration adjustments.
3. **Given** a real daily advisory message received on a physical sandbox device, **When** the user taps "Modify", **Then** the system prompts the user for modified runtime input as expected.
4. **Given** a voice-note advice confirmation prompt received on a physical device, **When** the user taps "Confirm" or "Cancel", **Then** the corresponding approval or cancellation flow completes and persists to Firestore.

---

### User Story 3 - Opt-Out and Help/Menu Real-Device Verification (Priority: P2)

As the maintainer, I want to verify that keyword commands (`/stop` and `/help`) function correctly on real WhatsApp sandbox devices, ensuring farmer opt-outs are respected in batch runs and guidance menus render properly.

**Why this priority**: Essential governance and user control functionality. Ensures farmers can control their subscription state and access support instructions without crashing or experiencing formatted payload errors.

**Independent Test**: Can be tested by sending `/stop` and `/help` from a real sandbox device and observing batch execution filtering and menu output rendering.

**Acceptance Scenarios**:

1. **Given** a registered farm profile on a real sandbox number, **When** the user sends `/stop`, **Then** the system marks the profile as opted out in Firestore AND the next daily batch execution explicitly skips sending messages to this farm.
2. **Given** a registered farm profile on a real sandbox number, **When** the user sends `/help`, **Then** the system responds with the full menu text rendered clearly in the expected language (e.g., Darija/Arabic/French).

---

### User Story 4 - Dashboard Sanity Check Against Real Firestore Data (Priority: P2)

As the maintainer, I want to run the engagement dashboard script against current real Firestore production data to confirm it produces an accurate, honestly-labeled summary without crashing or interpolating data.

**Why this priority**: Prevents reporting misleading metrics to external stakeholders. Ensures the dashboard reflects actual pilot usage metrics with clear qualification of small sample sizes.

**Independent Test**: Can be tested by executing `python scripts/generate_engagement_report.py` against live Firestore data and validating the output structure and label indicators.

**Acceptance Scenarios**:

1. **Given** the current live Firestore dataset containing a small number of farm profiles, **When** the engagement report generator script is executed, **Then** the output displays an explicit "early/directional data" label acknowledging the sample size.
2. **Given** real Firestore records, **When** metrics are calculated by the report generator, **Then** zero fabricated, simulated, or interpolated figures appear in the output report.

---

### Edge Cases

- What happens if Meta WhatsApp API returns error code 131026 (Message undeliverable outside 24h window without approved template)? The exact raw payload must be recorded in the verification log and flagged immediately as a critical blocking finding.
- What happens if a button tap callback arrives after a long delay? The webhook handler must process the button payload idempotently without crashing or resetting farm state incorrectly.
- What happens if a farm profile sends `/stop` mid-batch run? The batch runner must evaluate opt-out status at dispatch time to prevent sending messages to opted-out profiles.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Verification execution MUST use real WhatsApp Cloud API sandbox numbers and physical/client device interactions rather than mock test fixtures or synthetic webhooks.
- **FR-002**: The 24-hour message window compliance test MUST verify daily advisory dispatch against a farm profile that has had zero inbound activity for at least 25 consecutive hours.
- **FR-003**: All verification activities MUST record exact execution timestamps, target phone number identifiers (anonymized/redacted if necessary), raw API request payloads, and raw API response payloads into a single markdown verification log (`verification_log.md`).
- **FR-004**: Verification MUST test all three interactive daily advisory buttons (`Approve`, `Skip`, `Modify`) and both voice-note confirmation buttons (`Confirm`, `Cancel`) individually on real devices, verifying resulting state changes in Firestore.
- **FR-005**: Verification MUST test command keywords (`/stop` and `/help`) on real devices, confirming `/stop` excludes the farm from subsequent daily batch job dispatches and `/help` returns a properly localized menu response.
- **FR-006**: The engagement dashboard tool (`scripts/generate_engagement_report.py`) MUST be run against live Firestore data, ensuring "early/directional data" warning banners trigger appropriately and outputs contain strictly empirical data.
- **FR-007**: Discovered defects or failures during verification MUST be documented in the verification log as standalone findings and MUST NOT be fixed inline within this verification scope.

### Key Entities *(include if feature involves data)*

- **Verification Log**: A structured markdown record containing test execution details, timestamps, target profiles, raw API responses, Firestore verification checks, and pass/fail determinations.
- **Farm Profile**: Live Firestore document containing farm location, crop type, opt-out status, and message window timestamps used during verification.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A comprehensive verification log (`verification_log.md`) exists with real timestamps, raw Meta API responses, and Firestore state assertions covering all four user stories.
- **SC-002**: 100% of discovered bugs or infrastructure gaps are cataloged as distinct, separate findings with zero inline code modifications made under this verification spec.
- **SC-003**: The maintainer possesses verified, empirical evidence (timestamps, API logs, screenshot evidence where applicable) validating all v1.0 claims prior to external stakeholder meetings.

## Non-Goals

- **NO New Features**: Does NOT add any new user-facing functionality, message types, or database fields.
- **NO Code Changes to Decision Engine or AI Models**: Does NOT modify `app/decision.py`, CropDoctor triage models, or Sentinel satellite data integration modules.
- **NO Inline Bug Fixing**: Does NOT attempt to resolve bugs or infrastructure errors discovered during testing within this specification scope. Any fix requires a separate, dedicated specification.
- **NO New Automated Test Suite**: Does NOT build or add automated unit/integration test suites; verification is strictly manual against real physical infrastructure.

## Assumptions

- Access to Meta WhatsApp Cloud API developer portal and configured sandbox test numbers is available.
- Real sandbox test device is available to send and receive WhatsApp messages and tap interactive buttons.
- Firestore database contains active test farm profiles or permits creating temporary real test profiles for verification.
- Python runtime environment has valid GCP credentials to query Firestore and run `scripts/generate_engagement_report.py`.
