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
