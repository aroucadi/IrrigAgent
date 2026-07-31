# Quickstart Validation Guide: Pre-Demo Critical Fixes

## 1. Clean Installation & Boot Verification (CRIT-006)

Validate that the app installs cleanly from scratch without `python-multipart` missing module errors.

```powershell
# 1. Create a temporary clean virtual environment
python -m venv .venv_clean_test
.\.venv_clean_test\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify app import and Uvicorn startup
python -c "import app.main; print('App imported successfully!')"

# 4. Cleanup test venv
deactivate
Remove-Item -Recurse -Force .venv_clean_test
```

---

## 2. Automated Pytest Verification Suite

Run the full pytest suite to verify template payload creation, button click webhook extraction, and missing media_id handling:

```powershell
pytest -v tests/unit/test_whatsapp.py tests/integration/test_webhook.py tests/integration/test_daily_batch_multi_farm.py
```

Expected result: All tests pass (100% pass rate).

---

## 3. Live 24-Hour Messaging Window Verification Protocol (CRIT-005)

1. **Step 1 (Hour 0)**: Send an inbound text message ("Hello") from verified test phone number `+212...` to the Meta Sandbox bot to initiate a customer service window.
2. **Step 2 (Hour 25+)**: Do not send any further inbound messages from the test phone for at least 25 hours.
3. **Step 3 (Trigger Out-of-Window Free-Form Message)**:
   - Trigger `/jobs/daily-recommendations` while `send_text_message()` is configured.
   - Assert Meta Graph API returns error code `131026` ("Message outside the 24-hour window"). Record exact API error response payload in `research.md`.
4. **Step 4 (Trigger Template Message with Quick Reply Buttons)**:
   - Trigger `/jobs/daily-recommendations` using `send_template_message()` for template `irrigagent_daily_advisory`.
   - Confirm successful delivery (`200 OK`, `wamid...`) to test recipient device with 3 tappable Quick Reply buttons (`Approve`, `Skip`, `Modify`).
5. **Step 5 (Tap Button Response)**:
   - Tap "Approve" button on test device.
   - Verify webhook receives `button_reply` with `id: "btn_approve"` and updates recommendation status to `"approved"`.
