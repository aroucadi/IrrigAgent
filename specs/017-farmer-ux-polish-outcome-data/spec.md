# Feature Specification: v1.0 Farmer UX Polish, Code Quality Cleanup, and Outcome-Data Foundation

**Feature Branch**: `017-farmer-ux-polish-outcome-data`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "Create a new feature spec covering the remaining 'To Do' items from Version 1.0 in backlog.md — UX-001's non-daily-advisory portion, UX-002, UX-003, UX-004, UX-005, and SMELL-001 through SMELL-003 — plus two specific data-instrumentation additions drawn from YC partner feedback that are cheap to fold in now because they touch the same onboarding and interaction-button work already in scope. Do not duplicate or modify the already-specified CRIT-005/006/007 batch — that remains its own in-flight spec. Do not include IRRIG-046 (demo video recording) — that is a manual task, not a spec item."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Voice-Confirmation Interactive Buttons (Priority: P1)

As Hassan, when I send a voice note and the system proposes an action (such as modifying an irrigation recommendation or confirming a CropDoctor triage step), I want to confirm or cancel it by tapping an interactive button instead of typing text, so I don't hit a literacy/typing friction gate at the one step voice input was designed to make accessible.

**Why this priority**: High accessibility impact for voice-first farmers. Eliminates text-typing friction during voice-intent confirmation while ensuring low cognitive load.

**Independent Test**: Can be fully tested by sending a voice note that triggers an intent confirmation prompt and verifying that interactive "Confirm" and "Cancel" buttons are delivered and processable via button taps as well as text replies.

**Acceptance Scenarios**:

1. **Given** Hassan receives a voice intent confirmation prompt, **When** he taps the "Confirm" button, **Then** the pending intent action executes identically to typing "1", "confirm", or "approve".
2. **Given** Hassan receives a voice intent confirmation prompt, **When** he taps the "Cancel" button, **Then** the pending intent action is cancelled identically to typing "cancel" or "0".
3. **Given** Hassan sends a voice note within an active 24-hour WhatsApp messaging window, **When** the system sends the confirmation prompt, **Then** the prompt is sent as a free-form interactive button message without requiring WhatsApp template pre-approval.

---

### User Story 2 - Menu-Driven Access to Features (Priority: P1)

As Hassan, I want to reach field-boundary setup, crop-health views, and profile updates through tappable menu options from `/help`, rather than needing to type exact English command strings from memory, so these features are usable regardless of my Latin-script literacy.

**Why this priority**: Critical for accessibility and feature discoverability. Eliminates the requirement to memorize and type Latin-script slash commands like `/parcel` or `/heatmap`.

**Independent Test**: Can be tested independently by requesting `/help` and tapping any presented menu option to verify that it seamlessly enters the corresponding feature flow.

**Acceptance Scenarios**:

1. **Given** Hassan requests help or menu, **When** the menu response is sent, **Then** it presents field-boundary setup (`/parcel`), crop-health view (`/heatmap`), and profile updates (`update crop/area`) as tappable menu options (interactive buttons or structured list message).
2. **Given** Hassan taps a menu option from the help menu, **When** the selection is processed, **Then** it triggers the exact same underlying logic and flow as typing the corresponding text command (`/parcel`, `/heatmap`, or profile update).
3. **Given** an existing user who prefers typed text commands, **When** they type `/parcel` or `/heatmap` directly, **Then** the system continues to process the text command identically to previous behavior.

---

### User Story 3 - Always-Available Help/Menu Command (Priority: P1)

As Hassan, I want a simple, always-available way to see what the bot can do in my preferred language at any point in the conversation, so I am not dependent on remembering the initial onboarding greeting or waiting for the daily advisory.

**Why this priority**: Essential conversational fallback and navigation anchor across all user states.

**Independent Test**: Can be tested by sending `/help`, `help`, or `menu` from any conversation state and verifying that the menu is returned in the user's detected preferred language.

**Acceptance Scenarios**:

1. **Given** Hassan is in any conversation state, **When** he sends `/help`, `help`, or `menu`, **Then** the system recognizes the command and responds with the interactive feature menu.
2. **Given** Hassan's profile has a stored language preference (e.g., Darija/Arabizi, French, English), **When** he requests help, **Then** the menu options and descriptions are localized to his preferred language.
3. **Given** the system sends a daily advisory or CropDoctor response, **When** the message is rendered, **Then** it includes a subtle persistent closing hint (e.g., "Reply help anytime for options").

---

### User Story 4 - Product-Level Opt-Out and Opt-In Mechanism (Priority: P1)

As Hassan, I want to stop receiving daily advisory messages whenever I choose to by replying with a simple stop command, and be able to resume later, so I have full control over messaging without having to block the number manually.

**Why this priority**: Essential user privacy control and WhatsApp policy compliance. Prevents spam complaints and respects farmer autonomy.

**Independent Test**: Can be tested by opting out via `/stop`, running the daily batch recommendation job to confirm exclusion, and then opting back in via `/start`.

**Acceptance Scenarios**:

1. **Given** Hassan sends `/stop`, `stop`, `unsubscribe`, or standard French/Darija equivalents (`arreter`), **When** processed, **Then** his farm profile is updated to `opted_out: true` and an opt-out acknowledgment is sent.
2. **Given** a farm profile has `opted_out: true`, **When** the daily batch advisory job executes, **Then** that farm profile is skipped and receives no automated daily advisory message.
3. **Given** Hassan is currently opted out, **When** he sends `/start` or any explicit interaction, **Then** his profile is updated to `opted_out: false` and advisory messaging resumes.

---

### User Story 5 - Real Onboarding Data Collection & Explicit Data Consent (Priority: P1)

As a new farmer, I want to be asked for my real location, crop type, and field size during onboarding instead of silently receiving fabricated defaults, and I want clear, plain-language transparency regarding how my data is used, so my recommendations are accurate from day one and my data rights are explicitly honored.

**Why this priority**: Directly addresses the YC memo's "Data rights: Missing" audit finding and prevents inaccurate recommendations driven by silent Agadir/tomato defaults. Folding consent into the onboarding greeting rewrite costs zero additional infrastructure.

**Independent Test**: Can be tested by walking through a new farmer setup, submitting location pin, selecting crop/area, verifying explicit consent message display in the greeting, and verifying Firestore profile state without default overrides.

**Acceptance Scenarios**:

1. **Given** a new farmer registers, **When** onboarding begins, **Then** the system sequentially prompts for real location (accepting WhatsApp location pin), crop type (via tappable crop options), and approximate field size in hectares.
2. **Given** a new farmer has not yet completed onboarding, **When** daily recommendations run, **Then** temporary fallback defaults may be used, but the profile MUST be flagged as `onboarding_incomplete: true` and the daily message MUST contain a prominent reminder to complete setup.
3. **Given** a new farmer undergoes onboarding, **When** presented with the rewritten onboarding greeting, **Then** the system includes a 2-3 sentence plain-language consent statement directly explaining: data is used to generate personalized recommendations, anonymized regional data may be used to improve disease alerts, and instructions for how to opt out (referencing User Story 4).
4. **Given** a farmer completes onboarding with explicit location/crop/size, **When** saved, **Then** the profile retains real data and is NEVER silently overwritten with hardcoded defaults.

---

### User Story 6 - Outcome-Feedback Quick-Reply Capture (Priority: P2)

As the system, I want to present a quick-reply interactive button prompt asking whether a farmer actually irrigated as recommended ("Yes", "Less", "More", "Skipped"), so that we establish an empirical longitudinal dataset for real-world override rates and outcomes.

**Why this priority**: Direct implementation of the YC memo's single most concrete ask ("Did you irrigate as recommended?"). Piggybacks on the interactive button infrastructure built under CRIT-005, making it virtually zero additional cost now while preventing expensive retrospective data gaps.

**Independent Test**: Can be tested by triggering the feedback prompt during an active conversation window following an advisory, tapping an outcome quick-reply button ("Yes", "Less", "More", "Skipped"), and verifying Firestore persistence under `outcome_feedback`.

**Acceptance Scenarios**:

1. **Given** an existing daily advisory cycle, **When** the farmer interacts at the next natural touchpoint within an open messaging window, **Then** the system presents a 4-option WhatsApp interactive quick-reply button prompt with concise titles adhering to WhatsApp's 20-character title limit: "Yes" (or "Followed"), "Less", "More", "Skipped".
2. **Given** the farmer selects one of the quick-reply buttons, **When** received, **Then** the response is persisted on the corresponding Firestore Irrigation Recommendation document under `outcome_feedback`.
3. **Given** the farmer does not respond to the feedback prompt, **When** processing subsequent interactions, **Then** the system logs `no_response` gracefully and does not repeat or nag the farmer.

---

### User Story 7 - Code Quality & Robustness Cleanup (Priority: P2)

As a developer, I want to eliminate string-stripping bugs in voice parsing, resolve raster window shape mismatches in Sentinel-2 imagery, and clean up dynamic import indirections, so that runtime execution is reliable and clean.

**Why this priority**: Eliminates fragile edge cases and dynamic import overhead identified in code quality audits (SMELL-001, SMELL-002, SMELL-003).

**Independent Test**: Can be tested by running targeted unit tests against `parse_voice_intent()` formatting, Sentinel-2 band shape resolution, and `google.genai` import logic.

**Acceptance Scenarios**:

1. **Given** JSON output enclosed in markdown code fences, **When** `parse_voice_intent()` parses the content, **Then** fence removal uses precise prefix/suffix trimming (e.g., `removeprefix`/`removesuffix` or regex) without inadvertently stripping JSON structural characters.
2. **Given** Sentinel-2 band fetching in `fetch_sentinel2_bands()`, **When** windowed raster reads encounter shape rounding variations, **Then** the reader enforces exact output dimensions (`out_shape`) to guarantee shape matching across bands.
3. **Given** Google GenAI model initialization in `parse_voice_intent()`, **When** the module loads, **Then** `google.genai` is imported directly without using `importlib.import_module()`.

---

### Edge Cases

- What happens when a farmer taps a voice confirmation button after the pending intent state has expired? The system must gracefully inform the farmer that the confirmation window has expired and invite them to resend their request.
- How does the system handle an invalid location pin (e.g., coordinates outside Morocco)? The system should accept the pin, validate coordinates within supported boundaries, and notify the user if out-of-bounds fallback applies.
- What if a farmer replies with an unrecognized text option during the feedback prompt? The system should ignore non-matching feedback input and proceed with standard conversation handling without crashing.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST update `process_pending_intent_reply()` to render confirmation prompts using interactive buttons (Confirm / Cancel) within open WhatsApp conversation windows.
- **FR-002**: System MUST route button taps and text confirmation equivalents ("1", "confirm", "approve", "cancel", "0") through a single unified confirmation processing path.
- **FR-003**: System MUST expose field boundary setup (`/parcel`), crop health (`/heatmap`), and profile update actions as tappable interactive button or list menu items within the `/help` menu response.
- **FR-004**: System MUST maintain full backward compatibility for existing typed text commands (`/parcel`, `/heatmap`, `/help`, `/stop`, `/start`).
- **FR-005**: System MUST handle `/help`, `help`, and `menu` triggers universally across all conversation states in the farmer's stored preferred language.
- **FR-006**: System MUST append a standard closing hint ("Reply help anytime for options") to daily advisories and CropDoctor triage outputs.
- **FR-007**: System MUST handle `/stop`, `stop`, `unsubscribe`, and localized stop words by setting `opted_out: true` on the farm profile and acknowledging the opt-out.
- **FR-008**: System MUST exclude any farm profile with `opted_out: true` from automated daily recommendation batch runs.
- **FR-009**: System MUST allow farmers to resume daily messages by sending `/start` or any interactive message, resetting `opted_out: false`.
- **FR-010**: System MUST prompt new farmers during onboarding for location (location pin), crop type (tappable options), and field size, replacing silent hardcoded defaults.
- **FR-011**: System MUST flag profiles with incomplete setup as `onboarding_incomplete: true` and include an onboarding completion reminder in daily advisory outputs until setup is completed.
- **FR-012**: System MUST present a 2-3 sentence plain-language data-use consent statement during the onboarding greeting rewrite covering recommendation generation, anonymized regional disease tracking, and opt-out instructions.
- **FR-013**: System MUST capture irrigation compliance feedback using WhatsApp quick-reply buttons ("Yes" / "Followed", "Less", "More", "Skipped", titles <= 20 chars) within active conversation windows following an advisory and record responses in Firestore under `outcome_feedback`.
- **FR-014**: System MUST log non-responses to outcome feedback as `no_response` without re-prompting or blocking conversational flow.
- **FR-015**: System MUST replace fragile string stripping (`strip("```json")`) in `parse_voice_intent()` with exact prefix/suffix stripping or regex matching (SMELL-001).
- **FR-016**: System MUST enforce explicit array shape specifications (`out_shape`) during raster reads in `fetch_sentinel2_bands()` to resolve band shape mismatches (SMELL-002).
- **FR-017**: System MUST replace dynamic `importlib.import_module("google.genai")` calls in `parse_voice_intent()` with direct static imports (SMELL-003).

### Key Entities

- **Farm Profile**: Represents a registered farmer's profile in Firestore. Attributes include `phone_number`, `location` (latitude, longitude), `crop_type`, `field_size_ha`, `preferred_language`, `opted_out` (boolean), and `onboarding_incomplete` (boolean).
- **Irrigation Recommendation**: Represents a generated daily recommendation stored in Firestore. Attributes include `recommendation_id`, `farm_id`, `date`, `et0`, `etc`, `recommended_duration_minutes`, and `outcome_feedback` (`yes` / `followed` | `less` | `more` | `skipped` | `no_response`).
- **Pending Intent**: Represents an unconfirmed action initiated by voice or text. Attributes include `intent_id`, `farm_id`, `action_type`, `payload`, `created_at`, and `status` (`pending` | `confirmed` | `cancelled`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Voice confirmation, `/help` navigation menu, opt-out toggling, and onboarding location/crop selection are 100% reachable via interactive button taps.
- **SC-002**: 0% of newly registered profiles silently retain unacknowledged hardcoded location/crop defaults without the `onboarding_incomplete` flag and advisory reminder.
- **SC-003**: 100% of onboarding flows present the plain-language data usage consent text prior to completing profile setup.
- **SC-004**: Outcome-feedback choices ("Yes"/"Followed", "Less", "More", "Skipped") are correctly recorded against the associated Firestore Irrigation Recommendation document, with missing responses defaulting cleanly to `no_response`.
- **SC-005**: 100% pass rate for dedicated unit tests targeting SMELL-001 (markdown code fence stripping), SMELL-002 (Sentinel-2 band array shape alignment), and SMELL-003 (direct `google.genai` import).
- **SC-006**: 100% pass rate across the full automated test suite (`pytest tests/`) with zero regressions.

## Assumptions

- Interactive button messages are dispatched using the existing Meta WhatsApp Cloud API button payload structure created under CRIT-005/006/007.
- Open conversation windows (within 24 hours of a farmer's inbound message) permit free-form interactive button messages without WhatsApp template pre-approval.
- The outcome-feedback feature captures raw responses only; analytical dashboards, accuracy metrics, and recommendation model adjustments are explicitly out of scope for this spec.
- Code quality cleanup items (SMELL-001, SMELL-002, SMELL-003) preserve existing functional contracts while improving execution safety.
- CRIT-005/006/007 (WhatsApp templates, missing dependency fix, mock backdoor removal) is being developed in parallel and remains a separate in-flight specification.
