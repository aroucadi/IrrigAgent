# Research & Decision Log: Pre-Demo Critical Fixes

## 1. Factual Verification of 24-Hour Customer Service Window (CRIT-005)

- **Context**: Meta's WhatsApp Cloud API documentation states that free-form messages (`type: "text"`) to recipient phone numbers are rejected outside a 24-hour window from the user's last inbound message with error `131026` ("Message outside the 24-hour window").
- **Verification Decision**: Perform live verification against a verified sandbox test number by sending an inbound message, waiting 25+ hours with zero inbound traffic, and triggering a free-form message dispatch (`send_text_message`).
- **Turnaround Protection Strategy**: While the 25-hour wait period is running, proceed in parallel with unit test scaffolding, payload builder implementation (`send_template_message`), and template definition (`irrigagent_daily_advisory`), while holding final Meta template submission until verification completes.
- **Payload Design**: Meta template `irrigagent_daily_advisory` under category `UTILITY`, language `fr`, containing:
  - Header: Optional text or media header (or standard bold header)
  - Body: Parameterized recommendation text (`{{1}}` for crop & ETc calculation details, `{{2}}` for estimated weather notice if present)
  - Quick Reply Buttons: 3 embedded template components (`Approve`, `Skip`, `Modify`) with explicit button IDs (`btn_approve`, `btn_skip`, `btn_modify`).

## 2. Webhook Button Postback Payload Parsing (CRIT-005 + UX-001)

- **Context**: When a user taps a Quick Reply button on a template message, Meta Cloud API sends a webhook POST payload containing `messages[0].type = "interactive"` (or `messages[0].type = "button"` for legacy quick replies), with details in `messages[0].interactive.button_reply` or `messages[0].button`.
- **Decision**: Update `extract_incoming_message(payload)` in `app/whatsapp.py` to inspect:
  - `msg.get("type") == "interactive"` -> `msg.get("interactive", {}).get("button_reply", {}).get("id")`
  - `msg.get("type") == "button"` -> `msg.get("button", {}).get("payload")` or `msg.get("button", {}).get("text")`
  - Map `btn_approve` -> `"1"`, `btn_skip` -> `"2"`, `btn_modify` -> `"3"`.
- **Rationale**: Reusing existing downstream routing in `app/main.py` (which handles `"1"`, `"2"`, `"3"`) ensures single-source-of-truth logic for recommendation status updates without duplicate code paths.

## 3. Dependency Fix for Clean Installation (CRIT-006)

- **Context**: `app/main.py` defines `@app.post("/cropdoctor/prefilter", ... file: UploadFile = File(...))` which requires `python-multipart`.
- **Decision**: Add `python-multipart>=0.0.12` to `requirements.txt`.
- **Rationale**: `fastapi==0.115.0` requires `python-multipart` to parse `multipart/form-data` uploads. Pinned version `>=0.0.12` resolves deprecation warnings in Python 3.13 and guarantees clean virtual environment installation.

## 4. Closing the Mock-Media-ID Production Backdoor (CRIT-007)

- **Context**: `app/main.py` currently lines 156 and 273 use:
  - `audio_id = incoming.get("audio_id") or "mock_audio_1"`
  - `image_bytes = await download_media(image_id or "mock_img_1")`
  When an incoming media payload lacks `image_id` or `audio_id`, `download_media()` receives `"mock_img_1"` / `"mock_audio_1"`, detects `media_id.startswith("mock_")`, and returns canned bytes (`b"fake_high_confidence"`).
- **Decision**:
  1. In `app/main.py`, remove `or "mock_img_1"` and `or "mock_audio_1"`.
  2. If `msg_type == "image"` and `not image_id`:
     - Log internal error: `logger.error("Missing image_id in incoming webhook payload for %s: %s", sender, payload)`
     - Send friendly WhatsApp message to farmer: `"🍃 Nous n'avons pas pu lire votre photo. Merci de renvoyer une photo claire de la feuille."`
     - Return `{"status": "missing_media_id_handled"}`
  3. If `msg_type in ("audio", "voice")` and `not audio_id`:
     - Log internal error: `logger.error("Missing audio_id in incoming webhook payload for %s: %s", sender, payload)`
     - Send friendly WhatsApp message to farmer: `"🎙️ Nous n'avons pas pu lire votre message vocal. Merci de réessayer."`
     - Return `{"status": "missing_media_id_handled"}`
- **Rationale**: Aligns strictly with Constitution Rule VIII (No-Ambiguous-Mock-Fallback Rule / CRIT-007). Real production code paths never construct strings matching test-mode detectors (`"mock_"`), and farmers receive polite retry guidance.
