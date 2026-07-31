# Feature Specification: Hassan Persona - Proactive Irrigation Agent & Leaf Photo Triage

**Feature Branch**: `001-hassan-irrigation-agent`

**Created**: 2026-07-28 | **Updated**: 2026-07-28

**Status**: Implemented

**Input**: User prompt: "Extend spec.md to incorporate an opt-in Darija Voice Teaser module using Google Cloud Text-to-Speech (ar-MA) for the WhatsApp IrrigAgent demo while preserving deterministic sub-second text/button execution as the core production path."

## Clarifications

### Session 2026-07-28 (Audit & Gap Remediation)
- Q: Daily Proactive Advisory Dispatch Schedule → A: Option B (Previous Evening 7:00 PM GMT+1 / Africa/Casablanca). Messages are dispatched the evening prior (19:00 GMT+1) to allow calm review and approval before early-morning irrigation operations (which often begin before 06:00 AM to prevent heat evaporation loss). This schedule will be sanity-checked with pilot farmers during initial conversations.
- Q: Initial Language & Onboarding Greeting Strategy → A: Option A (Dual-language French + Darija Arabizi initial greeting, zero-friction). First onboarding message uses a hardcoded bilingual string (French + Arabizi) without forcing a menu decision tax. Subsequent messages default to French; if the farmer replies using Darija or Arabizi tokens (detected via Arabic script or word-internal Arabizi digit substitutions like 'm3ak', '7na', '9dim'), `preferred_language` in Firestore automatically flips to Darija via rule-based heuristic (no LLM call required). Standalone digits ('3'), time strings ('06h30'), and quantities ('30 min') MUST NOT trigger language flipping.
- Q: Weather & ET₀ Data Retrieval Fallback Handling → A: Option B (Short-backoff retries + Baseline Fallback). The evening batch calculation initiates at 18:45 GMT+1 ahead of the 19:00 dispatch. Retries Open-Meteo API up to 3 times with short backoff inside a single job execution. If still failing, falls back to stored ET₀ baseline and appends a clear "Estimated data" notice to the evening WhatsApp message.
- Q: Handling Option 3 ("Modify") Custom Input Logic → A: Option A (Narrow Rule-Based Regex Extraction with Raw Text Fallback). Uses two narrow regex patterns: signed duration (`[+-]\d+\s*min`) and clock time (`\d{1,2}:\d{2}` or `\d{1,2}h\d{0,2}`). Matched details return a polished acknowledgment (e.g., *"Noted: +10 min at 05:00 tomorrow"*); unmatched text falls through to raw text logging in Firestore with a generic acknowledgment (*"Noted, thank you"*). Zero LLM dependency in hero reply loop.
- Q: CropDoctor Diagnosis Structure & Exception Safety → A: 1) **Confidence-Tiered Safety & Failure Fallback**: High/Medium confidence provides primary diagnosis + ONSSA product pointer (from static lookup) + verbatim disclaimer. Low confidence (<50%) outputs cautious observation only + request for a clearer close-up photo + verbatim disclaimer (**NO product name on Low confidence**). If Gemini SDK fails, raises an exception, or encounters unreadable/non-plant photos, the system MUST fallback safely to an unreadable prompt with `confidence_score = 0.0`, omitting chemical product recommendations entirely. 2) **Static ONSSA Lookup Table**: Gemini identifies the pathogen only; treatment pointers are retrieved strictly from a hardcoded static lookup table (~10–15 common tomato/citrus pathogens mapped to ONSSA-authorized classes). Unlisted pathogens fall back to "consult a licensed agronomist or ONSSA-authorized retailer" with zero generated product names.
- Q: Recommendation Persistence on Cloud Run → A: `get_latest_recommendation_for_user` MUST query the Firestore `irrigation_recommendations` collection directly by phone number and target date/timestamp descending, rather than relying solely on in-memory process state, ensuring stateless persistence across Cloud Run container scale-to-zero lifecycles.

### Session 2026-07-28 (Darija Voice Teaser Extension)
- Q: Darija Translation & Core Logic Execution → A: Core decision, weather calculation, and diagnostic logic execute strictly in English / structured JSON to eliminate hallucination. Incoming Darija/Arabizi inputs map to normalized English schemas. Outgoing responses are formatted into Arabic-script Darija for Google TTS synthesis.
- Q: Voice Teaser Execution Architecture → A: Voice responses run as an asynchronous/non-blocking opt-in teaser controlled by `ENABLE_DARIJA_VOICE_TEASER=true`. Text responses execute deterministically in sub-second time. If TTS synthesis or WhatsApp media upload fails, text delivery completes cleanly without error.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Daily Proactive Irrigation Advisory & One-Tap WhatsApp Reply (Priority: P1)

As Hassan (a farm manager managing 5–20 hectares of crops in Morocco), I want to receive a daily proactive WhatsApp message every evening at 7:00 PM GMT+1 with a clear irrigation adjustment recommendation for tomorrow based on weather and soil water loss (evapotranspiration), so that I can review and optimize my schedule the night before without logging into a complex software dashboard or rushing before early-morning field work.

**Why this priority**: Core hero feature. Solves the primary pain point of water inefficiency and dashboard fatigue by delivering actionable advice directly on Hassan's daily communication channel at a convenient evening review time.

**Independent Test**: Can be fully tested by triggering an evening recommendation cycle for a registered farm location, delivering a WhatsApp message to Hassan's phone at 19:00 GMT+1, capturing his reply (1, 2, or 3), and verifying that the system records his choice accurately in Firestore across stateless requests.

**Acceptance Scenarios**:

1. **Given** Hassan has registered his farm location and crop type, **When** the daily decision engine runs its evening cycle (initiating at 18:45 GMT+1 for 19:00 GMT+1 dispatch) evaluating next-day weather forecast and evapotranspiration, **Then** Hassan receives a proactive WhatsApp message stating tomorrow's recommended irrigation adjustment with 3 clear reply options (1 = Approve, 2 = Skip, 3 = Modify).
2. **Given** Hassan receives the evening irrigation alert, **When** Hassan replies with `1`, **Then** the system queries Firestore for his latest recommendation, logs the approval status in Firestore, and sends a brief confirmation message ("Approved. Irrigation adjustment applied for tomorrow.").
3. **Given** Hassan receives the evening irrigation alert, **When** Hassan replies with `2`, **Then** the system queries Firestore for his latest recommendation, logs that tomorrow's adjustment is skipped, and sends a brief confirmation ("Understood, skipping tomorrow's adjustment.").
4. **Given** Hassan receives the evening irrigation alert, **When** Hassan replies with `3`, **Then** the system prompts Hassan to specify his custom adjustment; when provided, narrow regex matches extract signed duration or start time for a tailored confirmation ("Noted: +10 min at 05:00 tomorrow"), while unmatched text falls back to raw text logging in Firestore with a generic confirmation ("Noted, thank you").

---

### User Story 2 - CropDoctor Leaf Photo Disease Triage (Priority: P2)

As Hassan, when I notice unusual leaf spots or yellowing in my field, I want to capture a photo of the affected leaf and send it via WhatsApp to get an instant first-pass diagnosis, confidence level, and ONSSA-compliant treatment guidance, so that I can react early to crop diseases before they spread.

**Why this priority**: Secondary value-add feature. Provides immediate, accessible agronomic support in the field for urgent pest/disease symptoms.

**Independent Test**: Can be fully tested by sending a leaf photo via WhatsApp to the system endpoint, verifying that the diagnostic response contains a likely issue in French/Darija, a confidence indicator, static ONSSA-aligned treatment pointers, and the mandatory regulatory disclaimer. Also verified that non-plant photos or API failures yield an unreadable prompt with zero product recommendations.

**Acceptance Scenarios**:

1. **Given** Hassan sends an image of a diseased crop leaf via WhatsApp, **When** the triage vision system analyzes the image with High or Medium confidence, **Then** the system replies with a concise text diagnosis in French/Darija, a confidence rating, a treatment pointer looked up from the static ONSSA table, and the mandatory regulatory disclaimer.
2. **Given** Hassan sends a leaf image yielding Low confidence (<50%), **When** analyzed, **Then** the system replies with a cautious observation ("possible signs of discoloration, unable to confirm"), requests a clearer close-up photograph, appends the verbatim disclaimer, and **MUST NOT** include any product or chemical name.
3. **Given** Hassan receives any CropDoctor response, **Then** every single message MUST conclude with the exact verbatim disclaimer: *"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."*
4. **Given** Hassan sends an unreadable, non-plant photo, or Gemini vision API raises an exception, **When** processed, **Then** the system safely catches the exception or non-plant classification, returns an unreadable response asking Hassan to send a clear close-up photograph of the affected plant leaf, sets `confidence_score = 0.0`, and MUST NOT return a chemical diagnosis or product pointer.

---

### User Story 3 - Farm Profile Setup & Management via WhatsApp (Priority: P3)

As Hassan, I want to register and update my basic farm profile (location/coordinates, crop type, approximate acreage, preferred language) directly over WhatsApp without being forced through rigid menu steps, so that my recommendations are tailored with zero friction.

**Why this priority**: Essential prerequisite for personalized decision logic, enabling multi-user pilot testing with verified sandbox numbers.

**Independent Test**: Can be fully tested by sending onboarding registration commands over WhatsApp, verifying dual-language greeting, auto-detection of word-internal Arabizi language preference, and DB updates.

**Acceptance Scenarios**:

1. **Given** a new verified sandbox user contacts the agent for the first time, **When** they initiate conversation, **Then** the agent sends a single dual-language (French + Darija Arabizi) welcome message without forcing a language decision menu step.
2. **Given** a new user receives the initial greeting, **When** they reply in French, **Then** subsequent messages default to French.
3. **Given** a user replies containing Arabic script or word-internal Arabizi digit substitutions (`m3ak`, `7na`, `9dim`), **When** processed by the rule-based language heuristic, **Then** the system automatically updates the user's `preferred_language` attribute in Firestore to Darija without an LLM call. Standalone digits (`3`) or time strings (`06h30`) MUST NOT trigger Darija flipping.
4. **Given** Hassan is registered, **When** he requests to view or update profile parameters via WhatsApp text using a simple rule-based command pattern (e.g. "update crop tomatoes", "update area 8 ha") one field at a time, **Then** the system updates his stored farm profile in Firestore, confirms the change back to him in his preferred_language, and falls back gracefully without erroring if an unrecognized update command is received.

---

### User Story 4 - Opt-In Darija Voice Teaser Response for WhatsApp Demo (Priority: P4)

As Hassan, I want to receive an optional, natural Moroccan Arabic (Darija) voice note on WhatsApp accompanying key text confirmations when the demo voice feature is enabled, so that I can listen to recommendations hands-free while working in the field without losing fast sub-second text execution.

**Why this priority**: Incubator demo teaser feature. Provides a high-impact audio experience for live pitch demonstrations without sacrificing production-grade text reliability or speed.

**Independent Test**: Can be tested by toggling `ENABLE_DARIJA_VOICE_TEASER=true`, sending a recommendation approval or modification via WhatsApp, and confirming that: 1) text acknowledgment returns in under 1 second, 2) an asynchronous Google Cloud TTS call generates an `ar-MA` OGG OPUS voice note, 3) WhatsApp receives and plays the audio note natively. Verify that setting `ENABLE_DARIJA_VOICE_TEASER=false` disables voice synthesis completely.

**Acceptance Scenarios**:

1. **Given** `ENABLE_DARIJA_VOICE_TEASER=true` is enabled, **When** Hassan sends an irrigation response or request, **Then** the primary text confirmation is delivered deterministically in sub-second time, and an accompanying Darija voice note (synthesized via Google Cloud TTS `ar-MA` in OGG OPUS format) is transmitted asynchronously to Hassan's WhatsApp.
2. **Given** `ENABLE_DARIJA_VOICE_TEASER=false` (default), **When** Hassan interacts with the agent, **Then** the system executes purely deterministic text/button responses with zero TTS API calls or latency overhead.
3. **Given** `ENABLE_DARIJA_VOICE_TEASER=true`, **When** GCP TTS synthesis fails or WhatsApp media upload times out, **Then** the system catches the failure silently, completes the text confirmation without error, and logs the audio failure for background analysis.
4. **Given** an incoming user message contains Latin Arabizi text (e.g., *"dir liya 10 min zeyada"*), **When** voice synthesis is triggered, **Then** the translation layer maps the intent to standard Arabic-script Darija (*"دير ليا 10 دقايق زيادة"*) prior to calling GCP TTS `ar-MA`, ensuring natural phoneme generation without gibberish audio output.

---

### Edge Cases

- **Connectivity Failure / Failed Message Delivery**: If a proactive evening WhatsApp message fails to deliver, the system logs the delivery failure and retries once before flagging the profile for admin review.
- **Weather API Failure / Fallback**: If Open-Meteo API calls fail during the 18:45 batch run, the system retries 3 times with short backoff. If still failing, it uses yesterday's ET₀ baseline and appends an explicit "Estimated data" notice to the 19:00 WhatsApp advisory message.
- **Unrecognized User Reply**: If Hassan replies with text other than `1`, `2`, `3`, or a valid profile-update command, the system MUST send a gentle reminder of valid reply options (`1`/`2`/`3` or profile update syntax) rather than silently doing nothing or erroring.
- **Extreme Weather Events**: If heavy rainfall is forecasted for the next day (>= 15mm), the recommendation engine automatically defaults to recommending "Skip irrigation" (Reply 2).
- **Gemini Vision Exception / Unreadable Photo**: If Gemini vision API throws an exception or fails to detect a plant leaf, CropDoctor falls back to an unreadable state (`is_unreadable = true`, `confidence_score = 0.0`), requesting a clearer close-up leaf photo without offering chemical product names.
- **Latin Arabizi Voice Synthesis Input**: Input provided in Latin Arabizi (e.g., *"dier 10 min"*) MUST be translated to standard Arabic-script Darija before passing to GCP TTS `ar-MA` to prevent invalid phoneme rendering or unintelligible speech output.
- **TTS Synthesis or WhatsApp Media Upload Failure**: If GCP Text-to-Speech API is unreachable or WhatsApp Cloud API media upload returns an error, the voice teaser flow fails silently without disrupting or delaying the primary text confirmation message.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST proactively generate and transmit a daily irrigation advisory message over WhatsApp to registered farm managers every evening at 19:00 (7:00 PM GMT+1 / Africa/Casablanca) for next-day irrigation planning.
- **FR-002**: Daily advisory messages MUST provide 3 explicit, one-tap reply options: `1` (Approve), `2` (Skip), and `3` (Modify).
- **FR-003**: System MUST record and log the user's response (`1`, `2`, or `3`, including free-text modification details) to complete the human-in-the-loop recommendation workflow, querying Firestore directly for state persistence across Cloud Run container instances.
- **FR-004**: System MUST NOT attempt autonomous valve, solenoid, hardware, or pump control under any circumstance; all actions require human approval.
- **FR-005**: System MUST ingest daily weather forecasts and evapotranspiration (ET₀) data for each farm's registered geographic location. If Open-Meteo API is unresponsive, system MUST retry 3 times with short backoffs before falling back to baseline ET₀ data with an explicit "Estimated data" notice appended.
- **FR-006**: Decision logic MUST function deterministically using rule-based thresholds first; any optional LLM integration must serve as an upgrade rather than a dependency.
- **FR-007**: System MUST accept incoming plant leaf photos sent via WhatsApp and perform diagnostic triage using multimodal vision analysis.
- **FR-008**: System MUST append the verbatim ONSSA regulatory disclaimer to EVERY CropDoctor response: *"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."*
- **FR-009**: CropDoctor treatment suggestions MUST reference only products listed on the official ONSSA register of authorized plant protection products, retrieved strictly via deterministic lookup rather than model generation.
- **FR-010**: Messaging infrastructure MUST operate strictly within the WhatsApp Cloud API Sandbox tier, supporting up to 5 verified test recipient numbers.
- **FR-011**: System MUST strictly reject or ignore unsanctioned features, including automated physical valve actuation, payment gateways, multi-farm scheduling software, and physical soil moisture hardware sensors.
- **FR-012**: System MUST store and maintain farm profile attributes (geographic coordinates, crop type, acreage, language preference) per user identifier in Firestore.
- **FR-013**: System MUST emit a dual-language (French + Darija Arabizi) initial greeting for new users without requiring a mandatory language selection menu step.
- **FR-014**: System MUST automatically update `preferred_language` in the user's Farm Profile to Darija if Arabic script or word-internal Arabizi digit substitutions (`m3ak`, `7na`, `9dim`) are detected in incoming replies via rule-based heuristic. Standalone digits (`3`) or time strings (`06h30`) MUST NOT trigger language flipping.
- **FR-015**: System MUST use narrow rule-based regex patterns (`[+-]\d+\s*min`, `\d{1,2}:\d{2}|\d{1,2}h\d{0,2}`) to extract custom duration/start-time parameters when handling Option 3 ("Modify") text, falling back to raw text logging in Firestore for unparseable input without LLM intervention.
- **FR-016**: System MUST maintain a static lookup table (~10–15 common tomato/citrus pathogens mapped to ONSSA-authorized active-ingredient classes). CropDoctor MUST retrieve product pointers strictly from this lookup table, omitting product names entirely on Low confidence (<50%) diagnoses or unlisted pathogens to eliminate hallucination risk.
- **FR-017**: When vision model analysis encounters an exception or cannot identify plant material in an uploaded photo (unreadable/non-plant image), system MUST reply asking for a clear close-up photo of the affected leaf, set `confidence_score = 0.0`, and MUST NOT return a chemical diagnosis, product tier, or product pointer.
- **FR-018**: System MUST support viewing and updating farm profile attributes (e.g. crop type, area/acreage) via a simple rule-based free-text command pattern (e.g. "update crop tomatoes", "update area 8 ha") updating one field at a time without LLM dependency, confirming updates in user's preferred_language, and falling back gracefully on unrecognized update commands.
- **FR-019**: System MUST send a gentle reminder of valid reply options (`1` Approve, `2` Skip, `3` Modify, or profile update command syntax) when Hassan replies with text other than `1`, `2`, `3`, or a valid profile-update command, rather than failing silently or erroring.
- **FR-020**: System MUST feature dedicated unit test coverage in `tests/unit/test_weather.py` asserting that when Open-Meteo fails after 3 retries, the fallback ET₀ baseline value is used AND the outgoing WhatsApp message text explicitly contains the "Estimated data" notice.
- **FR-021**: System MUST feature dedicated unit test coverage in `tests/unit/test_decision.py` verifying that forecasted rainfall >=15mm triggers an automatic recommendation to skip irrigation (FR-005 / decision logic).
- **FR-022**: System MUST feature dedicated unit test coverage in `tests/unit/test_cropdoctor.py` verifying that multi-leaf or low-light photo inputs force Low confidence triage (<50%) omitting chemical product pointers (FR-016).
- **FR-023**: System MUST safely catch all exceptions in CropDoctor vision execution (network, auth, or parsing errors) and return the unreadable fallback prompt without returning hardcoded pathogen defaults or high confidence scores.
- **FR-024**: `get_latest_recommendation_for_user` function MUST execute a Firestore collection query on `irrigation_recommendations` filtering by `phone_number` and ordering by creation timestamp descending to guarantee stateless execution on Cloud Run.
- **FR-025**: `detect_arabizi_or_arabic` function MUST enforce strict word-internal boundary regex for Arabizi digits (`3`, `7`, `9`) requiring surrounding letters, preventing false positive language flips on numeric option replies (`3`) or clock strings (`06h30`).
- **FR-026**: System MUST implement an explicit translation and formatting abstraction layer for Moroccan Darija, ensuring core business and decision logic (irrigation volume, ET₀ calculation, CropDoctor triage) executes strictly in English / structured JSON to guarantee zero AI hallucination.
- **FR-027**: Incoming Moroccan Arabic script, Arabizi, or voice transcriptions MUST map to normalized English intent schemas before hitting core business logic.
- **FR-028**: Outgoing Darija messages destined for voice synthesis MUST be converted from English intent schemas to standard Arabic-script Darija (e.g., *"دير ليا 10 دقايق زيادة غدا مع الـ 05:00"*) for downstream TTS compatibility.
- **FR-029**: System MUST provide a lightweight Google Cloud Text-to-Speech (GCP TTS) service wrapper using `google-cloud-texttospeech` client configured with `languageCode='ar-MA'` (Moroccan Arabic) and `OGG_OPUS` audio encoding for native WhatsApp voice note playback.
- **FR-030**: System MUST implement audio file generation, temporary local/Cloud Storage staging, and Meta WhatsApp Cloud API media upload and transmission flow (`send_audio_message`).
- **FR-031**: Voice response generation MUST be controlled via an explicit feature flag (`ENABLE_DARIJA_VOICE_TEASER=true`). When `ENABLE_DARIJA_VOICE_TEASER=false`, voice note synthesis and media upload MUST be completely bypassed.
- **FR-032**: TTS synthesis and WhatsApp media upload workflows MUST execute asynchronously or non-blockingly; any TTS or upload failure MUST NOT block, delay, or cause errors in the primary text confirmation delivery loop.
- **FR-033**: System MUST handle Latin Arabizi input safely by translating text to standard Arabic script before calling GCP TTS `ar-MA`, preventing phoneme distortion or gibberish audio synthesis.

### Key Entities

- **Farm Profile**: Represents a farmer's registered operational unit. Attributes include User ID/Phone Number, Geographic Location (latitude/longitude), Crop Type (e.g., Tomatoes, Citrus), Acreage (hectares), and Preferred Language (French/Darija).
- **Irrigation Recommendation**: Represents a single daily decision cycle. Attributes include Recommendation ID, Farm Profile ID, Forecasted Weather/ET₀, Recommended Water Adjustment, Status (Pending, Approved, Skipped, Modified), Scheduled Dispatch Time (19:00 GMT+1), Data Quality Flag (Fresh vs. Estimated), Parsed Modification Payload, and User Response Timestamp.
- **Disease Triage Request**: Represents a CropDoctor interaction. Attributes include Request ID, Farm Profile ID, Image Metadata, Identified Symptom/Disease, Confidence Score (High/Medium/Low), Static ONSSA Product Pointer, and Timestamp.
- **Voice Teaser Audio Payload**: Represents a generated Moroccan Darija voice note. Attributes include Payload ID, Target Phone Number, Arabic-Script Darija Source Text, Audio Encoding (`OGG_OPUS`), Temporary Staging Path, WhatsApp Media ID, Generation Time (ms), and Status (Queued, Synthesized, Uploaded, Delivered, Failed).

## Post-Selection Milestones (Post-MVP Roadmap)

- **M6 (Infrastructure Roadmap)**: Declarative Terraform IaC (`infra/` module) and automated GitHub Actions CI/CD deployment pipeline are archived post-selection assets. v1 pilot application deployment strictly uses GCP Cloud Run CLI (`gcloud run deploy`) per PRD Section 15.11.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: **100% End-to-End Delivery**: Proactive irrigation recommendations are successfully delivered to verified WhatsApp sandbox recipient numbers every evening at 19:00 (Africa/Casablanca).
- **SC-002**: **Rapid Decision Time**: Farmers can approve, skip, or modify an irrigation decision in under 15 seconds via WhatsApp one-tap reply (Pilot User Feedback KPI; software performance SLA is <2s webhook response).
- **SC-003**: **100% Regulatory & Safety Compliance**: 100% of CropDoctor diagnostic replies include the verbatim ONSSA disclaimer, 0% of Low-confidence or fallback exception replies contain chemical product names, and 0 false-positive diagnoses occur on non-plant photos.
- **SC-004**: **Stateless Cloud Run Reliability**: 100% of user one-tap replies (`1`, `2`, `3`) successfully update recommendation records in Firestore when executing on stateless Cloud Run containers.
- **SC-005**: **Zero Unsanctioned Scope Leakage**: 0 instances of automated hardware control, payment processing, or unapproved features introduced into the system.
- **SC-006**: **Sub-Second Core Latency**: 100% of primary text/button response webhook flows complete in under 1 second regardless of whether the voice teaser feature flag is enabled.
- **SC-007**: **Fast Voice Teaser Synthesis SLA**: Outgoing Darija text is converted to OGG OPUS via Google Cloud TTS (`ar-MA`) in under 2.5 seconds.
- **SC-008**: **Native WhatsApp Audio Playback**: 100% of generated OGG OPUS voice notes play natively on WhatsApp without codec or format rendering errors.

## Assumptions

- **Target User Persona**: Farm managers own a smartphone with active WhatsApp access and basic literacy in French or Latinized Darija text.
- **Connectivity**: Farmers have periodic cellular/data connectivity to receive WhatsApp messages during the evening.
- **Evening Review Habit**: 7:00 PM (Africa/Casablanca) previous evening dispatch aligns with early-morning irrigation schedules (pre-06:00 AM starts) and evening WhatsApp review habits.
- **Zero-Friction Language Strategy**: Dual-language initial greeting avoids menu friction; word-internal Arabizi digit heuristic (`m3ak`, `7na`, `9dim`) handles language preference auto-detection without LLM overhead.
- **Narrow Regex Parser**: Narrow duration/time regex handles Option 3 modification acknowledgments for demo polish; raw text logging fallback ensures unparseable input never causes errors.
- **Static ONSSA Lookup Table**: Hardcoded dictionary of ~10–15 pilot crop pathogens to ONSSA classes completely eliminates AI product hallucination risk while satisfying v1 scope bounds.
- **Sandbox Boundary**: Up to 5 verified phone numbers are sufficient for initial pilot validation and StartGate incubator demo.
- **Deployment Model**: Pilot application deployment strictly follows PRD Section 15.11 (`gcloud run deploy irrigagent --source . --region europe-west1 --set-env-vars ...`).
- **GCP TTS Service Availability**: Google Cloud Text-to-Speech API credentials and `ar-MA` voice models are configured and accessible when `ENABLE_DARIJA_VOICE_TEASER=true`.
- **Asynchronous Voice Teaser Isolation**: Voice teaser processing runs non-blockingly as an opt-in demo enhancement alongside deterministic text/button execution.
