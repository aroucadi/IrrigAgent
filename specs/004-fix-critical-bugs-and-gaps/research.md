# Research: 004-fix-critical-bugs-and-gaps

## 1. CropDoctor Mock Detection Collision Fix

### Problem
In `app/cropdoctor.py`:
```python
elif image_bytes == b"fake_high_confidence" or force_confidence is not None or image_bytes.startswith(b"\xFF\xD8\xFF\xE0"):
```
`\xFF\xD8\xFF\xE0` is the standard JFIF JPEG file signature. Matching `image_bytes.startswith(b"\xFF\xD8\xFF\xE0")` forces every real JFIF JPEG leaf photo uploaded by real farmers to bypass Gemini AI vision and return hardcoded mock diagnoses (`phytophthora_infestans`, 0.85 confidence).

### Decision
Scope mock detection strictly to:
1. Exact byte equality for test fixtures (`image_bytes == b"fake_high_confidence"`).
2. Environment test flag or mock header pass-through (`force_confidence is not None`).
Remove the generic JPEG magic bytes check `startswith(b"\xFF\xD8\xFF\xE0")`.

### Rationale
Real mobile camera photos uploaded via WhatsApp will start with `\xFF\xD8\xFF\xE0` (JFIF) or `\xFF\xD8\xFF\xE1` (EXIF). Removing the generic file signature check ensures all real images reach the Gemini 1.5 Flash vision model API in production while allowing automated pytest unit tests to pass using explicit mock byte sequences.

---

## 2. Arabizi Clock-Time Exclusion

### Problem
The Arabizi regex check matches digits adjacent to letters (e.g. `3`, `7`, `9`). Clock-time indicators like `07h00` or `19h00` contain `h` adjacent to digits (`7h0`, `9h0`), causing incoming/outgoing schedule messages to falsely trigger Darija script switching.

### Decision
Modify the language detection utility (`detect_arabizi_or_arabic_strict` in `app/firestore_client.py`) to strip or bypass clock-time patterns matching `\b\d{1,2}h\d{2}\b` (e.g. `07h00`, `19h00`, `06h30`) prior to evaluating digit-letter Arabizi triggers.

### Rationale
Clock times are standard format specifiers across both French and Darija text messages in Morocco. Stripping clock-time tokens before evaluating Arabizi digit rules prevents false-positive language flips.

---

## 3. Darija Voice Teaser Scope & WhatsApp Media Delivery

### Problem
Voice output (TTS) was introduced in `app/tts_voice.py` and `requirements.txt` (`google-cloud-texttospeech`). Per Constitution v1.4.0, voice output is permitted as an optional feature flag (`ENABLE_DARIJA_VOICE_TEASER=true`) sequenced after core text loop validation.

### Decision
1. Retain `ENABLE_DARIJA_VOICE_TEASER` as an opt-in environment flag (disabled by default in production demo runs until core text loop & CropDoctor are pilot-validated).
2. Ensure voice synthesis executes asynchronously in background tasks without blocking sub-second text replies.
3. Validate end-to-end WhatsApp audio delivery path (`upload_media` -> `send_audio_message` with OGG/OPUS audio content) against Meta Cloud API sandbox endpoint.

---

## 4. FarmProfile Schema Reconcillation

### Problem
`app/schemas.py` defines a `FarmProfile` Pydantic model with fields (`phone`, `region`, `crop`, `flow_rate_lph`, `baseline_minutes`) that do not match the profile dictionary used in `main.py` and `app/firestore_client.py` (`phone_number`, `location`, `crop_type`, `acreage_hectares`, `preferred_language`).

### Decision
Update `FarmProfile` in `app/schemas.py`:
```python
class FarmProfile(BaseModel):
    phone_number: str
    location: str
    crop_type: str
    acreage_hectares: float = Field(gt=0)
    preferred_language: str = Field(default="fr")
```
Wire `FarmProfile.model_validate()` into `parse_profile_command` and profile update handling in `main.py` so profile updates are validated cleanly before persistence.
