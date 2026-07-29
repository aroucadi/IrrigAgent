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

---

## 2. Arabizi Clock-Time Exclusion

### Problem
The Arabizi regex check matches digits adjacent to letters (e.g. `3`, `7`, `9`). Clock-time indicators like `07h00` or `19h00` contain `h` adjacent to digits (`7h0`, `9h0`), causing incoming/outgoing schedule messages to falsely trigger Darija script switching.

### Decision
Modify the language detection utility (`detect_arabizi_or_arabic_strict` in `app/firestore_client.py`) to strip or bypass clock-time patterns matching `\b\d{1,2}h\d{2}\b` (e.g. `07h00`, `19h00`, `06h30`) prior to evaluating digit-letter Arabizi triggers.

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
    location: Optional[Any] = Field(default="Agadir")
    crop_type: str = Field(default="tomatoes")
    acreage_hectares: float = Field(default=10.0, gt=0)
    preferred_language: str = Field(default="french")
```
Wire `FarmProfile.model_validate()` into `save_farm_profile` in `app/firestore_client.py`.

---

## 5. Strict Crop Catalog Fallback Elimination & README Safety Claims

### Problem
In `app/cropdoctor.py`:
```python
crop_catalog = ONSSA_STATIC_CATALOG.get(crop_type.lower(), ONSSA_STATIC_CATALOG["tomatoes"])
```
If a farmer grows an unsupported crop (e.g. `olives`, `wheat`), `lookup_onssa_product()` silently falls back to `ONSSA_STATIC_CATALOG["tomatoes"]`, returning tomato chemical pointers for non-tomato crops.

### Decision
1. Fail closed: If `crop_type.lower()` is not in `ONSSA_STATIC_CATALOG`, return `None`:
```python
crop_catalog = ONSSA_STATIC_CATALOG.get(crop_type.lower())
if not crop_catalog:
    return None
```
2. When `lookup_onssa_product()` returns `None`, omit chemical product pointers across all confidence tiers (including High confidence >= 75%) and instruct the farmer to consult an ONSSA-authorized retailer.
3. Revise `README.md` safety claim: State that product names are retrieved exclusively from a static, human-verified lookup table scoped to pilot crops (tomatoes, citrus) without substituting treatment recommendations for unsupported crops. Explicitly note that model confidence scores are uncalibrated self-reports.
