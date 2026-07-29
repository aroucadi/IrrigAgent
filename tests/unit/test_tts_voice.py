import asyncio
import pytest
from app.tts_voice import translate_arabizi_to_arabic_script, synthesize_darija_audio


def test_translate_arabizi_to_arabic_script():
    """Verify that Latin Arabizi or English intent strings translate to Arabic script."""
    # 1. English intent mapping
    assert translate_arabizi_to_arabic_script("approved") == "مزيان، صافي تم قبول تعديل السقي لغدا إن شاء الله."
    assert translate_arabizi_to_arabic_script("skipped") == "واخا، غادي نتجاوزو السقي د غدا."
    
    # 2. Existing Arabic script passthrough
    arabic_text = "دير ليا 10 دقايق زيادة غدا مع الـ 05:00"
    assert translate_arabizi_to_arabic_script(arabic_text) == arabic_text

    # 3. Arabizi duration and time translation
    arabizi_input = "dir 10 min zeyada at 05:00"
    translated = translate_arabizi_to_arabic_script(arabizi_input)
    assert "دقايق" in translated
    assert "زيادة" in translated


def test_synthesize_darija_audio_fallback():
    """Verify that synthesize_darija_audio produces valid non-empty byte stream in dev/test mode."""
    async def _test():
        audio_bytes = await synthesize_darija_audio("مزيان، صافي تم قبول تعديل السقي لغدا إن شاء الله.")
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0
        assert b"Opus" in audio_bytes or len(audio_bytes) > 20
    asyncio.run(_test())


def test_voice_teaser_feature_flag_gating():
    """Verify ENABLE_DARIJA_VOICE_TEASER feature flag configuration."""
    from app.config import ENABLE_DARIJA_VOICE_TEASER
    # Feature flag is boolean and off by default unless ENABLE_DARIJA_VOICE_TEASER=true
    assert isinstance(ENABLE_DARIJA_VOICE_TEASER, bool)


def test_whatsapp_audio_dispatch_pipeline():
    """Verify end-to-end media upload and audio message dispatch pipeline (upload_media -> send_audio_message)."""
    async def _test():
        from app.whatsapp import upload_media, send_audio_message
        mock_audio_bytes = b"OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00OpusHead"
        
        # 1. Upload audio media
        media_id = await upload_media(mock_audio_bytes, mime_type="audio/ogg; codecs=opus")
        assert media_id is not None
        assert len(media_id) > 0
        
        # 2. Send audio message using media_id
        res = await send_audio_message("+212600000000", media_id)
        assert res.get("messaging_product") == "whatsapp"
        assert len(res.get("messages", [])) > 0
    asyncio.run(_test())

