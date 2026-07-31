# Feature Specification: Pre-Demo Critical Fixes — Template-Based Daily Advisory, Dependency Fix, Mock-ID Backdoor Closure

**Feature Branch**: `016-pre-demo-critical-fixes`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "Create a new feature spec covering CRIT-005, CRIT-006, and CRIT-007 from backlog.md as a single pre-demo stabilization batch — these three are grouped because all three block trusting a live demo, not because they share implementation. Do not include UX-001, UX-002, UX-005, or any other backlog item in this pass..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Live Verification of the 24-Hour Window Restriction (Priority: P1)

As the system maintainer, I want factual confirmation of whether WhatsApp's 24-hour customer service window actually blocks free-form text messages to sandbox/test recipient numbers, before designing and submitting a Message Template based on an assumption.

**Why this priority**: Confirms the exact runtime behavior of Meta Graph API for out-of-window messages (`131026` error code) under live sandbox conditions so that template submission turnaround time is spent on a verified requirement rather than an unverified assumption.

**Independent Test**: Can be tested independently by taking a verified test phone number, sending an initial message to establish a window, waiting 25+ hours with zero inbound traffic, and triggering a free-form message dispatch (`send_text_message`) to capture the Graph API response payload and error code.

**Acceptance Scenarios**:

1. **Given** a test phone number that has sent no inbound WhatsApp messages for 25+ hours, **When** the system attempts to send an unprompted free-form text advisory via `send_text_message()`, **Then** the Meta Graph API response returns an error status with Meta error code `131026` ("Message outside the 24-hour window"), and this exact payload with timestamps is documented in `specs/016-pre-demo-critical-fixes/research.md`.
2. **Given** the 25-hour wait period is actively running, **When** developers work on template scaffolding, **Then** function signatures, payload builders, and unit tests using mocked responses may proceed in parallel, but the final template submission payload to Meta is locked only after verification (or a documented time-boxed assumption).

---

### User Story 2 - Unified Message Template with Embedded Quick Reply Buttons for Daily Advisory (Priority: P1)

As Hassan, I want to receive my daily irrigation advisory reliably every evening regardless of whether I replied to yesterday's message, with tappable Approve/Skip/Modify quick reply options built directly into that message, so the advisory always arrives and I don't have to type digits to respond.

**Why this priority**: WhatsApp standalone Interactive Messages (free-form buttons) are subject to the same 24-hour window restriction as plain text. Meta Message Templates allow embedding up to 3 Quick Reply buttons into the approved template component. Combining template delivery and quick reply buttons into a single template submission resolves both CRIT-005 and the daily advisory portion of UX-001 without violating Meta Cloud API architectural constraints.

**Independent Test**: Can be independently tested by triggering the daily job (`POST /jobs/daily-recommendations`) and asserting it dispatches a `"type": "template"` payload with correctly mapped variable parameters and embedded button component, and verifying that clicking a quick reply button sends a `button_reply` webhook payload that resolves to the exact same action state as typing digit `"1"`, `"2"`, or `"3"`.

**Acceptance Scenarios**:

1. **Given** an active farm profile and scheduled daily advisory job execution, **When** `/jobs/daily-recommendations` runs, **Then** the system dispatches outbound advisories using `send_template_message()` with template name `irrigagent_daily_advisory`, language `fr`, parameterized ETc recommendation variables (`{{1}}`, `{{2}}`), and 3 embedded Quick Reply buttons (`Approve`, `Skip`, `Modify`).
2. **Given** a farmer receives the daily advisory template with Quick Reply buttons, **When** the farmer taps "Approve" (button ID `btn_approve` / `1`), **Then** `extract_incoming_message()` parses the webhook `button_reply` payload into an internal action matching typed `"1"` ("approved"), updating the recommendation status seamlessly.
3. **Given** a farmer taps "Modify" (button ID `btn_modify` / `3`), **When** the button click webhook is processed, **Then** the system prompts the farmer for specific adjustment details ("Reply with your preferred adjustment (e.g. '+10 min at 05:00')"), following the exact downstream flow as typed `"3"`.
4. **Given** non-daily-advisory messages (replies to user messages, CropDoctor photo triage responses, profile updates), **When** dispatched, **Then** they continue using `send_text_message()` within the open 24-hour window without modification.

---

### User Story 3 - Graceful Handling of Template Send Failures (Priority: P2)

As the system, if a template message send is rejected (e.g., template not yet approved, quality rating issue, or Graph API rejection), I want the failure logged clearly with the affected farm profile and reason, so a missing daily message is instantly visible and debuggable.

**Why this priority**: Ensures operational visibility and auditability when outbound daily advisories fail, preventing silent dropping of messages.

**Independent Test**: Can be tested by mocking an error response from `send_template_message()` and verifying that the daily job logs the farm profile phone number, failure reason, and timestamp without breaking execution for other active profiles.

**Acceptance Scenarios**:

1. **Given** a template dispatch call that returns a Meta Graph API error or HTTP error, **When** `/jobs/daily-recommendations` executes, **Then** the system catches the exception, increments `failed_count`, logs a structured error containing phone number, error code/reason, and ISO timestamp, and continues processing remaining profiles.

---

### User Story 4 - Fix Missing Dependency Blocking Clean Installation (Priority: P1)

As a developer or system operator, I want the application to boot successfully from a clean `pip install -r requirements.txt`, so that Docker container builds and fresh environment deployments never crash on missing dependencies.

**Why this priority**: `app/main.py` uses FastAPI `UploadFile = File(...)` for the `/cropdoctor/prefilter` endpoint, which requires `python-multipart`. Its absence from `requirements.txt` is an immediate deployment and build blocker (CRIT-006).

**Independent Test**: Can be tested independently by creating a fresh Python virtual environment, running `pip install -r requirements.txt`, and executing `python -c "import app.main"` to verify clean module import without ImportError.

**Acceptance Scenarios**:

1. **Given** a fresh virtual environment, **When** `pip install -r requirements.txt` is executed, **Then** `python-multipart` (version compatible with pinned `fastapi==0.115.0`) is installed.
2. **Given** the dependencies are installed, **When** `app.main` is imported or Uvicorn boots the app, **Then** the application starts cleanly with zero missing module exceptions.

---

### User Story 5 - Close the Mock-Media-ID Production Backdoor (Priority: P1)

As the system, if a real incoming photo or voice note webhook event is missing its media ID after payload extraction, I want to fail explicitly and request a resend from the farmer, rather than silently substituting a fallback string that the media-download layer treats as a test fixture.

**Why this priority**: `app/main.py` previously constructed `image_id or "mock_img_1"` and `audio_id or "mock_audio_1"`. If webhook extraction missed a media ID on a genuine payload, the system silently processed canned test bytes (`b"fake_high_confidence"`). Removing this backdoor (CRIT-007) ensures real production edge cases never execute mock fixtures.

**Independent Test**: Can be tested by passing a webhook payload containing an `image` or `audio` event type but missing the media `id` field to `receive_webhook`, asserting that the system logs an internal failure and sends a friendly retry text to Hassan, rather than returning a mock CropDoctor triage or mock ASR response.

**Acceptance Scenarios**:

1. **Given** an incoming webhook payload for an image or voice event where `extract_incoming_message()` returns `None` for `image_id` / `audio_id`, **When** `receive_webhook` processes the payload, **Then** the system logs the failure internally (sender phone, timestamp, raw payload shape), sends a friendly farmer-facing message (*"🍃 Nous n'avons pas pu lire votre photo/vocal. Merci de la renvoyer."*), and exits without invoking CropDoctor triage or ASR processing.
2. **Given** unit test suites using explicit mock fixtures (where `media_id` explicitly starts with `"mock_"`), **When** `download_media()` is called, **Then** `download_media()`'s mock-detection check (`media_id.startswith("mock_")`) continues to work as expected for isolated test fixtures.

---

### Edge Cases

- What happens if Meta template approval takes longer than expected? The system daily job logs template unapproved status cleanly per User Story 3 while sandbox tests validate the constructed template payload structure using mock handlers.
- What happens if a farmer sends a text message while a voice intent or template quick-reply confirmation is pending? Numeric replies (`1`, `2`, `3`) and button click postbacks (`btn_approve`, `btn_skip`, `btn_modify`) resolve to identical internal status mutations (`approved`, `skipped`, `modified`).
- What happens if a farmer taps a Quick Reply button outside the daily advisory flow? Webhook payload parsing extracts `button_reply.id` into the existing command/text router seamlessly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support sending Meta WhatsApp Cloud API Message Templates via `send_template_message(to, template_name, language_code, components)` in `app/whatsapp.py`.
- **FR-002**: The daily recommendation job (`POST /jobs/daily-recommendations`) MUST dispatch proactive daily advisories using `send_template_message()` with template name `irrigagent_daily_advisory`, language code `fr`, parameterized ETc weather/recommendation values, and embedded Quick Reply buttons (`Approve`, `Skip`, `Modify`).
- **FR-003**: `extract_incoming_message()` in `app/whatsapp.py` MUST parse Meta webhook `interactive` / `button_reply` postback payloads and map button IDs (`btn_approve`, `btn_skip`, `btn_modify` or `"1"`, `"2"`, `"3"`) to the exact same internal action outcomes as typed numeric text replies.
- **FR-004**: The system MUST log explicit structured error details (farm phone number, failure reason, ISO timestamp) whenever a template dispatch call fails or is rejected by Meta Graph API.
- **FR-005**: `requirements.txt` MUST include `python-multipart>=0.0.12` to ensure clean environment installation and FastAPI `UploadFile` endpoint execution.
- **FR-006**: `app/main.py` MUST NOT use `"mock_img_1"` or `"mock_audio_1"` as default fallback strings for incoming media webhook payloads.
- **FR-007**: When an incoming photo or voice note message event lacks a valid media ID, `app/main.py` MUST log the extraction failure internally and send a friendly, farmer-facing retry request message without surfacing raw error stack traces or executing mock data logic.
- **FR-008**: Outbound replies to farmer-initiated messages (e.g. voice responses, CropDoctor leaf diagnostics, profile updates) MUST continue using standard free-form text messaging (`send_text_message()`) within the open 24-hour customer service window.

### Key Entities

- **Message Template Payload**: Represents the structured JSON body sent to Meta Graph API containing `messaging_product: "whatsapp"`, `recipient_type: "individual"`, `to`, `type: "template"`, and `template: { name, language, components }`.
- **Quick Reply Button Component**: Template component array defining buttons with `type: "button"`, `sub_type: "quick_reply"`, `index`, and parameters.
- **Webhook Button Reply Postback**: Inbound Meta payload under `entry[0].changes[0].value.messages[0].interactive.button_reply` containing `id` and `title`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Factual verification of the 24-hour window restriction is documented in `research.md` with exact ISO timestamps and Graph API response payload (error code `131026`).
- **SC-002**: Daily advisory job dispatches via `send_template_message()` using `"type": "template"` payload shape with parameterized slots and 3 Quick Reply buttons, verified by automated unit and integration tests.
- **SC-003**: Tapping a Quick Reply button (`Approve`/`Skip`/`Modify`) and typing a digit (`1`/`2`/`3`) both produce identical state changes in `save_recommendation()`, verified by unified assertion tests.
- **SC-004**: Clean virtual environment installation using `pip install -r requirements.txt` and app import succeeds with zero missing dependency errors.
- **SC-005**: An incoming image or audio event with a missing media ID triggers an internal log entry and a polite farmer-facing retry message, failing closed without executing mock fixtures or raw exceptions.
- **SC-006**: 100% of existing unit and integration test suite passes with zero regressions.

## Assumptions

- Sandbox test phone number is available for the 25-hour out-of-window verification test.
- Meta Message Template `irrigagent_daily_advisory` category is "UTILITY".
- The 24-hour customer service window restriction applies strictly to business-initiated proactive messages (daily advisory job), not to inbound user-initiated response flows.
- Non-goals: UX-001 (voice note / CropDoctor interactive buttons), UX-002 (typed `/parcel` and `/heatmap` command buttons), and UX-005 (onboarding defaults) are explicitly deferred to subsequent spec passes.
