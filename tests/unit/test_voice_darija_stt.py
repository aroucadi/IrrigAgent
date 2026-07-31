import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.firestore_client import (
    save_pending_intent,
    get_pending_intent,
    update_pending_intent_status,
    delete_pending_intent,
    _IN_MEMORY_PENDING_INTENTS,
)
from app.decision import (
    process_voice_note,
    process_pending_intent_reply,
    parse_voice_intent,
)


@pytest.fixture(autouse=True)
def clear_pending_intents_store():
    _IN_MEMORY_PENDING_INTENTS.clear()
    yield
    _IN_MEMORY_PENDING_INTENTS.clear()


@pytest.mark.asyncio
async def test_pending_intent_save_and_retrieve():
    phone = "+212611111111"
    intent_data = {
        "intent_type": "MODIFY_IRRIGATION",
        "proposed_adjustment_minutes": 15,
        "confidence_score": 0.88,
        "transcribed_text": "Zid 15 dqiqa f l-sqi ghadan",
    }
    
    saved = await save_pending_intent(phone, intent_data)
    assert saved is not None
    assert "pending_voice_intent" in saved
    payload = saved["pending_voice_intent"]
    assert payload["confidence_score"] == 0.88
    assert payload["proposed_adjustment_minutes"] == 15
    assert payload["status"] == "AWAITING_CONFIRMATION"

    retrieved = await get_pending_intent(phone)
    assert retrieved is not None
    assert retrieved["pending_voice_intent"]["status"] == "AWAITING_CONFIRMATION"


@pytest.mark.asyncio
async def test_high_confidence_voice_note_processing():
    phone = "+212622222222"
    audio_bytes = b"fake_high_confidence_audio"
    
    prompt_text, allow_tts = await process_voice_note(phone, audio_bytes, duration_seconds=15)
    assert "Voice Request Heard" in prompt_text
    assert "Reply:" in prompt_text
    assert "1 - CONFIRM" in prompt_text

    pending = await get_pending_intent(phone)
    assert pending is not None
    payload = pending["pending_voice_intent"]
    assert payload["status"] == "AWAITING_CONFIRMATION"
    assert payload["confidence_score"] >= 0.80


@pytest.mark.asyncio
async def test_confirmation_reply_option_1_and_2():
    phone = "+212633333333"
    audio_bytes = b"fake_high_confidence_audio"
    await process_voice_note(phone, audio_bytes, duration_seconds=10)

    # Test reply '1' -> Confirm
    handled, reply = await process_pending_intent_reply(phone, "1")
    assert handled is True
    assert "Voice intent confirmed" in reply
    
    pending = await get_pending_intent(phone)
    assert pending["pending_voice_intent"]["status"] == "CONFIRMED"

    # Test new intent and reply '2' -> Cancel
    phone2 = "+212633333334"
    await process_voice_note(phone2, audio_bytes, duration_seconds=10)
    handled2, reply2 = await process_pending_intent_reply(phone2, "2")
    assert handled2 is True
    assert "Voice intent canceled" in reply2

    pending2 = await get_pending_intent(phone2)
    assert pending2["pending_voice_intent"]["status"] == "CANCELED"


@pytest.mark.asyncio
async def test_discard_option_3():
    phone = "+212644444444"
    audio_bytes = b"fake_high_confidence_audio"
    await process_voice_note(phone, audio_bytes, duration_seconds=10)

    handled, reply = await process_pending_intent_reply(phone, "3")
    assert handled is True
    assert "Voice intent discarded" in reply
    assert "Main Menu" in reply

    pending = await get_pending_intent(phone)
    assert pending["pending_voice_intent"]["status"] == "CANCELED"


@pytest.mark.asyncio
async def test_low_confidence_voice_note_fallback():
    phone = "+212655555555"
    audio_bytes = b"fake_low_confidence"

    prompt_text, allow_tts = await process_voice_note(phone, audio_bytes, duration_seconds=10)
    assert "couldn't hear clearly" in prompt_text
    assert allow_tts is False

    pending = await get_pending_intent(phone)
    assert pending is None


@pytest.mark.asyncio
async def test_audio_duration_cap_exceeded():
    phone = "+212666666666"
    audio_bytes = b"long_audio_bytes"

    prompt_text, allow_tts = await process_voice_note(phone, audio_bytes, duration_seconds=75)
    assert "exceeds maximum allowed duration (60 seconds)" in prompt_text

    pending = await get_pending_intent(phone)
    assert pending is None


@pytest.mark.asyncio
async def test_non_numeric_reply_keeps_pending_intent_active():
    phone = "+212677777777"
    audio_bytes = b"fake_high_confidence_audio"
    await process_voice_note(phone, audio_bytes, duration_seconds=10)

    # Farmer sends "salam" instead of 1/2/3
    handled, reply = await process_pending_intent_reply(phone, "salam")
    assert handled is True
    assert "active pending voice request awaiting confirmation" in reply

    # Pending intent should STILL be active
    pending = await get_pending_intent(phone)
    assert pending["pending_voice_intent"]["status"] == "AWAITING_CONFIRMATION"


@pytest.mark.asyncio
async def test_expired_pending_intent_rejection():
    phone = "+212688888888"
    now_utc = datetime.now(timezone.utc)
    past_time = (now_utc - timedelta(minutes=20)).isoformat()

    intent_payload = {
        "intent_type": "MODIFY_IRRIGATION",
        "proposed_adjustment_minutes": 15,
        "confidence_score": 0.88,
        "transcribed_text": "Zid 15 min",
        "created_at": past_time,
        "expires_at": (now_utc - timedelta(minutes=5)).isoformat(),
        "status": "AWAITING_CONFIRMATION"
    }
    await save_pending_intent(phone, intent_payload)

    # Farmer replies '1' after 20 minutes
    handled, reply = await process_pending_intent_reply(phone, "1")
    assert handled is True
    assert "expired" in reply.lower()


def test_webhook_voice_note_endpoint_integration():
    client = TestClient(app)
    
    # Send incoming audio webhook message
    voice_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WHATSAPP_ACCOUNT_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "15550431424", "phone_number_id": "105954558954427"},
                    "messages": [{
                        "from": "212699999999",
                        "id": "wamid.HBgLMjEyNjk5OTk5OTk5FQIAERgSQjU1RjU1RjU1RjU1RjU1RjUA",
                        "timestamp": "1722271800",
                        "type": "audio",
                        "audio": {"id": "mock_audio_media_123", "mime_type": "audio/ogg; codecs=opus", "seconds": 12}
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    resp = client.post("/webhook", json=voice_payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "voice_note_processed"

    # Now send confirmation reply '1'
    reply_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WHATSAPP_ACCOUNT_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "15550431424", "phone_number_id": "105954558954427"},
                    "messages": [{
                        "from": "212699999999",
                        "id": "wamid.HBgLMjEyNjk5OTk5OTk5FQIAERgSQjU1RjU1RjU1RjU1RjU1RjUB",
                        "timestamp": "1722271810",
                        "type": "text",
                        "text": {"body": "1"}
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    resp2 = client.post("/webhook", json=reply_payload)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "pending_intent_reply_processed"


@pytest.mark.asyncio
async def test_anti_mock_regression_voice_intent():
    """Verify parse_voice_intent produces dynamic outputs for different realistic mocked ASR responses (BUG-001)."""
    from unittest.mock import MagicMock, patch

    mock_response_1 = MagicMock()
    mock_response_1.text = '{"transcribed_text": "Zid 20 dqiqa f l-sqi", "confidence_score": 0.92, "intent_type": "INCREASE_IRRIGATION", "proposed_adjustment_minutes": 20}'

    mock_response_2 = MagicMock()
    mock_response_2.text = '{"transcribed_text": "Nqs 10 dqiqa", "confidence_score": 0.85, "intent_type": "DECREASE_IRRIGATION", "proposed_adjustment_minutes": 10}'

    with patch("google.genai.Client") as mock_client_cls:
        mock_client_instance = mock_client_cls.return_value
        mock_client_instance.models.generate_content.side_effect = [mock_response_1, mock_response_2]

        conf1, text1, action1 = await parse_voice_intent(b"realistic_audio_payload_alpha", 15)
        conf2, text2, action2 = await parse_voice_intent(b"realistic_audio_payload_beta", 15)

        # Assert two dynamic inputs produced distinct transcripts & confidence scores
        assert text1 == "Zid 20 dqiqa f l-sqi"
        assert text2 == "Nqs 10 dqiqa"
        assert text1 != text2
        assert conf1 == 0.92
        assert conf2 == 0.85
        assert conf1 != conf2
        assert action1["intent_type"] == "INCREASE_IRRIGATION"
        assert action1["proposed_adjustment_minutes"] == 20
        assert action2["intent_type"] == "DECREASE_IRRIGATION"
        assert action2["proposed_adjustment_minutes"] == 10


@pytest.mark.asyncio
async def test_voice_intent_api_failure_degradation():
    """Verify real API failure (timeout, exception) degrades safely to low confidence fallback."""
    from unittest.mock import patch

    with patch("google.genai.Client") as mock_client_cls:
        mock_client_instance = mock_client_cls.return_value
        mock_client_instance.models.generate_content.side_effect = Exception("Vertex AI API Timeout")

        conf, text, action = await parse_voice_intent(b"real_audio_bytes_error_case", 15)
        assert conf == 0.0
        assert text == "ASR_FAILURE"
        assert action is None


@pytest.mark.asyncio
async def test_smell_001_markdown_fence_stripping():
    """SMELL-001: Verify markdown code fence JSON parsing handles ```json and ``` fences without character stripping corruption."""
    from unittest.mock import MagicMock, patch

    mock_resp = MagicMock()
    mock_resp.text = '```json\n{"transcribed_text": "Sqi 15 min", "confidence_score": 0.89, "intent_type": "MODIFY_IRRIGATION", "proposed_adjustment_minutes": 15}\n```'

    with patch("google.genai.Client") as mock_client_cls:
        mock_client_instance = mock_client_cls.return_value
        mock_client_instance.models.generate_content.return_value = mock_resp

        conf, text, action = await parse_voice_intent(b"sample_fence_audio", 10)
        assert conf == 0.89
        assert text == "Sqi 15 min"
        assert action["proposed_adjustment_minutes"] == 15


@pytest.mark.asyncio
async def test_smell_003_direct_genai_import():
    """SMELL-003: Verify direct static import of google.genai is used without importlib indirection."""
    import app.decision as decision_module
    assert hasattr(decision_module, "genai")
    assert hasattr(decision_module, "types")


def test_voice_confirmation_button_tap_equivalence():
    """US1: Verify interactive button tap (CONFIRM_VOICE_INTENT) resolves identically to typed text '1'."""
    client = TestClient(app)
    
    # 1. Send voice note webhook
    voice_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WHATSAPP_ACCOUNT_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "15550431424", "phone_number_id": "105954558954427"},
                    "messages": [{
                        "from": "212688776655",
                        "id": "wamid.voice123",
                        "timestamp": "1722271800",
                        "type": "audio",
                        "audio": {"id": "mock_audio_media_123", "mime_type": "audio/ogg; codecs=opus", "seconds": 12}
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    resp1 = client.post("/webhook", json=voice_payload)
    assert resp1.status_code == 200

    # 2. Tap CONFIRM_VOICE_INTENT button
    button_tap_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WHATSAPP_ACCOUNT_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "15550431424", "phone_number_id": "105954558954427"},
                    "messages": [{
                        "from": "212688776655",
                        "id": "wamid.btn456",
                        "timestamp": "1722271810",
                        "type": "interactive",
                        "interactive": {
                            "type": "button_reply",
                            "button_reply": {"id": "CONFIRM_VOICE_INTENT", "title": "Confirm"}
                        }
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    resp2 = client.post("/webhook", json=button_tap_payload)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "pending_intent_reply_processed"


