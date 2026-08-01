# Feature Specification: Anti-Fabrication Verification Tooling — Real Credential Enforcement, Raw-Output-Only Reporting

**Feature Branch**: `020-anti-fabrication-verification-tooling`

**Created**: 2026-08-01

**Status**: Draft

**Input**: User description: "Create a new feature spec — this replaces and supersedes the fabricated verification attempt in specs/019-production-readiness-verification. Do not modify any farmer-facing code. The explicit goal is tooling that makes it structurally impossible to repeat what just happened: a 'verification log' that reported PASS results generated entirely from mocked API responses (identifiable by mock_wamid IDs and a labeled 'simulated' timestamp) rather than real calls, right before an external stakeholder conversation."

> [!IMPORTANT]
> **Hard Constraint (Non-Negotiable)**: No script, function, or log produced by this spec may contain the words "PASS", "FAIL", "Verified", or any checkmark/status symbol (`✓`, `✔`, `❌`, `✕`). Every tool built here prints RAW, UNMODIFIED API responses and raw data only. Interpreting whether that raw output means success is explicitly a human judgment, made outside this spec, never narrated or summarized by generated code or by an agent's own log-writing.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Structural Guard Against Mock-Mode Fabrication (Priority: P1)

As the maintainer, I want any verification tool to refuse to run at all if it is not using real credentials against real Meta/Firestore infrastructure, so it is impossible to silently produce output that looks like a real test but is actually simulated.

**Why this priority**: Highest priority guardrail. Eliminates the possibility of silent mock fallbacks or simulated test outputs claiming to represent live infrastructure state.

**Independent Test**: Execute any tool in this spec with missing, placeholder, or dev credentials (e.g. tokens matching `app/whatsapp.py`'s `_is_mock_token()`), or force an API response containing the substring `"mock"`. The tool must immediately halt with an explicit hard error and refuse execution without falling back to mock mode.

**Acceptance Scenarios**:

1. **Given** environment credentials that are unconfigured, placeholder, or matching `_is_mock_token()` checks, **When** any verification tool is executed, **Then** the tool refuses to run, prints an explicit error stating verification cannot proceed, and exits immediately without executing mock code.
2. **Given** valid-appearing credentials, **When** an API call returns a response body containing the literal substring `"mock"` anywhere, **Then** the tool triggers an independent second tripwire that hard-fails execution with an explicit error.
3. **Given** real configured credentials, **When** credential verification functions run, **Then** the check reuses the existing `_is_mock_token()` function from `app/whatsapp.py` to prevent logic drift.

---

### User Story 2 - Real 24-Hour Window Check Split into Two Human-Run Steps (Priority: P1)

As the maintainer, I want a CLI tool that I run once to open a messaging window and once after a real 25+ hour wall-clock gap, printing only Meta's literal raw API response each time, so the 24-hour window question is answered by real elapsed time and real API calls without code-level timestamp backdating.

**Why this priority**: P1 critical verification mechanism. Removes automated timestamp simulation and requires human wall-clock timing between explicit CLI commands.

**Independent Test**: Execute `verify_window.py --step=open --to=<phone>` and `verify_window.py --step=check --to=<phone>` manually against a real WhatsApp recipient number, confirming raw JSON responses and explicit reminder output without any code-computed pass/fail status.

**Acceptance Scenarios**:

1. **Given** a real recipient phone number, **When** the human maintainer runs `verify_window.py --step=open --to=<real_phone_number>`, **Then** the tool sends one real free-form message via `send_text_message()`, prints Meta's raw API response verbatim, outputs the wall-clock timestamp of the call, and writes the timestamp to a local reference file.
2. **Given** an existing opened window timestamp, **When** the human maintainer runs `verify_window.py --step=check --to=<same_phone_number>`, **Then** the tool attempts a real free-form send via `send_text_message()` and a real template send via `send_template_message()` (if configured), printing both raw API responses (including full error bodies) verbatim.
3. **Given** the execution of `verify_window.py --step=check`, **When** output is printed, **Then** the tool explicitly prints a reminder stating that elapsed time enforcement is strictly on the human operator and does NOT compute, evaluate, or summarize whether 25 hours have elapsed.
4. **Given** any output from `verify_window.py`, **When** printed to stdout/stderr, **Then** no summary lines, status symbols, or pass/fail labels are included.

---

### User Story 3 - Real Meta Template Approval Status Check (Priority: P1)

As the maintainer, I want to query Meta's actual Template Management API and view the raw approval status of the daily advisory template, so I know whether it is officially usable on WhatsApp Cloud API before relying on it.

**Why this priority**: Eliminates guessing or assuming template status. Queries Meta's live endpoints directly for actual approval state.

**Independent Test**: Run `check_template_status.py` against the configured WhatsApp Business Account (WABA) ID and verify that the verbatim API payload (template name, status `PENDING`/`APPROVED`/`REJECTED`/`PAUSED`, rejection reasons, or not-found status) is printed directly.

**Acceptance Scenarios**:

1. **Given** a configured WhatsApp Business Account (WABA), **When** `check_template_status.py` is executed, **Then** the tool queries Meta's Template Management API, explicitly prints the WABA account ID queried, and outputs the raw API response for the target daily advisory template without narrative or interpretation.
2. **Given** a template that does not exist in the Meta account, **When** queried by the tool, **Then** the tool outputs the raw "not found" response body plainly without masking it or transforming it into a synthetic summary error.

---

### User Story 4 - Real Firestore Farm-Count Reality Check (Priority: P1)

As the maintainer, I want a tool that connects to the live production/pilot Firestore project (not an emulator or test database) and prints the literal count of farm profile documents, phone numbers, and last-interaction timestamps, so I can cross-verify against known pilot recruitment numbers.

**Why this priority**: Validates database environment and prevents false confidence from querying emulators or empty test collections.

**Independent Test**: Run `check_firestore_count.py` in an environment configured with real GCP credentials and verify that the target GCP project ID is explicitly printed along with raw list data (document count, phone numbers/anonymized IDs, last-interaction timestamps).

**Acceptance Scenarios**:

1. **Given** GCP Cloud credentials, **When** `check_firestore_count.py` is executed, **Then** the tool explicitly prints the connected GCP Project ID on every run.
2. **Given** active farm profile documents in Firestore, **When** the tool finishes querying, **Then** it outputs a plain, unformatted list consisting of total document count and per-document phone number (or anonymized identifier) with last-interaction timestamps—without generating a "health report" or summary judgment.

---

### User Story 5 - Retroactive Correction of the Fabricated Log (Priority: P2)

As the project record, I want the existing `specs/019-production-readiness-verification/verification_log.md` explicitly marked invalid rather than deleted, so the history of what occurred is preserved according to established project practice.

**Why this priority**: Ensures transparency and historical integrity by marking synthetic records as superseded without erasing project history.

**Independent Test**: Inspect `specs/019-production-readiness-verification/verification_log.md` and confirm the presence of the exact required SUPERSEDED header notice while preserving all original text intact.

**Acceptance Scenarios**:

1. **Given** `specs/019-production-readiness-verification/verification_log.md`, **When** this spec is executed, **Then** a prominent header is prepended: `"SUPERSEDED — this log was generated using mocked API responses (see mock_wamid identifiers and 'Simulated Inbound Timestamp' entries throughout) and does not reflect real verification. See specs/020-anti-fabrication-verification-tooling for the replacement process."`
2. **Given** the update to `verification_log.md`, **When** modified, **Then** none of the original log content is deleted or rewritten, and no attempt is made by automated scripts to generate a "corrected" log.

---

### Edge Cases

- What happens if credentials look valid initially but Meta API returns a response payload containing `"mock"`? The tool must trigger its secondary tripwire, abort execution immediately, and print an explicit error refusing to process simulated data.
- What happens if the Meta API endpoint returns an HTTP 400/401/403/404 error during template check or window verification? The tool must print the raw, unmodified HTTP status code and response payload body without swallowing the error or mapping it to a summary string.
- What happens if Firestore cannot be reached or credentials lack permissions? The tool must print the raw exception traceback/error and exit immediately without generating fallback data.
- What if a human attempts to run `--step=check` immediately after `--step=open`? The tool prints the raw API call response and re-emits its mandatory warning that human wall-clock elapsed time is not verified by the script itself.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Verification tools MUST implement `is_real_credential_configured()` (or equivalent) reusing `_is_mock_token()` from `app/whatsapp.py` to check for mock tokens and placeholder credentials.
- **FR-002**: Verification tools MUST halt execution with an explicit error message whenever `is_real_credential_configured()` returns `False` and MUST NEVER fall back to mock mode.
- **FR-003**: Verification tools MUST inspect API response bodies and halt immediately with a hard error if the substring `"mock"` appears in any response payload.
- **FR-004**: No script, module, function, or output text created under this spec MAY contain the strings `"PASS"`, `"FAIL"`, `"Verified"`, or status checkmarks (`✓`, `✔`, `❌`, `✕`).
- **FR-005**: `verify_window.py` MUST provide a CLI argument `--step=open` taking `--to=<phone>` that dispatches a real text message via `send_text_message()`, prints the raw Meta API response, logs the call wall-clock timestamp, and records the timestamp to a local file.
- **FR-006**: `verify_window.py` MUST provide a CLI argument `--step=check` taking `--to=<phone>` that dispatches a real text message via `send_text_message()` and a real template message via `send_template_message()` (if template name configured), printing both raw Meta API responses verbatim.
- **FR-007**: `verify_window.py` MUST print an explicit disclaimer on every `--step=check` execution reminding the human operator that elapsed time enforcement is solely the operator's responsibility.
- **FR-008**: `check_template_status.py` MUST query Meta's Template Management API for the target WhatsApp Business Account (WABA), explicitly print the WABA ID queried, and output raw template status JSON payload without narrative.
- **FR-009**: `check_firestore_count.py` MUST connect to live GCP Firestore infrastructure, explicitly print the connected GCP Project ID on every run, and output a raw list of document count, phone numbers/identifiers, and last-interaction timestamps.
- **FR-0010**: The project record `specs/019-production-readiness-verification/verification_log.md` MUST be prepended with the explicit `SUPERSEDED` header notice while preserving all original lines intact.
- **FR-011**: No tool built under this spec shall produce summary reports, health scores, or automated pass/fail determinations.
- **FR-012**: Farmer-facing code in `app/` MUST NOT be modified by any tool or script created in this spec.

### Key Entities *(include if feature involves data)*

- **Credential Tripwire**: Centralized validation function reusing `app.whatsapp._is_mock_token` to enforce non-mock environment configuration.
- **Raw API Payload**: Unmodified response body returned directly by Meta WhatsApp Cloud API or Firestore API endpoints.
- **Window Verification Record**: Local reference file containing raw execution timestamps recorded during `--step=open` CLI runs.
- **Superseded Log Header**: Standardized notice banner prepended to `specs/019-production-readiness-verification/verification_log.md` to indicate synthetic test history.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All anti-fabrication tools (`verify_window.py`, `check_template_status.py`, `check_firestore_count.py`) refuse to execute against mock/placeholder credentials and explicitly error rather than proceeding.
- **SC-002**: 100% of source files and output streams produced by this spec are free from the words "PASS", "FAIL", "Verified", and checkmark/cross status symbols.
- **SC-003**: 100% of tool executions for template status and Firestore count explicitly print the target WABA ID and GCP Project ID respectively before displaying raw output.
- **SC-004**: `specs/019-production-readiness-verification/verification_log.md` is prepended with the exact `SUPERSEDED` header notice while retaining all original log entries without deletion or revision.

## Non-Goals

- **NO Automated Pass/Fail Summaries**: Does NOT compute, evaluate, or output pass/fail verdicts or verification summaries.
- **NO Modifications to Farmer-Facing Code**: Does NOT alter code in `app/`.
- **NO Automated 25-Hour Wait Scheduling**: Does NOT automate, schedule, or simulate time delays; window verification is strictly two manual steps executed by a human operator.
- **NO Verification Log Generation**: Does NOT output new verification logs or markdown completion reports.

## Assumptions

- Maintainer has access to live Meta WhatsApp Cloud API credentials (phone number ID, WABA ID, permanent access token).
- Maintainer has access to live GCP Cloud Run / Firestore credentials (`GCP_PROJECT_ID` or application default credentials).
- The existing function `_is_mock_token()` in `app/whatsapp.py` accurately identifies dev/test token patterns and can be imported directly.
- The human operator takes personal responsibility for measuring real elapsed wall-clock time between `--step=open` and `--step=check` executions.
