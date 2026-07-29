# Interface Contract: WhatsApp Webhook & Profile Interaction API

## Endpoints Exposed

### 1. WhatsApp Inbound Webhook
- **URL**: `POST /webhook`
- **Payload**: Meta WhatsApp Cloud API standard webhook payload
- **Supported Commands**:
  - `profile` / `mon profil`: Returns current farm profile attributes.
  - `update crop <crop_name>`: Updates primary crop type.
  - `update area <N> ha`: Updates farm acreage in hectares.
  - Photo attachment (image/jpeg): Routes to CropDoctor vision triage.

---

### 2. Profile Update Parser Contract (`app/firestore_client.py`)
- **Function**: `parse_profile_command(text: str) -> Optional[Dict[str, Any]]`
- **Behavior**:
  - Input: Raw WhatsApp text message (e.g. `"update crop tomatoes"`, `"update area 10 ha"`).
  - Validation: Validates parsed dict against `FarmProfile` Pydantic model (`app/schemas.py`).
  - Returns: Dict containing updated field(s) or `None` if message is not a profile command.

---

### 3. Voice Teaser Integration Contract (`app/tts_voice.py` & `app/whatsapp.py`)
- **Function**: `synthesize_darija_audio(text: str) -> Optional[bytes]`
- **Flag**: Controlled by `ENABLE_DARIJA_VOICE_TEASER=true` environment variable.
- **WhatsApp Media Dispatch**:
  - Step 1: `upload_media(file_bytes: bytes, mime_type: "audio/ogg; codecs=opus") -> str (media_id)`
  - Step 2: `send_audio_message(to_phone: str, media_id: str)`
- **Failure Contract**: If TTS fails or flag is `false`, message flow proceeds with text reply silently without erroring.
