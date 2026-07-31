import pytest
import httpx
from unittest.mock import patch, MagicMock, AsyncMock
from app.whatsapp import (
    send_text_message,
    upload_media,
    extract_incoming_message,
    send_audio_message,
    send_image_message,
    download_media,
    _is_mock_token,
)


# --- Helper to create mock AsyncClient responses ---
def _mock_httpx_response(status_code: int, json_data: dict = None, content: bytes = b""):
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.content = content
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            message=f"HTTP {status_code} Error",
            request=MagicMock(spec=httpx.Request),
            response=resp,
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


# --- T003 & T004: send_text_message unit tests ---
@pytest.mark.asyncio
async def test_send_text_message_mock_mode():
    """Verify send_text_message returns mock payload when WHATSAPP_TOKEN is placeholder."""
    result = await send_text_message("+212600000001", "Hello Hassan")
    assert result["messaging_product"] == "whatsapp"
    assert result["contacts"][0]["wa_id"] == "+212600000001"
    assert result["messages"][0]["id"] == "mock_wamid_123"


@pytest.mark.asyncio
async def test_send_text_message_success(override_whatsapp_token):
    """Verify Graph API URL formatting, Bearer auth header, JSON payload schema, and 200 response."""
    mock_resp = _mock_httpx_response(
        200,
        {"messaging_product": "whatsapp", "contacts": [{"wa_id": "+212600000001"}], "messages": [{"id": "wamid.real.123"}]},
    )

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await send_text_message("+212600000001", "Hello Hassan")

    assert result["messages"][0]["id"] == "wamid.real.123"
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args

    # Verify Graph API endpoint URL
    url = call_args[0][0]
    assert "/messages" in url

    # Verify Headers (Bearer Token)
    headers = call_args[1]["headers"]
    assert headers["Authorization"] == f"Bearer {override_whatsapp_token}"
    assert headers["Content-Type"] == "application/json"

    # Verify Payload Structure
    json_payload = call_args[1]["json"]
    assert json_payload == {
        "messaging_product": "whatsapp",
        "to": "+212600000001",
        "type": "text",
        "text": {"body": "Hello Hassan"},
    }


@pytest.mark.asyncio
async def test_send_text_message_http_error(override_whatsapp_token):
    """Verify 4xx/5xx HTTP error status handling raises HTTPStatusError."""
    mock_resp = _mock_httpx_response(400, {"error": {"message": "Invalid parameter"}})

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(httpx.HTTPStatusError):
            await send_text_message("+212600000001", "Hello Hassan")


# --- T006 & T007: upload_media unit tests ---
@pytest.mark.asyncio
async def test_upload_media_mock_mode():
    """Verify upload_media returns mock_media_id when WHATSAPP_TOKEN is placeholder."""
    media_id = await upload_media(b"fake_audio_bytes")
    assert media_id == "mock_media_id_123"


@pytest.mark.asyncio
async def test_upload_media_success(override_whatsapp_token):
    """Verify multipart form payload structure, headers, and media ID extraction on 200 OK."""
    mock_resp = _mock_httpx_response(200, {"id": "media_id_real_456"})

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        media_id = await upload_media(b"binary_audio_data", mime_type="audio/ogg; codecs=opus", filename="voice.ogg")

    assert media_id == "media_id_real_456"
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args

    # Verify Graph API media endpoint URL
    url = call_args[0][0]
    assert "/media" in url

    # Verify Authorization header
    headers = call_args[1]["headers"]
    assert headers["Authorization"] == f"Bearer {override_whatsapp_token}"

    # Verify files dict passed to httpx
    files = call_args[1]["files"]
    assert "file" in files
    assert files["file"] == ("voice.ogg", b"binary_audio_data", "audio/ogg; codecs=opus")
    assert files["messaging_product"] == (None, "whatsapp")
    assert files["type"] == (None, "audio/ogg; codecs=opus")


@pytest.mark.asyncio
async def test_upload_media_http_error(override_whatsapp_token):
    """Verify HTTP status error when upload media returns 500 Internal Error."""
    mock_resp = _mock_httpx_response(500, {"error": {"message": "Internal Server Error"}})

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(httpx.HTTPStatusError):
            await upload_media(b"binary_audio_data")


# --- T008 & T009: extract_incoming_message unit tests ---
def test_extract_incoming_message_text_payload():
    """Verify extraction of text message webhook payload."""
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "212612345678",
                                    "id": "wamid.HBgLMjEyNjEyMzQ1Njc4",
                                    "type": "text",
                                    "text": {"body": "1"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    extracted = extract_incoming_message(payload)
    assert extracted is not None
    assert extracted["from"] == "212612345678"
    assert extracted["type"] == "text"
    assert extracted["text"] == "1"
    assert extracted["message_id"] == "wamid.HBgLMjEyNjEyMzQ1Njc4"


def test_extract_incoming_message_image_payload():
    """Verify extraction of image message webhook payload."""
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "212612345678",
                                    "id": "wamid.img.1001",
                                    "type": "image",
                                    "image": {"id": "media_img_888", "mime_type": "image/jpeg"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    extracted = extract_incoming_message(payload)
    assert extracted is not None
    assert extracted["from"] == "212612345678"
    assert extracted["type"] == "image"
    assert extracted["image_id"] == "media_img_888"


def test_extract_incoming_message_audio_payload():
    """Verify extraction of audio/voice message webhook payload."""
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "212612345678",
                                    "id": "wamid.audio.2002",
                                    "type": "audio",
                                    "audio": {"id": "media_audio_777", "seconds": 15},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    extracted = extract_incoming_message(payload)
    assert extracted is not None
    assert extracted["from"] == "212612345678"
    assert extracted["type"] == "audio"
    assert extracted["audio_id"] == "media_audio_777"
    assert extracted["audio_duration"] == 15


def test_extract_incoming_message_status_callback():
    """Verify non-message webhook payloads (status callbacks) return None safely."""
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "statuses": [
                                {
                                    "id": "wamid.HBgLMjEyNjEyMzQ1Njc4",
                                    "status": "delivered",
                                    "timestamp": "1722300000",
                                    "recipient_id": "212612345678",
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    extracted = extract_incoming_message(payload)
    assert extracted is None


def test_extract_incoming_message_malformed_payload():
    """Verify malformed or empty payloads evaluate to None without throwing exceptions."""
    assert extract_incoming_message({}) is None
    assert extract_incoming_message({"entry": []}) is None
    assert extract_incoming_message({"entry": [{"changes": []}]}) is None


def test_extract_incoming_message_interactive_button_reply():
    """Verify extraction of interactive quick reply button postback payload."""
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "212612345678",
                                    "id": "wamid.button.3003",
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "button_reply",
                                        "button_reply": {
                                            "id": "btn_approve",
                                            "title": "Approve",
                                        },
                                    },
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    extracted = extract_incoming_message(payload)
    assert extracted is not None
    assert extracted["from"] == "212612345678"
    assert extracted["type"] == "interactive"
    assert extracted["button_id"] == "btn_approve"
    assert extracted["text"] == "1"


@pytest.mark.asyncio
async def test_send_template_message_mock_mode():
    """Verify send_template_message returns mock payload when WHATSAPP_TOKEN is placeholder."""
    from app.whatsapp import send_template_message
    res = await send_template_message("+212600000001", "irrigagent_daily_advisory", "fr", ["Rec text", ""])
    assert res["messaging_product"] == "whatsapp"
    assert res["messages"][0]["id"] == "mock_wamid_template_999"


@pytest.mark.asyncio
async def test_send_template_message_success(override_whatsapp_token):
    """Verify Graph API template payload structure with Quick Reply button components."""
    from app.whatsapp import send_template_message
    mock_resp = _mock_httpx_response(200, {"messaging_product": "whatsapp", "messages": [{"id": "wamid.tmpl.555"}]})
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        res = await send_template_message("+212600000001", "irrigagent_daily_advisory", "fr", ["ETc rec", ""])

    assert res["messages"][0]["id"] == "wamid.tmpl.555"
    json_payload = mock_client.post.call_args[1]["json"]
    assert json_payload["type"] == "template"
    assert json_payload["template"]["name"] == "irrigagent_daily_advisory"
    assert len(json_payload["template"]["components"]) >= 2
    assert json_payload["template"]["components"][0]["type"] == "body"
    assert json_payload["template"]["components"][0]["parameters"][0]["text"] == "ETc rec"

