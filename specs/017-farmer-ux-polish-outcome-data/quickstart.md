# Quickstart & Verification Guide: v1.0 Farmer UX Polish, Code Quality Cleanup, and Outcome-Data Foundation

**Feature Directory**: `specs/017-farmer-ux-polish-outcome-data`  
**Date**: 2026-07-31  

---

## 1. Automated Unit & Integration Tests

Execute the full suite and targeted tests using `pytest`:

```bash
# Run all tests (must maintain zero broken tests policy per Constitution VIII)
pytest tests/

# Run targeted unit tests for Feature 017
pytest tests/unit/test_voice_darija_stt.py -k "test_process_pending_intent"
pytest tests/unit/test_help_menu_buttons.py
pytest tests/unit/test_opt_out_flow.py
pytest tests/unit/test_onboarding_consent.py
pytest tests/unit/test_outcome_feedback.py
pytest tests/unit/test_sentinel_canopy_heatmap.py -k "test_fetch_sentinel2_bands_shape"
```

---

## 2. Verification Scenarios & Expected Outcomes

### Scenario 2.1: Voice Intent Confirmation Buttons (US1 / FR-001 / FR-002)
- **Action**: Trigger a voice note processing that sets `status="AWAITING_CONFIRMATION"`. Send WhatsApp interactive button payload tap (`id="CONFIRM_VOICE_INTENT"`) or text (`"1"`).
- **Expected Outcome**: Pending intent resolves to `status="CONFIRMED"`, irrigation adjustment applies, and no divergent code path exists.

### Scenario 2.2: Menu-Driven Help & Slash Command Triggers (US2 & US3 / FR-003 to FR-006)
- **Action**: Send `/help`, `help`, or `menu` to the webhook.
- **Expected Outcome**: Returns interactive menu message containing `/parcel`, `/heatmap`, and profile update buttons/list options localized to the user's preferred language (`fr`, `ar`, `en`). Daily advisory closing message includes hint: `"Reply help anytime for options"`.

### Scenario 2.3: Product-Level Opt-Out & Opt-In (US4 / FR-007 to FR-009)
- **Action**: Send `/stop` or `stop`. Then execute `POST /jobs/daily-recommendations`. Send `/start`.
- **Expected Outcome**:
  - Profile updated to `opted_out: true` and receives opt-out acknowledgment.
  - Daily batch recommendation run skips the opted-out farm profile.
  - Sending `/start` resets `opted_out: false` and sends welcome-back acknowledgment.

### Scenario 2.4: Real Onboarding Data Collection & Explicit Data Consent (US5 / FR-010 to FR-012)
- **Action**: Send initial message from a new phone number. Progress through location pin submission, crop selection, and area input.
- **Expected Outcome**:
  - Onboarding greeting includes 2-3 sentence explicit data rights/usage consent text.
  - Profile saved with real location coordinates, crop, and field size without silent Agadir/tomato defaults.
  - Incomplete profile receives `onboarding_incomplete: true` flag and daily setup reminder line.

### Scenario 2.5: Outcome-Feedback Quick-Reply Capture (US6 / FR-013 & FR-014)
- **Action**: Simulate active conversation window touchpoint following an advisory cycle. Tap quick-reply button `"Yes"` / `FB_YES` or `"Less"` / `FB_LESS`.
- **Expected Outcome**: Firestore `IrrigationRecommendation` document updated with `outcome_feedback: "yes"` or `"less"`. Non-responses default cleanly to `no_response`.

### Scenario 2.6: Code Quality Fix Verification (US7 / FR-015 to FR-017)
- **Action**: Run SMELL-001 (markdown code fence stripping), SMELL-002 (Sentinel-2 band array shape alignment with `out_shape`), and SMELL-003 (direct `google.genai` import) tests.
- **Expected Outcome**:
  - `parse_voice_intent()` correctly parses JSON wrapped in ```json fences without stripping structural JSON characters.
  - `fetch_sentinel2_bands()` outputs `red_data` and `nir_data` arrays with identical `.shape` tuple.
  - Direct static import of `google.genai` executes cleanly without dynamic `importlib` reflection.
