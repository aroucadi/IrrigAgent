# Feature Specification: WhatsApp 24-hour customer service window compliance for proactive daily advisory dispatch

**Feature Branch**: `015-whatsapp-24h-window-compliance`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "Create a new feature spec — do not bundle this into the P0 stabilization spec or any other in-flight spec. Feature name: WhatsApp 24-hour customer service window compliance for proactive daily advisory dispatch. Background: app/whatsapp.py's send_text_message() always sends 'type': 'text' free-form messages. Meta's Cloud API only permits free-form business-initiated messages within 24 hours of the user's last inbound message; outside that window, only pre-approved Message Templates are permitted, and the API returns error code 131026."

## Clarifications

### Session 2026-07-31

- Q: What primary Meta Template Category and Language Code should be defined for the daily irrigation advisory template submission? → A: `UTILITY` category with French (`fr`) language code and standard dynamic parameters (`{{1}}` farm name, `{{2}}` ET₀ recommendation, `{{3}}` suggested duration).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Live Verification & Window Tracking (Priority: P1)

As a maintainer, I want to track the timestamp of each user's last inbound WhatsApp message and verify whether free-form message dispatches outside the 24-hour window trigger Meta API error 131026, so that the system accurately recognizes when customer service windows expire.

**Why this priority**: Immediate live verification is time-sensitive because Meta Message Template submission and approval has real calendar lead time. Knowing the exact live behavior and tracking window state is mandatory before deploying templates.

**Independent Test**: Can be tested by simulating or observing an inbound message, calculating elapsed time, attempting a free-form dispatch past 24 hours, and confirming window expiration detection and/or Meta error 131026 response handling.

**Acceptance Scenarios**:

1. **Given** a user who sent an inbound WhatsApp message 25 hours ago, **When** a free-form message dispatch is evaluated, **Then** the system identifies that the 24-hour customer service window has expired.
2. **Given** a user who sent an inbound WhatsApp message 2 hours ago, **When** a free-form advisory message is sent, **Then** the system confirms the customer service window is open and permits free-form text transmission.
3. **Given** a free-form message sent to a recipient outside the 24-hour window, **When** Meta Cloud API returns error code 131026, **Then** the system logs the window expiration event without crashing or corrupting scheduled batch advisories.

---

### User Story 2 - Proactive Advisory Dispatch via Approved Templates (Priority: P2)

As a farm manager whose 24-hour activity window has lapsed, I want to receive proactive evening irrigation advisories via pre-approved WhatsApp Message Templates, so that I never miss critical daily irrigation recommendations even when I haven't messaged the bot recently.

**Why this priority**: Daily advisories are sent at 19:00 automatically. Farmers naturally stop replying to every single daily notification. Without template-based dispatch, silent window expiration will permanently block daily advisory delivery to passive users.

**Independent Test**: Can be tested independently by dispatching a daily advisory to a user whose 24-hour window is closed, verifying that the outgoing payload uses the registered WhatsApp Message Template format instead of free-form text, and confirming successful delivery.

**Acceptance Scenarios**:

1. **Given** a scheduled evening advisory at 19:00 for a farm manager outside the 24-hour window, **When** the advisory dispatcher runs, **Then** it automatically formats and sends the recommendation using an approved WhatsApp Message Template with required dynamic variables (e.g., farm name, ET₀ value, recommended duration).
2. **Given** an approved Message Template notification delivered to a farm manager, **When** the manager clicks or replies to the template message, **Then** a new 24-hour customer service window opens immediately for subsequent interactive conversations.

---

### User Story 3 - Automatic Window Fallback and Error Resilience (Priority: P3)

As a system operator, I want the messaging service to gracefully catch free-form transmission failures (error 131026) and automatically attempt or flag template fallback, so that transient timing desynchronizations do not cause message loss.

**Why this priority**: Ensures high operational resilience for edge cases where local window tracking differs slightly from Meta's server-side window enforcement clock.

**Independent Test**: Can be tested by sending a free-form message when server state thinks window is open, receiving error 131026 from Meta, and verifying the automated retry or fallback routing to template dispatch.

**Acceptance Scenarios**:

1. **Given** an attempted free-form message dispatch that receives Meta error code 131026, **When** error handling is triggered, **Then** the system logs the policy restriction, updates the user's local window state to expired, and initiates template-based delivery retry.
2. **Given** a failed delivery attempt due to unapproved template parameters or invalid phone state, **When** failure occurs, **Then** the failure is recorded in dispatch logs and non-blocking retry alerts are surfaced to operators.

---

### Edge Cases

- What happens when a user sends an inbound message while an outbound template dispatch is in flight? The inbound message timestamp MUST update immediately, making subsequent outbound messages eligible for free-form delivery.
- How does the system handle template variable length or formatting mismatches mandated by Meta approval policies? Dynamic variables MUST be sanitized and constrained to template character limits prior to API submission.
- What happens if Meta template approval is pending or rejected? The system MUST log an explicit configuration error and prevent silent transmission failures.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST record and persist the ISO timestamp of the last received inbound message for every registered user phone number.
- **FR-002**: System MUST evaluate whether a user is within the 24-hour customer service window before initiating free-form WhatsApp message dispatch.
- **FR-003**: System MUST support dispatching proactive daily advisories using pre-approved Meta WhatsApp Message Templates when the recipient's 24-hour customer service window is closed.
- **FR-004**: System MUST map dynamic advisory parameters (`{{1}}` farm name, `{{2}}` ET₀ recommendation, `{{3}}` suggested duration) into pre-defined French (`fr`) Meta `UTILITY` Message Template components.
- **FR-005**: System MUST detect Meta Cloud API error code 131026 (Message Undeliverable / Outside 24h Window) on outgoing requests and update local window state accordingly.
- **FR-006**: System MUST maintain compatibility with Meta WhatsApp Cloud API Sandbox environment limits (maximum 5 verified numbers).

### Key Entities *(include if feature involves data)*

- **Customer Service Window State**: Tracks user phone number, last inbound message timestamp, window active status (boolean), and last outbound dispatch mode (free-form vs. template).
- **Advisory Message Template**: Represents the pre-approved Meta template definition in `UTILITY` category with French (`fr`) language code, including template name, language code (`fr`), category (`UTILITY`), and ordered component parameters (`{{1}}`, `{{2}}`, `{{3}}`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of proactive evening advisories dispatched to users outside the 24-hour window are successfully delivered via approved Message Templates without triggering Meta error 131026.
- **SC-002**: Inbound user interactions reset customer service window tracking within 1 second of webhook receipt.
- **SC-003**: 0% message loss for proactive daily advisories across active pilot recipients regardless of inbound user engagement frequency.
- **SC-004**: Automated test suite validates window detection logic, error 131026 state transitions, and template payload construction with 100% test pass rate.

## Assumptions

- Meta WhatsApp Cloud API sandbox environment supports creating and testing approved Message Templates for verified numbers.
- Inbound webhook payloads contain accurate message timestamps (`timestamp` field in Meta webhook payload) to update user window state.
- Daily advisory generation logic remains unchanged; only the outbound transport selector (free-form vs. template) is affected by customer service window state.
