# Quickstart Guide: Anti-Fabrication Verification Tooling

This guide outlines how maintainers interactively execute the raw-output verification tools and validate their refusal guards.

## Prerequisites

1. Set real Meta WhatsApp credentials in environment variables or `.env`:
   ```bash
   export WHATSAPP_TOKEN="EAAG..." # Real permanent access token
   export WHATSAPP_PHONE_NUMBER_ID="105938472910482"
   export WHATSAPP_BUSINESS_ACCOUNT_ID="109283746510293"
   ```
2. Set real GCP credentials for Firestore:
   ```bash
   export GCP_PROJECT_ID="irrigagent-prod" # Real pilot GCP Project ID
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
   ```

---

## Tool 1: Credential Guard Verification

Run the credential guard standalone check to confirm environment credentials pass mock token detection:

```bash
python scripts/verify_credential_guard.py
```

Expected behavior:
- If `WHATSAPP_TOKEN` matches `_is_mock_token()` patterns, the script prints an explicit refusal error and exits with non-zero status code.
- If real credentials are present, it prints raw configuration confirmation (with token masked).

---

## Tool 2: 24-Hour Messaging Window Verification (Two Steps)

### Step 1: Open Window (Run initially)
Sends a free-form message to open/verify the messaging window and records the call timestamp locally:

```bash
python scripts/verify_window.py --step=open --to=+212600000001
```

Output: Verbatim JSON response from Meta Graph API and local wall-clock timestamp string recorded to `.verify_window_last_open.json`.

### Step 2: Check Window (Run after a real 25+ hour wall-clock gap)
Attempts free-form and template-based message dispatches:

```bash
python scripts/verify_window.py --step=check --to=+212600000001
```

Output: Verbatim raw JSON response for both text and template attempts (including error body if 131026 window expired error occurs). Emits mandatory notice:
> *"NOTICE: Time elapsed between open and check steps is not asserted or calculated by this script. Human operator must verify wall-clock elapsed time manually."*

---

## Tool 3: Meta Template Approval Status Query

Query Meta's Template Management API for live approval status of configured templates:

```bash
python scripts/check_template_status.py --waba-id=109283746510293 --name=irrigagent_daily_advisory
```

Output: Explicitly prints target WABA ID and verbatim Graph API JSON payload (showing `APPROVED`, `PENDING`, `REJECTED`, or `PAUSED`).

---

## Tool 4: Firestore Farm Document Count Reality Check

Query production Firestore for active farm profile counts, phone numbers, and last interaction timestamps:

```bash
python scripts/check_firestore_count.py
```

Output: Explicitly prints connected GCP Project ID and plain list of document count and per-document phone number / last-interaction timestamp records. Refuses execution if Firestore client falls back or cannot authenticate.

---

## Automated Refusal Guard Tests

Execute automated tests asserting refusal behavior on mock inputs:

```bash
pytest tests/test_anti_fabrication_tooling.py -v
```

Expected behavior: All unit tests validating refusal on mock tokens, missing credentials, and `"mock"` payload tripwires pass.
