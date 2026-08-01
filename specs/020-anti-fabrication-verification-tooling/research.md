# Phase 0 Research: Anti-Fabrication Verification Tooling

## Technical Findings & Architectural Decisions

### Decision 1: Reuse of `_is_mock_token()` and Credential Tripwires
- **Context**: The existing `app/whatsapp.py` module defines `_is_mock_token(token: str) -> bool`, which returns `True` if `token` is empty or begins with known dev/test prefixes (`eaag_your_`, `your_`, `mock_`, `test_`).
- **Reuse Strategy**: `_is_mock_token` is already a module-level function in `app/whatsapp.py`. All new CLI scripts under `scripts/` will directly import `from app.whatsapp import _is_mock_token`. Zero changes to `app/whatsapp.py` or any farmer-facing code in `app/` are required.
- **Credential Guard Implementation**: A dedicated helper module (`scripts/verify_credential_guard.py`) will provide:
  1. `is_real_credential_configured()`: Reuses `_is_mock_token(WHATSAPP_TOKEN)` and verifies that `WHATSAPP_PHONE_NUMBER_ID` and `GCP_PROJECT_ID` are set and non-placeholder.
  2. `assert_no_mock_substring(payload)`: Scans any API response dictionary or string for the literal substring `"mock"` (case-insensitive). If detected, raises an explicit `RuntimeError("Mock payload detected in verification output - refusing execution.")`.

### Decision 2: Interactive Human-Only Execution Model
- **Context**: Automated scripts running unattended in background tasks or CI pipelines invite silent mock fallbacks and backdated timestamp claims.
- **Design Choice**:
  - Each CLI tool requires mandatory, explicit positional or flag arguments (e.g., `--to=<phone>`, `--step=<open|check>`).
  - No default phone numbers or fallback steps are provided.
  - Execution runs strictly in local interactive terminals against environment variables set by the operator (`WHATSAPP_TOKEN`, `GCP_PROJECT_ID`).

### Decision 3: Structural Raw-Output-Only Enforcement
- **Hard Constraint**: Source code and CLI outputs MUST NOT contain the words `PASS`, `FAIL`, `Verified`, or status checkmarks (`✓`, `✔`, `❌`, `✕`).
- **Implementation Rules**:
  - All outputs print raw JSON structures using `json.dumps(obj, indent=2)` or plain unformatted text tuples.
  - In `verify_window.py`, step `--step=open` prints wall-clock timestamp and raw JSON. Step `--step=check` attempts text send and template send, printing both raw HTTP response payloads.
  - `verify_window.py` MUST NOT compute or output elapsed hours, timestamp deltas, or time elapsed assertions. Every run of `--step=check` prints the literal reminder: `"NOTICE: Elapsed time between window open and check steps is NOT asserted or computed by this tool. The human operator is strictly responsible for verifying real wall-clock elapsed time."`

### Decision 4: Testing Refusal Behavior vs. Real API Responses
- **Testing Scope**:
  - Unit tests in `tests/test_anti_fabrication_tooling.py` MUST verify refusal logic: given `WHATSAPP_TOKEN="mock_123"` or a response body with `"mock_wamid"`, the tools exit with a non-zero code or raise a `RuntimeError`.
  - Unit tests MUST NOT mock Meta API or Firestore responses to assert simulated success output, as that would recreate the synthetic verification flaw.

### Decision 5: Direct Firestore Client Access
- **Context**: `app/firestore_client.py` contains an in-memory fallback dict (`_IN_MEMORY_FARM_PROFILES`) when GCP credentials are missing.
- **Anti-Fabrication Rule**: `scripts/check_firestore_count.py` MUST NOT use `app.firestore_client`. Instead, it initializes `google.cloud.firestore.Client(project=GCP_PROJECT_ID)` directly. If authentication fails or credentials are invalid, it prints the error and terminates immediately.
