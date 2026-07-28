# Feature Specification: Hassan Persona - Proactive Irrigation Agent & Leaf Photo Triage

**Feature Branch**: `001-hassan-irrigation-agent`

**Created**: 2026-07-28

**Status**: Complete

**Input**: User description: "Read PRD.md and draft our formal spec artifact for the Hassan persona (proactive irrigation agent + light photo triage)."

## Clarifications

### Session 2026-07-28
- Q: Daily Proactive Advisory Dispatch Schedule → A: Option B (Previous Evening 7:00 PM GMT+1). Messages are dispatched the evening prior (19:00 GMT+1) to allow calm review and approval before early-morning irrigation operations (which often begin before 06:00 AM to prevent heat evaporation loss). This schedule will be sanity-checked with pilot farmers during initial conversations.
- Q: Initial Language & Onboarding Greeting Strategy → A: Option A (Dual-language French + Darija Arabizi initial greeting, zero-friction). First onboarding message uses a hardcoded bilingual string (French + Arabizi) without forcing a menu decision tax. Subsequent messages default to French; if the farmer replies using Darija or Arabizi tokens (detected via Arabic script or common Arabizi digit substitutions '3','7','9'), `preferred_language` in Firestore automatically flips to Darija via rule-based heuristic (no LLM call required).
- Q: Weather & ET₀ Data Retrieval Fallback Handling → A: Option B (Short-backoff retries + Previous Day Baseline Fallback). The evening batch calculation initiates at 18:45 GMT+1 ahead of the 19:00 dispatch. Retries Open-Meteo API up to 3 times with short backoff (10s / 30s / 60s) inside a single job execution. If still failing, falls back to yesterday's ET₀ baseline and appends a clear "Estimated data" notice to the evening WhatsApp message.
- Q: Handling Option 3 ("Modify") Custom Input Logic → A: Option A (Narrow Rule-Based Regex Extraction with Raw Text Fallback). Uses two narrow regex patterns: signed duration (`[+-]\d+\s*min`) and clock time (`\d{1,2}:\d{2}` or `\d{1,2}h\d{0,2}`). Matched details return a polished acknowledgment (e.g., *"Noted: +10 min at 05:00 tomorrow"*); unmatched text falls through to raw text logging in Firestore with a generic acknowledgment (*"Noted, thank you"*). Zero LLM dependency in hero reply loop.
- Q: CropDoctor Diagnosis Structure & Low-Confidence Fallback → A: Option A with two regulatory & safety refinements. 1) **Confidence-Tiered Behavior**: High/Medium confidence provides primary diagnosis + ONSSA product pointer (from static lookup) + verbatim disclaimer. Low confidence (<50%) outputs cautious observation only ("possible signs of discoloration, unable to confirm") + request for a clearer close-up photo + verbatim disclaimer (**NO product name on Low confidence**). 2) **Static ONSSA Lookup Table**: Gemini identifies the pathogen only; treatment pointers are retrieved strictly from a hardcoded static lookup table (~10–15 common tomato/citrus pathogens mapped to ONSSA-authorized classes). Unlisted pathogens fall back to "consult a licensed agronomist or ONSSA-authorized retailer" with zero generated product names.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Daily Proactive Irrigation Advisory & One-Tap WhatsApp Reply (Priority: P1)

As Hassan (a farm manager managing 5–20 hectares of crops in Morocco), I want to receive a daily proactive WhatsApp message every evening at 7:00 PM GMT+1 with a clear irrigation adjustment recommendation for tomorrow based on weather and soil water loss (evapotranspiration), so that I can review and optimize my schedule the night before without logging into a complex software dashboard or rushing before early-morning field work.

**Why this priority**: Core hero feature. Solves the primary pain point of water inefficiency and dashboard fatigue by delivering actionable advice directly on Hassan's daily communication channel at a convenient evening review time.

**Independent Test**: Can be fully tested by triggering an evening recommendation cycle for a registered farm location, delivering a WhatsApp message to Hassan's phone at 19:00 GMT+1, capturing his reply (1, 2, or 3), and verifying that the system records his choice accurately for next-day execution.

**Acceptance Scenarios**:

1. **Given** Hassan has registered his farm location and crop type, **When** the daily decision engine runs its evening cycle (initiating at 18:45 GMT+1 for 19:00 GMT+1 dispatch) evaluating next-day weather forecast and evapotranspiration, **Then** Hassan receives a proactive WhatsApp message stating tomorrow's recommended irrigation adjustment with 3 clear reply options (1 = Approve, 2 = Skip, 3 = Modify).
2. **Given** Hassan receives the evening irrigation alert, **When** Hassan replies with `1`, **Then** the system logs the approval for tomorrow's schedule and sends a brief confirmation message ("Approved. Irrigation adjustment applied for tomorrow.").
3. **Given** Hassan receives the evening irrigation alert, **When** Hassan replies with `2`, **Then** the system logs that tomorrow's adjustment is skipped and sends a brief confirmation ("Understood, skipping tomorrow's adjustment.").
4. **Given** Hassan receives the evening irrigation alert, **When** Hassan replies with `3`, **Then** the system prompts Hassan to specify his custom adjustment; when provided, narrow regex matches extract signed duration or start time for a tailored confirmation ("Noted: +10 min at 05:00 tomorrow"), while unmatched text falls back to raw text logging with a generic confirmation ("Noted, thank you").

---

### User Story 2 - CropDoctor Leaf Photo Disease Triage (Priority: P2)

As Hassan, when I notice unusual leaf spots or yellowing in my field, I want to capture a photo of the affected leaf and send it via WhatsApp to get an instant first-pass diagnosis, confidence level, and ONSSA-compliant treatment guidance, so that I can react early to crop diseases before they spread.

**Why this priority**: Secondary value-add feature. Provides immediate, accessible agronomic support in the field for urgent pest/disease symptoms.

**Independent Test**: Can be fully tested by sending a leaf photo via WhatsApp to the system endpoint, verifying that the diagnostic response contains a likely issue in French/Darija, a confidence indicator, static ONSSA-aligned treatment pointers, and the mandatory regulatory disclaimer.

**Acceptance Scenarios**:

1. **Given** Hassan sends an image of a diseased crop leaf via WhatsApp, **When** the triage vision system analyzes the image with High or Medium confidence, **Then** the system replies with a concise text diagnosis in French/Darija, a confidence rating, a treatment pointer looked up from the static ONSSA table, and the mandatory regulatory disclaimer.
2. **Given** Hassan sends a leaf image yielding Low confidence (<50%), **When** analyzed, **Then** the system replies with a cautious observation ("possible signs of discoloration, unable to confirm"), requests a clearer close-up photograph, appends the verbatim disclaimer, and **MUST NOT** include any product or chemical name.
3. **Given** Hassan receives any CropDoctor response, **Then** every single message MUST conclude with the exact verbatim disclaimer: *"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."*
4. **Given** Hassan sends an unreadable or non-plant photo, **When** analyzed, **Then** the system politely prompts Hassan to send a clear, close-up photograph of the affected plant leaf.

---

### User Story 3 - Farm Profile Setup & Management via WhatsApp (Priority: P3)

As Hassan, I want to register and update my basic farm profile (location/coordinates, crop type, approximate acreage, preferred language) directly over WhatsApp without being forced through rigid menu steps, so that my recommendations are tailored with zero friction.

**Why this priority**: Essential prerequisite for personalized decision logic, enabling multi-user pilot testing with verified sandbox numbers.

**Independent Test**: Can be fully tested by sending onboarding registration commands over WhatsApp, verifying dual-language greeting, auto-detection of language preference, and DB updates.

**Acceptance Scenarios**:

1. **Given** a new verified sandbox user contacts the agent for the first time, **When** they initiate conversation, **Then** the agent sends a single dual-language (French + Darija Arabizi) welcome message without forcing a language decision menu step.
2. **Given** a new user receives the initial greeting, **When** they reply in French, **Then** subsequent messages default to French.
3. **Given** a user replies containing Arabic script or common Arabizi digit substitutions (`3`, `7`, `9`), **When** processed by the rule-based language heuristic, **Then** the system automatically updates the user's `preferred_language` attribute in Firestore to Darija without an LLM call.
4. **Given** Hassan is registered, **When** he requests to view or update profile parameters via WhatsApp text, **Then** the system updates his stored farm profile and confirms the changes.

---

---

### User Story 4 - Automated Infrastructure-as-Code Provisioning (Priority: P2)

As a DevOps / Platform Engineer, I want all GCP cloud resources (Cloud Run service, Firestore Native DB, Cloud Scheduler job set to 18:45 Africa/Casablanca, Secret Manager secrets, IAM Service Accounts with least-privilege roles) defined and managed strictly via Infrastructure-as-Code (Terraform/HCL), so that environment provisioning, staging replication, and secret wiring are 100% reproducible, auditable, and free of manual GCP Console configuration drift per Constitution Principle VII.

**Why this priority**: Essential architectural foundation. Enforces strict reproducibility, security best practices, and zero manual console configuration.

**Independent Test**: Can be fully tested by running `terraform plan` and `terraform apply` against a sandbox GCP project, verifying that all resources (Cloud Run service, Firestore DB, Cloud Scheduler cron in `Africa/Casablanca` timezone, Secret Manager secrets, and IAM service accounts) build cleanly without manual console intervention.

**Acceptance Scenarios**:

1. **Given** a clean GCP project environment, **When** the Terraform IaC module (`terraform apply`) is executed, **Then** all required GCP resources (Cloud Run FastAPI container service, Firestore Native database instance, Cloud Scheduler 18:45 Africa/Casablanca HTTP trigger, Secret Manager secret containers, and IAM service accounts) are provisioned completely without manual GCP Console intervention.
2. **Given** Secret Manager secret containers (`WHATSAPP_TOKEN`, `VERIFY_TOKEN`, `CRON_SECRET`) are provisioned, **When** Cloud Run executes, **Then** the Cloud Run service account accesses secret values via Secret Manager secret accessor IAM permissions without hardcoded environment variables.
3. **Given** Cloud Scheduler triggers the daily batch endpoint at 18:45 Africa/Casablanca, **When** invoked, **Then** Cloud Scheduler authenticates to the Cloud Run `POST /jobs/daily-recommendations` endpoint using an OIDC token generated by a dedicated IAM service account holding `roles/run.invoker`.

---

### User Story 5 - Automated GitHub Actions CI/CD Pipeline (Priority: P2)

As a Developer / Maintainer, I want an automated GitHub Actions CI/CD workflow (`.github/workflows/deploy.yml`) that builds and pushes the application Docker image to GCP Artifact Registry and executes `terraform apply` automatically upon every push to `main`, so that application updates and infrastructure reconciliations deploy continuously without manual CLI commands.

**Why this priority**: Continuous Integration and Continuous Deployment (CI/CD) automation ensures every merged change is verified, containerized, and deployed reliably.

**Independent Test**: Can be tested by pushing a commit to `main`, observing the GitHub Actions workflow execution in `.github/workflows/deploy.yml`, verifying that the Docker image is built and pushed to Artifact Registry, and confirming that `terraform apply` reconciles infrastructure seamlessly.

**Acceptance Scenarios**:

1. **Given** a commit is pushed to the `main` branch, **When** GitHub Actions triggers `.github/workflows/deploy.yml`, **Then** the workflow authenticates to GCP, builds the Docker container image, tags and pushes it to GCP Artifact Registry (`gcr.io` or `pkg.dev`), and runs `terraform apply` in `infra/` non-interactively to complete deployment.

---

### Edge Cases

- **Connectivity Failure / Failed Message Delivery**: If a proactive evening WhatsApp message fails to deliver, the system logs the delivery failure and retries once before flagging the profile for admin review.
- **Weather API Failure / Fallback**: If Open-Meteo API calls fail during the 18:45 batch run, the system retries 3 times with short backoff (10s/30s/60s). If still failing, it uses yesterday's ET₀ baseline and appends an explicit "Estimated data" notice to the 19:00 WhatsApp advisory message.
- **Unrecognized User Reply**: If Hassan replies with text other than `1`, `2`, `3`, or a valid profile command, the system gently reminds Hassan of the available reply options.
- **Extreme Weather Events**: If heavy rainfall is forecasted for the next day (>= 15mm), the recommendation engine automatically defaults to recommending "Skip irrigation" (Reply 2).
- **Non-Standard Photo Content**: If a submitted photo contains multiple leaves or low lighting, the diagnosis automatically falls into the Low confidence (<50%) tier, omitting chemical product recommendations entirely and requesting a clearer single-leaf close-up photo per FR-016.
- **Secret Rotation / Missing Secret Version**: If a Secret Manager secret version is disabled or missing during startup/execution, Cloud Run logs a secret retrieval error and fails health checks until a valid secret version is enabled.
- **CI/CD Pipeline Failure / Terraform Drift**: If a GitHub Actions pipeline run fails during `terraform apply`, the workflow halts deployment, alerts maintainers in GitHub Actions logs, and leaves existing Cloud Run revisions active.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST proactively generate and transmit a daily irrigation advisory message over WhatsApp to registered farm managers every evening at 19:00 (7:00 PM GMT+1 / Africa/Casablanca) for next-day irrigation planning.
- **FR-002**: Daily advisory messages MUST provide 3 explicit, one-tap reply options: `1` (Approve), `2` (Skip), and `3` (Modify).
- **FR-003**: System MUST record and log the user's response (`1`, `2`, or `3`, including free-text modification details) to complete the human-in-the-loop recommendation workflow.
- **FR-004**: System MUST NOT attempt autonomous valve, solenoid, hardware, or pump control under any circumstance; all actions require human approval.
- **FR-005**: System MUST ingest daily weather forecasts and evapotranspiration (ET₀) data for each farm's registered geographic location. If Open-Meteo API is unresponsive, system MUST retry 3 times with short backoffs (10s/30s/60s) before falling back to yesterday's ET₀ baseline with an explicit "Estimated data" notice appended.
- **FR-006**: Decision logic MUST function deterministically using rule-based thresholds first; any optional LLM integration must serve as an upgrade rather than a dependency.
- **FR-007**: System MUST accept incoming plant leaf photos sent via WhatsApp and perform diagnostic triage using multimodal vision analysis.
- **FR-008**: System MUST append the verbatim ONSSA regulatory disclaimer to EVERY CropDoctor response: *"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."*
- **FR-009**: CropDoctor treatment suggestions MUST reference only products listed on the official ONSSA register of authorized plant protection products, retrieved strictly via deterministic lookup rather than model generation.
- **FR-010**: Messaging infrastructure MUST operate strictly within the WhatsApp Cloud API Sandbox tier, supporting up to 5 verified test recipient numbers.
- **FR-011**: System MUST strictly reject or ignore scope-cut features, including voice input/output processing, automated valve control, payment processing, multi-farm scheduling, and physical soil sensor integration.
- **FR-012**: System MUST store and maintain farm profile attributes (geographic coordinates, crop type, acreage, language preference) per user identifier.
- **FR-013**: System MUST emit a dual-language (French + Darija Arabizi) initial greeting for new users without requiring a mandatory language selection menu step.
- **FR-014**: System MUST automatically update `preferred_language` in the user's Farm Profile to Darija if Arabic script or common Arabizi digit substitutions (`3`, `7`, `9`) are detected in incoming replies via rule-based heuristic.
- **FR-015**: System MUST use narrow rule-based regex patterns (`[+-]\d+\s*min`, `\d{1,2}:\d{2}|\d{1,2}h\d{0,2}`) to extract custom duration/start-time parameters when handling Option 3 ("Modify") text, falling back to raw text logging in Firestore for unparseable input without LLM intervention.
- **FR-016**: System MUST maintain a static lookup table (~10–15 common tomato/citrus pathogens mapped to ONSSA-authorized active-ingredient classes). CropDoctor MUST retrieve product pointers strictly from this lookup table, omitting product names entirely on Low confidence (<50%) diagnoses or unlisted pathogens to eliminate hallucination risk.
- **FR-017**: All GCP cloud infrastructure MUST be fully defined and declaratively provisioned as Infrastructure as Code (Terraform/HCL) per Constitution Principle VII. Manual resource creation in the GCP Console is strictly prohibited.
- **FR-018**: System MUST provision a GCP Cloud Run service resource configured for serverless execution of the FastAPI application container, referencing environment configurations and Secret Manager secrets.
- **FR-019**: System MUST provision a GCP Firestore database instance in Native Mode to store farm profiles, irrigation recommendations, and disease triage logs.
- **FR-020**: System MUST provision a GCP Cloud Scheduler job resource configured to trigger `POST /jobs/daily-recommendations` on the Cloud Run service daily at 18:45 `Africa/Casablanca` time zone using secure OIDC service account authentication.
- **FR-021**: System MUST provision GCP Secret Manager resources for sensitive environment credentials (`WHATSAPP_TOKEN`, `VERIFY_TOKEN`, `CRON_SECRET`), granting read access strictly to the runtime Cloud Run IAM service account via least-privilege role bindings (`roles/secretmanager.secretAccessor`).
- **FR-022**: System MUST provision dedicated IAM Service Accounts with minimal least-privilege permissions for Cloud Run runtime and Cloud Scheduler invocation, eliminating broad administrative privileges.
- **FR-023**: System MUST provide an automated CI/CD pipeline defined in `.github/workflows/deploy.yml` that triggers on every push to the `main` branch.
- **FR-024**: The CI/CD pipeline MUST authenticate to GCP, build the application Docker container image, push it to GCP Artifact Registry, and run `terraform apply` non-interactively in `infra/` to deploy container revisions and reconcile GCP infrastructure automatically.
- **FR-025**: The Cloud Scheduler resource definition MUST explicitly specify `time_zone = "Africa/Casablanca"` at `18:45` daily to ensure precise local dispatch timing for Moroccan agricultural operations across daylight saving transitions.

### Key Entities

- **Farm Profile**: Represents a farmer's registered operational unit. Attributes include User ID/Phone Number, Geographic Location (latitude/longitude), Crop Type (e.g., Tomatoes, Citrus), Acreage (hectares), and Preferred Language (French/Darija).
- **Irrigation Recommendation**: Represents a single daily decision cycle. Attributes include Recommendation ID, Farm Profile ID, Forecasted Weather/ET₀, Recommended Water Adjustment, Status (Pending, Approved, Skipped, Modified), Scheduled Dispatch Time (19:00 GMT+1), Data Quality Flag (Fresh vs. Estimated), Parsed Modification Payload, and User Response Timestamp.
- **Disease Triage Request**: Represents a CropDoctor interaction. Attributes include Request ID, Farm Profile ID, Image Metadata, Identified Symptom/Disease, Confidence Score (High/Medium/Low), Static ONSSA Product Pointer, and Timestamp.
- **GCP Infrastructure Bundle**: Declarative Terraform HCL definitions specifying Cloud Run service resources, Firestore Native database configuration, Cloud Scheduler cron trigger (`Africa/Casablanca`), Secret Manager secrets, and IAM role bindings.
- **CI/CD Pipeline Workflow**: Declarative GitHub Actions configuration (`.github/workflows/deploy.yml`) automating GCP authentication, Docker build and push to Artifact Registry, and non-interactive `terraform apply` execution.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: **100% End-to-End Delivery**: Proactive irrigation recommendations are successfully delivered to verified WhatsApp sandbox recipient numbers every evening at 19:00 (Africa/Casablanca).
- **SC-002**: **Rapid Decision Time**: Farmers can approve, skip, or modify an irrigation decision in under 15 seconds via WhatsApp one-tap reply (Pilot User Feedback KPI; software performance SLA is <2s webhook response).
- **SC-003**: **100% Regulatory Compliance**: 100% of CropDoctor diagnostic replies include the verbatim ONSSA disclaimer, and 0% of Low-confidence replies contain chemical product names.
- **SC-004**: **High Triage Clarity**: 90%+ of pilot users report that CropDoctor disease triage explanations (French/Darija) are easy to understand (Pilot User Feedback KPI; software performance SLA is <5s vision triage).
- **SC-005**: **Zero Unsanctioned Scope Leakage**: 0 instances of automated hardware control, voice processing, or billing workflows introduced into the system.
- **SC-006**: **100% Declarative Infrastructure Coverage**: 100% of GCP cloud resources (Cloud Run, Firestore, Cloud Scheduler, Secret Manager, IAM Service Accounts) are managed via Terraform with 0 manual GCP Console configuration steps required.
- **SC-007**: **100% Automated Deployment Pipeline**: 100% of merged commits pushed to `main` complete the GitHub Actions CI/CD workflow (`.github/workflows/deploy.yml`), container image build/push, and `terraform apply` execution without manual intervention.

## Assumptions

- **Target User Persona**: Farm managers own a smartphone with active WhatsApp access and basic literacy in French or Latinized Darija text.
- **Connectivity**: Farmers have periodic cellular/data connectivity to receive WhatsApp messages during the evening.
- **Evening Review Habit**: 7:00 PM (Africa/Casablanca) previous evening dispatch aligns with early-morning irrigation schedules (pre-06:00 AM starts) and evening WhatsApp review habits; exact timing will be sanity-checked with the 3 pilot farmers during pilot conversations.
- **Zero-Friction Language Strategy**: Dual-language initial greeting avoids menu friction; Arabizi digit heuristic (`3`, `7`, `9`) handles language preference auto-detection without LLM overhead.
- **Narrow Regex Parser**: Narrow duration/time regex handles Option 3 modification acknowledgments for demo polish; raw text logging fallback ensures unparseable input never causes errors.
- **Static ONSSA Lookup Table**: Hardcoded dictionary of ~10–15 pilot crop pathogens to ONSSA classes completely eliminates AI product hallucination risk while satisfying v1 scope bounds.
- **Sandbox Boundary**: Up to 5 verified phone numbers are sufficient for initial pilot validation and StartGate incubator demo.
- **Agronomic Verification**: CropDoctor triage is understood to be a pre-selection demonstration; full agronomic validation of treatment recommendations will occur in partnership with IAV Hassan II during incubation.
- **Terraform / GCP Credentials**: Infrastructure deployment assumes standard GCP authentication with permissions to manage Cloud Run, Firestore, Cloud Scheduler, Secret Manager, IAM, and Artifact Registry.
- **CI/CD Authentication**: GitHub Actions workflow uses GCP Service Account keys or Workload Identity Federation with Secrets (`GCP_SA_KEY`, `GCP_PROJECT_ID`, etc.) configured in GitHub repository secrets.
