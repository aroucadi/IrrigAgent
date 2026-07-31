# Research & Technical Decisions: v1.0 Farmer UX Polish, Code Quality Cleanup, and Outcome-Data Foundation

**Feature Directory**: `specs/017-farmer-ux-polish-outcome-data`  
**Date**: 2026-07-31  

---

## 1. Technical Context & Unknowns Resolution

### Decision 1.1: Interactive Button Integration for Voice Confirmation (UX-001)
- **Decision**: Update `process_voice_note()` and `process_pending_intent_reply()` to invoke `send_interactive_buttons_message()` (from WhatsApp Cloud API helper added in CRIT-005) when an active 24-hour conversation window exists.
- **Rationale**: Farmers sending a voice note are active in a 24-hour conversation window. Free-form interactive button messages can be sent immediately without WhatsApp template pre-approval.
- **Unified Path**: Incoming WhatsApp webhooks route both button tap payloads (`payload: "CONFIRM_VOICE_INTENT"` / `"CANCEL_VOICE_INTENT"`) and typed text (`"1"`, `"confirm"`, `"approve"`, `"2"`, `"cancel"`) into the same `process_pending_intent_reply()` logic in `app/decision.py`.

### Decision 1.2: Interactive Menu for `/help`, `/parcel`, `/heatmap`, and Profile Updates (UX-002 & UX-003)
- **Decision**: Implement `/help` response using WhatsApp Interactive List Messages or Button Messages (depending on item count: 3 quick reply buttons or up to 10 list options).
- **Options**:
  1. 🗺️ Field Boundary Setup (`/parcel`)
  2. 🛰️ Crop Health View (`/heatmap`)
  3. 👤 Profile & Crop Settings (`/profile`)
  4. ❓ General Info & Support (`/help`)
- **Language Localization**: Menu titles and body descriptions are dynamically generated using `preferred_language` (`fr`, `ar`/Arabizi, `en`).
- **Backward Compatibility**: Typed commands (`/help`, `/parcel`, `/heatmap`, `/stop`, `/start`) continue to be parsed directly in `app/main.py`.

### Decision 1.3: Product-Level Opt-Out & Opt-In (UX-004)
- **Decision**: Add `/stop`, `stop`, `unsubscribe`, `arreter`, `daha` detection in `app/main.py`. When received, set `opted_out: true` on the Firestore Farm Profile.
- **Batch Processing**: The daily advisory job (`POST /jobs/daily-recommendations`) queries active profiles where `opted_out != true`. Any profile with `opted_out: true` is skipped.
- **Opt-In**: Sending `/start` or any new interactive message sets `opted_out: false` and sends a "Welcome back" confirmation.

### Decision 1.4: Real Onboarding & Plain-Language Consent (UX-005)
- **Decision**: Implement explicit sequential state machine for onboarding:
  1. **Location Request**: Prompt for WhatsApp Location Pin (latitude, longitude).
  2. **Crop Type**: Present interactive buttons for supported crops (Tomatoes, Citrus, Olives, Wheat).
  3. **Field Size**: Prompt for area in hectares.
  4. **Consent Statement**: Append 2-3 sentence plain-language data rights statement to greeting and initial setup prompt.
- **Incomplete Setup Safeguard**: Profiles missing location or crop retain `onboarding_incomplete: true` flag. Daily advisories delivered to incomplete profiles append a setup reminder line: *"⚠️ Profile setup incomplete. Reply setup to specify location & crop."*

### Decision 1.5: Outcome-Feedback Quick-Reply Capture (YC Feedback / US-006)
- **Decision**: Deliver a lightweight 4-option interactive quick-reply button prompt following daily recommendation cycles within active conversation windows.
- **WhatsApp Title Limit**: Button titles MUST NOT exceed WhatsApp's 20-character title limit:
  1. `"Yes"` (or `"Followed"`) (id: `FB_YES`)
  2. `"Less"` (id: `FB_LESS`)
  3. `"More"` (id: `FB_MORE`)
  4. `"Skipped"` (id: `FB_SKIPPED`)
- **Firestore Schema**: Persist response on the `IrrigationRecommendation` document in Firestore under `outcome_feedback` (`yes`, `less`, `more`, `skipped`, or `no_response`).

---

## 2. Code Quality Fixes (SMELL-001, SMELL-002, SMELL-003)

### SMELL-001: JSON Fence Stripping in `parse_voice_intent()`
- **Issue**: `.strip("```json").strip("```")` treats characters inside the argument string as a character set to be trimmed from both ends of the target string, potentially removing valid JSON characters (e.g., `{`, `n`, `s`, `o`).
- **Fix**: Replace with explicit prefix/suffix removal using Python standard `removeprefix()` and `removesuffix()` or regex.
```python
cleaned = response.text.strip()
if cleaned.startswith("```"):
    # Strip opening fence (e.g. ```json or ```)
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    # Strip closing fence (```)
    cleaned = re.sub(r"\s*```$", "", cleaned)
```
- **Verification**: Unit test passing raw markdown JSON strings like ` ```json\n{"intent_type": "MODIFY_IRRIGATION"}\n``` ` and ensuring valid JSON extraction without character truncation.

### SMELL-002: Sentinel-2 Band Array Shape Mismatch in `fetch_sentinel2_bands()`
- **Root Cause Analysis**: `rasterio.open()` windowed reads on Red (B04) and NIR (B08) COG band assets can result in 1-pixel rounding discrepancies when computing window dimensions `from_bounds()` if the underlying raster bounds/transforms differ slightly or floating-point bounding box bounds map to fractional pixel boundaries.
- **Fix**: Calculate `target_out_shape` explicitly from the window pixel height and width, and pass `out_shape=target_out_shape` to **both** `src_red.read(1, window=window, out_shape=target_out_shape)` and `src_nir.read(1, window=window, out_shape=target_out_shape)`.
```python
win_height = int(round(window.height))
win_width = int(round(window.width))
target_out_shape = (win_height, win_width)

red_data = src_red.read(1, window=window, out_shape=target_out_shape).astype(np.float32)
nir_data = src_nir.read(1, window=window, out_shape=target_out_shape).astype(np.float32)
```
- **Verification**: Unit test asserting `red_data.shape == nir_data.shape` across non-square boundary boxes and edge-case raster transforms.

### SMELL-003: Direct Import for `google.genai` in `parse_voice_intent()`
- **Issue**: Historical dynamic import or dynamic indirection (`importlib.import_module("google.genai")`) introduces runtime overhead and hides hard dependency static analysis.
- **Fix**: Use direct static module import `from google import genai` and `from google.genai import types` at top of `app/decision.py` or within module initialization block.
- **Verification**: Static analysis and unit test verifying `parse_voice_intent()` executes without dynamic module reflection.

---

## 3. Alternatives Considered

| Alternative | Rationale for Rejection |
|---|---|
| Use WhatsApp Template Messages for Voice Confirmation | Unnecessary template approval friction and delay; voice note confirmation occurs in open 24h window where free-form interactive buttons are allowed. |
| Automatic AI parsing for location text | Lower accuracy and higher friction compared to native WhatsApp Location Pin attachment. |
| Separate Firestore collection for outcome feedback | Creates unnecessary join queries; extending existing `IrrigationRecommendation` document with `outcome_feedback` field is lightweight and efficient. |
| Default spatial resampling for all bands in SMELL-002 | Over-engineered; forcing matching `out_shape` on window reads directly resolves pixel rounding mismatches without resampling artifacts. |
