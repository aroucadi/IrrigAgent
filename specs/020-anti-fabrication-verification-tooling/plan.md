# Implementation Plan: Anti-Fabrication Verification Tooling — Real Credential Enforcement, Raw-Output-Only Reporting

**Branch**: `020-anti-fabrication-verification-tooling` | **Date**: 2026-08-01 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/020-anti-fabrication-verification-tooling/spec.md)

**Input**: Feature specification from `/specs/020-anti-fabrication-verification-tooling/spec.md`

## Summary

This plan governs implementation of anti-fabrication verification tooling that makes it structurally impossible to generate synthetic "verification" logs. Tools enforce real GCP/Meta credentials via `_is_mock_token()` from `app/whatsapp.py` and secondary `"mock"` substring tripwires, refusing execution if mock mode is active. All tools output raw, unmodified API JSON responses without narrative, status checkmarks, pass/fail labels, or timestamp calculation.

## Technical Context

**Language/Version**: Python 3.11+ (CLI scripts under `scripts/`).

**Primary Dependencies**: `httpx` (Meta Graph API calls), `google-cloud-firestore` (Direct Firestore client), `app.whatsapp` (`_is_mock_token`, `send_text_message`, `send_template_message`).

**Storage**: Local JSON file (`.verify_window_last_open.json`) for raw open timestamp recording; Firestore for live count check.

**Testing**: `pytest` (`tests/test_anti_fabrication_tooling.py`) testing refusal behavior on mock credentials and mock payload tripwires. No synthetic API response mocks for live test paths.

**Target Platform**: Local interactive terminal execution against live GCP/Meta infrastructure. Strictly non-automated, non-scheduled.

**Project Type**: CLI verification scripts (`scripts/`).

**Performance Goals**: Instant CLI execution and direct raw payload rendering (<3s per API call).

**Constraints**:
- **Zero changes to farmer-facing code** in `app/`. `_is_mock_token()` is imported directly as-is.
- **Hard Constraint**: No script or output contains `"PASS"`, `"FAIL"`, `"Verified"`, or checkmarks (`✓`, `✔`, `❌`, `✕`).
- **No Timestamp Calculation**: `verify_window.py` does not calculate or report elapsed hours between steps.
- **Direct Firestore Access**: `check_firestore_count.py` uses `google.cloud.firestore.Client` directly without in-memory fallback dicts.

## Constitution Check

*GATE: Passed. Re-verified post-design.*

1. **Principle VIII (No-Facade Rule & CRIT-007 No-Ambiguous-Mock-Fallback)**:
   - Verification tools explicitly check for mock tokens and halt on detection.
   - Secondary tripwires inspect raw HTTP response bodies for `"mock"` substrings to prevent hidden mock responses from passing as live calls.
2. **Lowest-Layer Enforcement**:
   - Credential validation and response body scanning occur directly on raw `httpx` responses and `google.cloud.firestore` connection objects.
   - No wrapper abstractions introduced that could be mocked in unit tests.

## Project Structure

### Documentation (this feature)

```text
specs/020-anti-fabrication-verification-tooling/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 research document
├── quickstart.md        # Quickstart validation guide
└── tasks.md             # Execution task breakdown
```

### Source Code & Test Layout

```text
scripts/
├── verify_credential_guard.py  # Credential check & mock substring tripwire module
├── verify_window.py            # User Story 2: Two-step 24h window CLI tool
├── check_template_status.py    # User Story 3: Meta Template Management API status check
└── check_firestore_count.py    # User Story 4: Live Firestore farm document count check

specs/019-production-readiness-verification/
└── verification_log.md         # User Story 5: Retroactive SUPERSEDED header update

tests/
└── test_anti_fabrication_tooling.py  # Refusal behavior unit tests
```

**Structure Decision**: Single project repo structure with CLI tools under `scripts/`, test suite under `tests/`, and spec documentation under `specs/020-anti-fabrication-verification-tooling/`.

## Complexity Tracking

> No constitution violations. Structural enforcement strictly simplifies verification transparency.
