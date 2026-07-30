# Quickstart & Verification Guide: Voice-to-Intent Darija STT Safety Policy & Confirmation Prompts

## Overview

This guide details how to run and verify the **Voice-to-Intent Darija STT (Tier 1 Safety Policy & Confirmation Prompts)** feature using unit tests and end-to-end API payloads.

---

## Prerequisites

- **Python**: 3.11+ environment with virtual environment active
- **Dependencies**: Installed via `requirements.txt` (`pytest`, `fastapi`, `google-cloud-firestore`, `vertexai`)
- **Environment Variables**:
  - `ENABLE_DARIJA_VOICE_TEASER=true` (or `false` to verify text-only confirmation)
  - `WHATSAPP_TOKEN=test_sandbox_token`
  - `FIRESTORE_EMULATOR_HOST=localhost:8080` (or mock Firestore client)

---

## Validation Scenarios

### Scenario 1: High-Confidence Voice Note ($\ge 0.80$)
1. **Action**: Submit an audio voice note payload to the webhook endpoint with simulated ASR confidence score $= 0.85$ (e.g. transcript: `"Zid 15 minutes f l'arrosage stp"`).
2. **Verification**:
   - Check that a pending intent is persisted in Firestore under `pending_intents/pending_<phone>` with `status = "pending"` and `expires_at = created_at + 15 min`.
   - Verify WhatsApp outgoing message payload contains: `"I heard: Increase irrigation by +15 min. Reply 1 to CONFIRM or 2 to CANCEL."`
   - Verify NO irrigation state modification has occurred yet (Zero Direct Execution policy satisfied).

### Scenario 2: Explicit Confirmation Loop (Farmer Replies '1' vs '2' vs '3')
1. **Action (Confirm)**: Submit incoming text message `'1'` from the same phone number.
2. **Verification**:
   - Verify pending intent status updates to `"confirmed"`.
   - Verify requested irrigation schedule (+15 min) is committed.
3. **Action (Cancel)**: Submit incoming text message `'2'` for a new pending intent.
4. **Verification**:
   - Verify pending intent status updates to `"canceled"`.
   - Verify no irrigation schedule change is committed.
5. **Action (Discard & Menu)**: Submit incoming text message `'3'` for a new pending intent.
6. **Verification**:
   - Verify pending intent is marked `"canceled"` / discarded and main text menu is returned.

### Scenario 3: Low-Confidence Voice Note ($< 0.80$)
1. **Action**: Submit a voice note with simulated confidence score $= 0.65$ or unparseable audio.
2. **Verification**:
   - Verify NO pending intent record is written to Firestore.
   - Verify WhatsApp outgoing message contains the fallback text menu: `"I couldn't hear clearly. Please reply: 1 - Approve (+15 min), 2 - Skip today, 3 - Modify"`.

### Scenario 4: Audio Duration Bounding (>60 Seconds)
1. **Action**: Submit a voice note audio payload with duration $= 75$ seconds.
2. **Verification**:
   - Verify ASR transcription is skipped prior to call.
   - Verify outgoing response asks the farmer to send a shorter voice note (under 60s) or text message.

### Scenario 5: 15-Minute Expiration TTL
1. **Action**: Create a pending intent document in Firestore with `created_at` timestamp set 16 minutes in the past. Submit text reply `'1'`.
2. **Verification**:
   - Verify reply `'1'` is rejected with a message stating that the intent proposal has expired.
   - Verify pending intent status updates to `"expired"`.

---

## Running Automated Verification Commands

Execute the test suite verifying safety policy, state machine transitions, and duration bounds:

```bash
# Run pytest on voice intent safety tests
pytest tests/unit/test_voice_darija_stt.py -v
```

---

## Artifact References

- [Specification](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/009-voice-darija-stt-safety/spec.md)
- [Data Model](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/009-voice-darija-stt-safety/data-model.md)
- [Contract Schema](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/009-voice-darija-stt-safety/contracts/whatsapp_voice_intent.json)
