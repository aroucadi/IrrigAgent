<!--
### Sync Impact Report
- Version change: 1.6.1 → 1.7.0
- Modified principles:
  - Section VIII (Quality, Security & Automated Verification Gates): Added No-Ambiguous-Mock-Fallback Rule (CRIT-007) prohibiting fallback or default values that match test-mode or mock-mode detection signals, requiring explicit loud failures on missing runtime values.
- Added sections: None
- Removed sections: None
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (Constitution Check gates verified)
  - ✅ .specify/templates/spec-template.md (Automated verification acceptance criteria verified)
  - ✅ .specify/templates/tasks-template.md (Pre-commit & test task discipline verified)
- Follow-up TODOs: None
-->

# IrrigAgent AI Constitution

## Core Principles

### I. Human-in-the-Loop Only (NON-NEGOTIABLE)
All recommendations, alerts, and advisories are transmitted to farm managers via WhatsApp for human review, approval, or modification. There MUST BE NO automated hardware control (e.g., solenoid valves, pumps, relays) in v1. The agent proposes; the human executes or confirms.

### II. Rule-Based First Logic
The core decision engine MUST be implemented and operational using plain, deterministic rule-based logic (e.g., weather forecasts and ET₀ calculation thresholds). LLM reasoning is an optional upgrade tier and MUST NOT be a dependency for the primary irrigation recommendation loop to function.

### III. Mandatory ONSSA Regulatory Disclaimer
Every response emitted by the CropDoctor disease-triage feature MUST contain the verbatim ONSSA regulatory disclaimer:
> *"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."*

Furthermore, any treatment pointers MUST reference only products listed on the official ONSSA authorized register.

### IV. WhatsApp Cloud API Sandbox Tier Only
Messaging infrastructure is strictly limited to the Meta WhatsApp Cloud API in sandbox mode (maximum 5 verified numbers). No paid messaging vendors (e.g., Twilio) or full WhatsApp Business Verification shall be introduced during initial pilot/application phases.

### V. Strict Scope Boundary & Cut List Enforcement (NON-NEGOTIABLE)
The explicit cut list is strictly enforced for v1. The system MUST NOT include:
- Autonomous hardware or solenoid valve control
- Payment processing or subscription billing flows
- Complex multi-farm scheduling
- Physical soil sensor hardware integration

*Note on Voice Scope*: Voice output (TTS acknowledgment of approve/skip/modify) is permitted as an optional, flagged enhancement (`ENABLE_DARIJA_VOICE_TEASER=true`) once the core text loop and CropDoctor features are fully pilot-validated. Voice input (transcription/ASR) remains strictly out of scope for this phase. Primary text/button execution MUST remain sub-second and fully independent.

Any feature request or code addition introducing non-permitted cut list capabilities MUST be rejected or deferred.

### VI. End-to-End Demoability
Every feature in scope MUST be testable and demoable end-to-end with a real WhatsApp test recipient number before being considered complete.

### VII. Infrastructure Management & Deployment Path (NON-NEGOTIABLE)
All v1 pilot application deployments MUST use GCP Cloud Run CLI (`gcloud run deploy`) per PRD Section 15.11. Declarative Infrastructure as Code (`infra/*.tf`) is explicitly deferred for post-selection environment scaling and is removed from the active build to eliminate scope drift and false-positive completion metrics. Manual GCP Console configuration ("clicking") remains strictly prohibited for production and staging environments to ensure auditability and zero configuration drift.

### VIII. Quality, Security & Automated Verification Gates (NON-NEGOTIABLE)
All development and feature deliverables MUST satisfy mandatory automated verification and security controls:
- **Zero-Broken-Tests Policy**: No feature implementation task is considered "DONE" unless the full automated test suite (`pytest tests/`) executes with a 100% pass rate.
- **Deterministic Math & Parsing Coverage**: All irrigation decision calculations (ET₀ thresholds, duration deltas) and WhatsApp message interaction parsing rules (options 1, 2, 3) MUST have explicit unit test coverage.
- **Zero Secrets in Code**: Hardcoding, staging, or committing plain-text API keys, Google Cloud service account JSON credentials, or Meta WhatsApp tokens is strictly forbidden.
- **Mandatory Pre-Commit Gate Enforcement**: All local commits MUST execute and pass automated pre-commit hook checks enforcing secret scanning, fast unit tests (execution time < 3.0 seconds), and static linting/formatting (`ruff`, `black`).
- **Automated Verification Standard**: Every major feature specification MUST explicitly define acceptance criteria that can be verified deterministically via automated test assertions or endpoint health/swagger checks.
- **No-Facade Rule for External Integrations**: No feature may be marked "Completed & Verified" if its core external API/model call has a hardcoded or synthetic default path reachable in production. Every completion claim MUST include a test that fails when realistic (non-fixture) input hits that path with the mock still in place.
- **No-Ambiguous-Mock-Fallback Rule (CRIT-007)**: No function may construct a fallback or default value that coincides with a string another function in the codebase treats as a test-mode or mock-mode signal. If a real value is missing at runtime, the system MUST fail loudly (log error and raise exception) and NEVER silently substitute a value that matches a test-detection pattern.

## Technical & Architectural Constraints

- **Messaging Infrastructure**: Meta WhatsApp Cloud API Sandbox tier only (max 5 verified recipient phone numbers).
- **Backend Stack**: Python 3.11+, FastAPI web service deployed on GCP Cloud Run.
- **Infrastructure Provisioning**: GCP Cloud Run CLI (`gcloud run deploy`) for v1 pilot deployment; Terraform HCL deferred post-selection.
- **Data Persistence**: Firestore for farm profiles and interaction logs only; flat, lightweight schemas.
- **External Integrations**: Open-Meteo API for daily weather/ET₀ data; Gemini 1.5 Flash via Vertex AI for leaf photo triage; Google Cloud Text-to-Speech API (`ar-MA`) for optional Darija voice teaser notes.
- **Resource Constraints**: Designed for solo founder execution within GCP credit limits ($10k hackathon credits).

## Development & Spec-Driven Workflow

- **Spec-Driven Methodology**: All implementation must follow the GitHub `spec-kit` workflow (constitution → specify → plan → tasks → implement).
- **No Vibe-Coding Drift**: Features MUST be implemented strictly against explicit, versioned specification documents (`spec.md`), not informal or ad-hoc prompt history.
- **Quality & Verification**: Every task implementation MUST undergo runtime verification over WhatsApp sandbox endpoints before sign-off.

## Governance

- **Supremacy**: This Constitution supersedes all other technical specifications, implementation plans, and development habits.
- **Amendment Procedure**: Amendments to principles or scope boundaries require explicit updating of this document, semantic version increment, and a recorded Sync Impact Report.
- **Compliance Review**: Every implementation plan (`plan.md`) MUST include a mandatory "Constitution Check" gate verifying compliance prior to execution.
- **Versioning Policy**:
  - **MAJOR**: Removal or redefinition of core governance principles or non-negotiables.
  - **MINOR**: Addition of new principles, expanded scope boundaries, or governance rules.
  - **PATCH**: Clarifications, formatting, typo corrections, and non-semantic refinements.

**Version**: 1.7.0 | **Ratified**: 2026-07-28 | **Last Amended**: 2026-07-31
