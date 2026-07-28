# Google Cloud TTS (ar-MA) & Voice Media Contract

**Branch**: `001-hassan-irrigation-agent` | **Date**: 2026-07-28 | **Spec**: [spec.md](../spec.md)

## Service Interface: `TTSVoiceWrapper`

Python abstraction wrapping Google Cloud Text-to-Speech API (`google-cloud-texttospeech`).

### Method Signature

```python
async def synthesize_darija_audio(
    arabic_script_text: str,
    output_filename: str | None = None
) -> bytes:
    """
    Synthesizes Arabic-script Darija text to OGG OPUS audio bytes.
    
    Args:
        arabic_script_text: Moroccan Darija string formatted in Arabic script 
                            (e.g., 'دير ليا 10 دقايق زيادة غدا مع الـ 05:00').
        output_filename: Optional local path to write bytes.
        
    Returns:
        bytes: Raw OGG_OPUS audio byte stream.
        
    Raises:
        TTSSynthesisError: If GCP TTS API fails or returns non-zero error code.
    """
```

### Synthesis Configuration

- **Language Code**: `ar-MA` (Moroccan Arabic)
- **Audio Encoding**: `AudioEncoding.OGG_OPUS`
- **Voice Parameters**: `ssml_gender = texttospeech.SsmlVoiceGender.MALE` or `FEMALE` standard `ar-MA` voice

---

## Meta WhatsApp Audio Transmission Contract

Function: `send_audio_message(to_phone_number: str, audio_bytes: bytes)`

### Workflow Steps:
1. **Media Staging**: Write `audio_bytes` to temporary file `/tmp/voice_<id>.ogg`.
2. **Media Upload (`POST https://graph.facebook.com/v20.0/<PHONE_NUMBER_ID>/media`)**:
   - `messaging_product: whatsapp`
   - `type: audio/ogg; codecs=opus`
   - Returns `{"id": "<MEDIA_ID>"}`.
3. **Send Audio Message (`POST https://graph.facebook.com/v20.0/<PHONE_NUMBER_ID>/messages`)**:
   ```json
   {
     "messaging_product": "whatsapp",
     "recipient_type": "individual",
     "to": "212600000000",
     "type": "audio",
     "audio": {
       "id": "<MEDIA_ID>"
     }
   }
   ```
4. **Cleanup**: Remove temporary file `/tmp/voice_<id>.ogg`.
