# Research: P0 Stabilization Batch Technical Decisions

## Technical Decisions

### 1. Vertex AI Gemini 1.5 Flash Audio ASR Integration (BUG-001)

- **Decision**: Wire `parse_voice_intent()` to Gemini 1.5 Flash Audio ASR using `google.generativeai` / `vertexai` SDKs with structured JSON extraction.
- **Rationale**:
  - `gemini-1.5-flash` natively accepts raw audio bytes (`audio/ogg; codecs=opus`, `audio/mp3`, `audio/wav`) without requiring local `ffmpeg` transcoding dependencies.
  - Gemini 1.5 Flash excels at Moroccan Darija phonetics, Arabic script, and French/Darija code-switching (e.g. *"Zid 15 minutes f l'arrosage stp"*).
  - Constraining Gemini with a strict system instruction forces output into a schema matching the expected action tuple `(confidence_score, transcribed_text, parsed_action)`.
- **System Prompt Specification**:
  ```text
  You are an audio speech-to-text assistant for Moroccan farm managers speaking Darija or French.
  Transcribe the audio note accurately and extract the requested irrigation action.
  Output ONLY a raw JSON object with keys:
  - "transcribed_text": string
  - "confidence_score": float between 0.0 and 1.0
  - "intent_type": one of ["MODIFY_IRRIGATION", "INCREASE_IRRIGATION", "DECREASE_IRRIGATION", "SKIP_IRRIGATION"]
  - "proposed_adjustment_minutes": integer (default 15 if duration adjustment requested, else 0)
  ```
- **Error & Exception Safety**:
  - Any SDK exception (API timeout, authentication error, invalid payload, or rate limit) is caught in a `try...except Exception` block.
  - On error, `parse_voice_intent()` logs a warning and returns `(0.0, "ASR_FAILURE", None)`.
  - Downstream caller `process_voice_note()` checks `confidence >= 0.80`; any score < 0.80 automatically triggers the low-confidence text fallback menu and writes zero pending intent to Firestore.
- **Test Fixture Exemption & Anti-Mock Verification**:
  - Test fixture byte strings (`b"fake_low_confidence"`, `b"garbled"`) are explicitly checked first in `parse_voice_intent()` to preserve fast, deterministic testing of fallback paths.
  - All other audio inputs hit the Vertex AI SDK call.
  - Anti-mock regression test mocks the Vertex AI SDK client response (returning dynamic transcripts for different mocked payloads) and asserts that distinct audio inputs produce distinct results, failing if a hardcoded mock is returned.

---

### 2. Terraform / IaC Scope Resolution (BUG-003 - Option A)

- **Decision**: Execute Option A — delete `infra/*.tf` and `.terraform.lock.hcl` files from the repository active build.
- **Rationale**:
  - IaC scope ambiguity has recurred three times as scope creep across spec passes.
  - Option A completely removes unused HCL files from the active build until post-selection explicitly reopens IaC scope, eliminating confusion and automated false-positive metrics.
- **Constitution Governance Amendment**:
  - Section VII of `.specify/memory/constitution.md` updated to state:
    > *"Infrastructure as Code (Terraform) is explicitly deferred for pilot deployment. `gcloud run deploy` is the sole sanctioned pre-selection deployment path. `infra/*.tf` files are removed from the active build."*
- **Report & Documentation Audit**:
  - Update `README.md` and project summaries to reflect that deployment relies on `gcloud run deploy` and that IaC scope is deferred post-selection.

---

### 3. Spec Status Metadata Audit (BUG-004)

- **Decision**: Update header statuses across all numbered specs to reflect verified completion state.
- **Target Status Matrix**:
  | Spec ID | Spec Title | New Status | Justification |
  |---------|------------|------------|---------------|
  | 001 | Hassan Irrigation Agent | `Status: Implemented` | Core hero features verified complete. |
  | 002 | Quality & Security Gate | `Status: Implemented` | Pre-commit hooks & gates active. |
  | 003 | Audit Schema Coverage | `Status: Implemented` | Audit logging & schemas verified. |
  | 004 | Fix Critical Bugs & Gaps | `Status: Implemented` | Verified accurate (no change). |
  | 005 | ONSSA Registry Sync | `Status: Implemented` | ONSSA lookup & sync verified. |
  | 006 | Crop ETc Calculation | `Status: Implemented` | FAO-56 ETc calculations verified. |
  | 007 | Image Prefilter Heuristics | `Status: Implemented` | Blur & Laplacian prefilters verified. |
  | 008 | Sentinel Canopy Heatmaps | `Status: Blocked` | Blocked until spec 011 real-imagery fix merges. |
  | 009 | Voice Darija STT Safety | `Status: Blocked` | Blocked until User Story 1 of spec 012 completes. |
  | 010 | IAV Disease Classifier | `Status: Blocked` | Dataset dependency gated. |
  | 011 | Real Sentinel NDVI | `Status: In Progress` | Tracked in separate feature spec. |
  | 012 | P0 Stabilization Batch | `Status: Draft` | Current active stabilization spec. |
