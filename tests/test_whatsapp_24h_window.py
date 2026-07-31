import pytest
import httpx
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

from app.whatsapp import (
    is_user_in_24h_window,
    send_template_message,
    is_meta_window_expired_error,
    send_message_with_window_fallback,
)
from app.firestore_client import save_inbound_timestamp, get_inbound_timestamp
from app.decision import format_advisory_template_params


def test_is_user_in_24h_window_active():
    """Verify window evaluates to True when last inbound message was received within 24 hours."""
    now = datetime.now(timezone.utc)
    inbound_2h_ago = (now - timedelta(hours=2)).isoformat()
    assert is_user_in_24h_window(inbound_2h_ago, now=now) is True

    inbound_23h_ago = (now - timedelta(hours=23, minutes=59)).isoformat()
    assert is_user_in_24h_window(inbound_23h_ago, now=now) is True


def test_is_user_in_24h_window_expired():
    """Verify window evaluates to False when last inbound message was received >24 hours ago or None."""
    now = datetime.now(timezone.utc)
    inbound_25h_ago = (now - timedelta(hours=25)).isoformat()
    assert is_user_in_24h_window(inbound_25h_ago, now=now) is False

    assert is_user_in_24h_window(None) is False
    assert is_user_in_24h_window("invalid_iso_string") is False


@pytest.mark.asyncio
async def test_save_and_get_inbound_timestamp():
    """Verify persistence and retrieval of inbound timestamps."""
    phone = "+212611223344"
    now_str = datetime.now(timezone.utc).isoformat()
    await save_inbound_timestamp(phone, now_str)

    retrieved = await get_inbound_timestamp(phone)
    assert retrieved == now_str
    assert is_user_in_24h_window(retrieved) is True


def test_format_advisory_template_params():
    """Verify formatting of positional template parameters [{{1}} farm, {{2}} ET0, {{3}} duration]."""
    params = format_advisory_template_params(farm_name="Ferme Hassan", et0_val=4.5, duration_str="45 min")
    assert params == ["Ferme Hassan", "4.5 mm", "45 min"]


@pytest.mark.asyncio
async def test_send_template_message_payload():
    """Verify template message dispatch payload structure."""
    res = await send_template_message(
        to="+212600000000",
        template_name="daily_irrigation_advisory",
        language_code="fr",
        parameters=["Ferme Hassan", "4.5 mm", "45 min"],
    )
    assert res.get("messaging_product") == "whatsapp"
    assert "messages" in res


def test_is_meta_window_expired_error():
    """Verify detection of Meta error code 131026 from HTTPStatusError response."""
    request = httpx.Request("POST", "https://graph.facebook.com/v21.0/messages")
    response_131026 = httpx.Response(
        status_code=400,
        json={"error": {"code": 131026, "message": "Message undeliverable. Customer service window has expired."}},
        request=request,
    )
    err = httpx.HTTPStatusError("Client error", request=request, response=response_131026)
    assert is_meta_window_expired_error(err) is True

    response_other = httpx.Response(
        status_code=400,
        json={"error": {"code": 100, "message": "Invalid parameter."}},
        request=request,
    )
    err_other = httpx.HTTPStatusError("Client error", request=request, response=response_other)
    assert is_meta_window_expired_error(err_other) is False


@pytest.mark.asyncio
async def test_send_message_with_window_fallback(monkeypatch):
    """Verify automatic fallback to template message when free-form text fails with error 131026."""
    request = httpx.Request("POST", "https://graph.facebook.com/v21.0/messages")
    response_131026 = httpx.Response(
        status_code=400,
        json={"error": {"code": 131026, "message": "Message undeliverable. Customer service window has expired."}},
        request=request,
    )
    err_131026 = httpx.HTTPStatusError("Client error", request=request, response=response_131026)

    async def mock_failing_text(to, body):
        raise err_131026

    monkeypatch.setattr("app.whatsapp.send_text_message", mock_failing_text)

    res = await send_message_with_window_fallback(
        to="+212600000000",
        text_body="Free-form message",
        template_name="daily_irrigation_advisory",
        language_code="fr",
        parameters=["Ferme Hassan", "4.5 mm", "45 min"],
    )
    assert res.get("messaging_product") == "whatsapp"
    assert "messages" in res
