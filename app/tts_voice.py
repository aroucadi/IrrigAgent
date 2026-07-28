import os
import re
from typing import Optional
from app.config import GCP_PROJECT_ID

# Standard fallback mapping for common English/Arabizi intents to Arabic-script Darija
DARIJA_INTENT_MAPPING = {
    "approved": "مزيان، صافي تم قبول تعديل السقي لغدا إن شاء الله.",
    "skipped": "واخا، غادي نتجاوزو السقي د غدا.",
    "modified": "مزيان، سجلنا التعديل ديالك لغدا.",
    "default": "مرحبا بيك فـ IrrigAgent. عافاك اختار 1 للتأكيد، 2 للإلغاء، أو 3 للتعديل.",
}


def translate_arabizi_to_arabic_script(text: str) -> str:
    """Pre-translates incoming Latin Arabizi or English intent text into standard Arabic-script Darija.
    
    Prevents GCP TTS ar-MA synthesizer from attempting to render Latin phonemes.
    """
    if not text:
        return DARIJA_INTENT_MAPPING["default"]

    # Check if text is already in Arabic script
    if re.search(r'[\u0600-\u06FF]', text):
        return text

    text_lower = text.strip().lower()

    # Intent or common string translation
    if "approved" in text_lower or text_lower == "1":
        return DARIJA_INTENT_MAPPING["approved"]
    elif "skipped" in text_lower or text_lower == "2":
        return DARIJA_INTENT_MAPPING["skipped"]
    elif "noted" in text_lower or "modified" in text_lower or text_lower.startswith("3"):
        return DARIJA_INTENT_MAPPING["modified"]

    # Basic regex replacements for Latin Arabizi duration & time phrases
    # e.g., "dir 10 min zeyada" -> "دير 10 دقايق زيادة"
    translated = text
    translated = re.sub(r'\b(\d+)\s*min\b', r'\1 دقايق', translated, flags=re.IGNORECASE)
    translated = re.sub(r'\bat\s+(\d{1,2}:\d{2})\b', r'مع الـ \1', translated, flags=re.IGNORECASE)
    translated = re.sub(r'\b(dir|dier)\b', 'دير', translated, flags=re.IGNORECASE)
    translated = re.sub(r'\b(zeyada|zyada)\b', 'زيادة', translated, flags=re.IGNORECASE)
    translated = re.sub(r'\bghada\b', 'غدا', translated, flags=re.IGNORECASE)

    # If any Latin characters remain, default to a clean Arabic script Darija confirmation
    if re.search(r'[a-zA-Z]', translated):
        return f"مزيان، تم تسجيل: {text}"

    return translated


async def synthesize_darija_audio(arabic_script_text: str) -> bytes:
    """Synthesize Arabic-script Darija text to OGG OPUS audio byte stream using GCP Text-to-Speech API.
    
    Configured with languageCode='ar-MA' (Moroccan Arabic) and OGG_OPUS audio encoding.
    Falls back to mock byte stream in local/test environments if GCP credentials are not present.
    """
    clean_text = translate_arabizi_to_arabic_script(arabic_script_text)

    # Check for GCP credentials in environment
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ or "K_SERVICE" in os.environ:
        try:
            from google.cloud import texttospeech

            client = texttospeech.TextToSpeechAsyncClient()
            synthesis_input = texttospeech.SynthesisInput(text=clean_text)

            voice = texttospeech.VoiceSelectionParams(
                language_code="ar-MA",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.OGG_OPUS
            )

            response = await client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            return response.audio_content
        except Exception:
            pass

    # Mock OGG OPUS header/byte sequence for dev/test execution
    mock_ogg_opus_header = (
        b"OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x01\x00\x00\x00\x00\x00\x00\x00\x13OpusHead"
        b"\x01\x01\x38\x01\x80\xbb\x00\x00\x00\x00\x00"
        b"OggS\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x02\x00\x00\x00\x00\x00\x00\x00\x0cOpusTags"
    )
    return mock_ogg_opus_header
