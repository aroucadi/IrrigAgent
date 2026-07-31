# Implementation Plan: Pre-Conversation Production Readiness Verification

**Branch**: `019-production-readiness-verification` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/019-production-readiness-verification/spec.md)

**Input**: Feature specification from `specs/019-production-readiness-verification/spec.md`

## Summary

This plan outlines the operational verification strategy to validate that all v1.0 claims (24-hour window compliance, template dispatches, interactive button callbacks, opt-out logic, and engagement report sanity) work end-to-end against real Meta WhatsApp sandbox infrastructure and live Firestore database state.

This is an operational verification plan rather than a software development plan. It introduces **no new code, no new dependencies, no new data schemas, and no new automated tests**. The single primary artifact produced by executing this plan is a comprehensive execution record: `specs/019-production-readiness-verification/verification_log.md`.

## Technical Context

**Language/Version**: Operational verification only. Documentation created in Plain Markdown (`verification_log.md`). Existing scripts run on Python 3.11.

**Primary Dependencies**: None new. Existing Python standard libraries, `httpx`, `google-cloud-firestore`, and official Meta WhatsApp Cloud API sandbox endpoints. No new libraries, logging frameworks, or monitoring tools will be added.

**Storage**: Real Google Cloud Firestore instance (read & state mutation verification). Verification log stored at `specs/019-production-readiness-verification/verification_log.md`.

**Testing**: 100% Manual, Real-Device & Real-API verification. Automated tests are explicitly excluded from this phase as prior automated tests passed with mocks and masked live behavior gaps. Any recommended automated tests discovered during this audit will be logged as follow-up recommendations in `verification_log.md`.

**Target Platform**: Live Meta WhatsApp Cloud API Sandbox environment (targeting real verified recipient phone numbers) and live Cloud Run deployment (or local execution against live Firestore and Meta API credentials).

**Project Type**: Operational Verification & Audit.

**Performance Goals**: N/A for code. Verification completion target is within 36 hours of launch.

**Constraints**:
- **25+ Hour Wait Constraint**: User Story 1 requires waiting 25+ consecutive hours without sending any inbound messages from the test sandbox number.
- **Parallelization Constraint**: User Stories 2, 3, and 4 MUST be executed during the 25-hour wait period using separate dedicated test numbers or carefully sequenced runs before the 25-hour silence window begins, ensuring zero wasted calendar time.
- **Zero Production Code Changes**: No application code (`app/`), decision logic (`app/decision.py`), or models may be modified. Bugs identified must be logged as standalone findings in `verification_log.md`.
- **Target Completion Date**: 2026-08-02 12:00 UTC (providing a 3-day buffer ahead of next week's stakeholder meeting).

## Constitution Check

*GATE: Must pass before execution.*

- [x] **I. Human-in-the-Loop Only**: Verified. All interactions are via WhatsApp message/button prompts to human recipient numbers.
- [x] **IV. WhatsApp Cloud API Sandbox Tier Only**: Verified. Verification targets official Meta WhatsApp Sandbox numbers only (max 5 verified recipients).
- [x] **V. Strict Scope Boundary**: Verified. No cut-list items (solenoid controls, billing, complex scheduling) introduced.
- [x] **VI. End-to-End Demoability**: Verified. Core goal of this plan is empirical proof of live end-to-end demoability.
- [x] **VIII. Quality, Security & Automated Verification Gates**:
  - *No-Facade Rule for External Integrations*: Directly addressed by this plan. Verifies real Meta API responses outside the 24h window instead of mock responses.
  - *No-Ambiguous-Mock-Fallback Rule*: Verified. Live Meta API error codes (e.g. 131026) and HTTP status codes will be captured verbatim without synthetic fallback.
- [x] **No Fabricated Data in Production Check**: User Story 4 dashboard verification explicitly inspects `scripts/generate_engagement_report.py` output against live Firestore to assert the presence of "early/directional data" warnings and 0 fabricated/interpolated values.

## Project Structure

### Documentation (this feature)

```text
specs/019-production-readiness-verification/
├── spec.md                  # Feature specification
├── plan.md                  # This implementation plan
├── verification_log.md      # Primary deliverable: Raw API logs, timestamps, state assertions
├── checklists/
│   └── requirements.md      # Specification quality checklist
└── tasks.md                 # Task checklist grouped by execution phase
```

### Source Code (existing scripts used for verification)

```text
scripts/
├── verify_whatsapp_24h_window.py    # Used for User Story 1 (live 24h window test)
└── generate_engagement_report.py    # Used for User Story 4 (live Firestore report check)

app/
├── main.py                          # Cloud Run FastAPI entrypoint receiving webhooks
├── whatsapp.py                      # Outbound Cloud API dispatch module
└── firestore_client.py              # Firestore reader/writer
```

## Verification Strategy & Environment Matrix

| User Story | Target Environment | Test Subject | Key Action | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **US1: 24h Window & Template** | Live Cloud Run / Script against Live Meta API | Real Sandbox Number A | Send baseline msg, wait 25+ hrs, attempt daily job trigger | Capture raw API response; verify template delivery or Meta 131026 error code |
| **US2: Interactive Buttons** | Physical WhatsApp Client + Webhook Handler | Real Sandbox Number B | Tap `Approve`, `Skip`, `Modify`, `Confirm`, `Cancel` | State updated in Firestore; correct reply emitted |
| **US3: Opt-Out & Help** | Physical WhatsApp Client + Webhook Handler | Real Sandbox Number B | Send `/stop` and `/help` | Profile set `opt_out=True` & skipped in batch; local menu rendered |
| **US4: Dashboard Sanity** | Local Execution against Live Firestore | Live Firestore DB | Run `generate_engagement_report.py` | "Early/directional data" label present; 0 synthetic numbers |

## Timeline & Parallelization Strategy

```
Calendar Timeline (Target Completion: Aug 2, 2026)

[Day 1 - Friday Night (Aug 1, 00:00 UTC)]
  └── Task 1.1: Trigger inbound ping from Test Phone A, record timestamp T0.
  └── START 25-HOUR SILENCE WINDOW on Test Phone A.

[Day 1 - Saturday (During 25h Silence Window on Test Phone A)]
  ├── Task 2.1: Test Interactive Buttons (Approve/Skip/Modify/Confirm/Cancel) on Test Phone B.
  ├── Task 3.1: Test Opt-Out (/stop) & Batch Exclusion on Test Phone B.
  ├── Task 3.2: Test Help Menu (/help) Rendering on Test Phone B.
  └── Task 4.1: Run Engagement Dashboard against Live Firestore on Local Dev machine.

[Day 2 - Saturday Night / Sunday Morning (Aug 2, 01:30 UTC - 25.5 Hours Post T0)]
  ├── Task 1.2: Attempt Free-form Text & Daily Advisory Template send to Test Phone A.
  ├── Task 1.3: Record raw Meta API response payload, HTTP code, and timestamps.
  └── Task 5.1: Synthesize all findings into specs/019-production-readiness-verification/verification_log.md.
```

## User Review Required

> [!IMPORTANT]
> **25-Hour Window Calendar Dependency**: User Story 1 requires a strict 25+ hour window with **zero** inbound messages from Test Phone A. Ensure Test Phone A is not used for any other testing or interactive messaging during this period.

> [!WARNING]
> **No Inline Fixes Policy**: If any verification step fails (e.g. Meta template rejected, button webhook times out, or dashboard fails), the failure will be logged as a blocking finding in `verification_log.md`. No inline code patches will be committed as part of this plan.
