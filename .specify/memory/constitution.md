<!--
### Sync Impact Report
- Version change: 1.0.0 → 1.1.0
- Modified principles: N/A
- Added sections:
  - Core Principles: Added VII. Infrastructure as Code (NON-NEGOTIABLE) requiring Terraform/HCL or TypeScript for all GCP infrastructure.
- Removed sections: N/A
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (Constitution Check gate verified)
  - ✅ .specify/templates/spec-template.md (Scope/constraints verified)
  - ✅ .specify/templates/tasks-template.md (Task categorization verified)
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
- Voice input or output processing (Darija or French voice notes)
- Autonomous hardware or solenoid valve control
- Payment processing or subscription billing flows
- Complex multi-farm scheduling
- Physical soil sensor hardware integration

Any feature request or code addition introducing cut list capabilities MUST be rejected or deferred.

### VI. End-to-End Demoability
Every feature in scope MUST be testable and demoable end-to-end with a real WhatsApp test recipient number before being considered complete.

### VII. Infrastructure as Code (NON-NEGOTIABLE)
All GCP infrastructure components (Cloud Run, Firestore, Cloud Scheduler, Secret Manager, IAM) MUST be defined as Infrastructure as Code using Terraform/HCL or TypeScript (e.g., Pulumi/CDKTF). Manual GCP Console configuration ("clicking") is strictly prohibited for production and staging environments to ensure reproducibility, auditability, and zero configuration drift.

## Technical & Architectural Constraints

- **Messaging Infrastructure**: Meta WhatsApp Cloud API Sandbox tier only (max 5 verified recipient phone numbers).
- **Backend Stack**: Python 3.11+, FastAPI web service deployed on GCP Cloud Run.
- **Infrastructure Provisioning**: Terraform/HCL or TypeScript for all GCP resources (Cloud Run, Firestore, Cloud Scheduler, Secret Manager, IAM).
- **Data Persistence**: Firestore for farm profiles and interaction logs only; flat, lightweight schemas.
- **External Integrations**: Open-Meteo API for daily weather/ET₀ data; Gemini 1.5 Flash via Vertex AI for leaf photo triage.
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

**Version**: 1.1.0 | **Ratified**: 2026-07-28 | **Last Amended**: 2026-07-28
