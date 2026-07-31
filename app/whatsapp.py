import httpx
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Union
from app.config import WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, GRAPH_API_VERSION

GRAPH_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
MESSAGES_URL = f"{GRAPH_BASE_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"


def _is_mock_token(token: str) -> bool:
    if not token:
        return True
    lower_token = token.lower()
    return any(lower_token.startswith(prefix) for prefix in ["eaag_your_", "your_", "mock_", "test_"])


async def send_text_message(to: str, body: str) -> Dict[str, Any]:
    """Send a plain text WhatsApp message to a recipient."""
    if _is_mock_token(WHATSAPP_TOKEN):
        # Mock mode if token is not set or placeholder
        return {"messaging_product": "whatsapp", "contacts": [{"wa_id": to}], "messages": [{"id": "mock_wamid_123"}]}

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(MESSAGES_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()


async def download_media(media_id: str) -> bytes:
    """Retrieve media binary bytes from Meta Graph API using media_id."""
    if _is_mock_token(WHATSAPP_TOKEN) or media_id.startswith("mock_"):
        # Return mock high confidence bytes for unit/integration testing
        return b"fake_high_confidence"


    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    media_info_url = f"{GRAPH_BASE_URL}/{media_id}"
    
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(media_info_url, headers=headers)
        resp.raise_for_status()
        media_url = resp.json().get("url")
        if not media_url:
            raise ValueError("Media URL not found in Graph API response")
        
        media_resp = await client.get(media_url, headers=headers)
        media_resp.raise_for_status()
        return media_resp.content


def extract_incoming_message(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract sender number, text body, image ID, location attachment, or interactive button reply from Meta webhook POST payload."""
    try:
        entry = payload["entry"][0]
        change = entry["changes"][0]["value"]
        messages = change.get("messages")
        if not messages:
            return None  # Status callback, not a user message

        msg = messages[0]
        msg_type = msg.get("type")

        sender = msg.get("from")
        text_body = msg.get("text", {}).get("body") if msg_type == "text" else None
        
        # Parse interactive or quick-reply button postbacks
        button_id = None
        button_title = None
        if msg_type == "interactive":
            interactive = msg.get("interactive", {})
            if interactive.get("type") == "button_reply":
                btn_reply = interactive.get("button_reply", {})
                button_id = btn_reply.get("id")
                button_title = btn_reply.get("title")
        elif msg_type == "button":
            btn = msg.get("button", {})
            button_id = btn.get("payload") or btn.get("text")
            button_title = btn.get("text")

        if button_id:
            button_map = {
                "btn_approve": "1",
                "btn_confirm": "1",
                "btn_skip": "2",
                "btn_cancel": "2",
                "btn_modify": "3",
                "btn_discard": "3",
            }
            text_body = button_map.get(button_id, button_id)

        image_id = msg.get("image", {}).get("id") if msg_type == "image" else None
        location_data = msg.get("location") if msg_type == "location" else None
        audio_obj = msg.get("audio") or msg.get("voice") or {}
        audio_id = audio_obj.get("id") if msg_type in ("audio", "voice") else None
        audio_duration = int(audio_obj.get("seconds") or audio_obj.get("duration") or 0) if msg_type in ("audio", "voice") else 0

        return {
            "from": sender,
            "type": msg_type,
            "text": text_body,
            "button_id": button_id,
            "button_title": button_title,
            "image_id": image_id,
            "audio_id": audio_id,
            "audio_duration": audio_duration,
            "location": location_data,
            "message_id": msg.get("id"),
        }
    except (KeyError, IndexError, AttributeError):
        return None


async def upload_media(file_bytes: bytes, mime_type: str = "audio/ogg; codecs=opus", filename: str = "voice.ogg") -> str:
    """Upload media binary to Meta WhatsApp Cloud API and return media_id."""
    if _is_mock_token(WHATSAPP_TOKEN):
        return "mock_media_id_123"

    url = f"{GRAPH_BASE_URL}/{WHATSAPP_PHONE_NUMBER_ID}/media"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    files = {
        "file": (filename, file_bytes, mime_type),
        "messaging_product": (None, "whatsapp"),
        "type": (None, mime_type),
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, files=files)
        resp.raise_for_status()
        return resp.json().get("id", "")


async def send_audio_message(to: str, media_id: str) -> Dict[str, Any]:
    """Send an audio voice note message via WhatsApp Cloud API using media_id."""
    if _is_mock_token(WHATSAPP_TOKEN) or media_id.startswith("mock_"):
        return {"messaging_product": "whatsapp", "contacts": [{"wa_id": to}], "messages": [{"id": "mock_wamid_audio_456"}]}

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "audio",
        "audio": {"id": media_id},
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(MESSAGES_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()


async def send_image_message(to: str, media_id: str, caption: Optional[str] = None) -> Dict[str, Any]:
    """Send an image message via WhatsApp Cloud API using media_id and optional text caption."""
    if _is_mock_token(WHATSAPP_TOKEN) or media_id.startswith("mock_"):
        return {"messaging_product": "whatsapp", "contacts": [{"wa_id": to}], "messages": [{"id": "mock_wamid_img_789"}]}

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    image_payload: Dict[str, Any] = {"id": media_id}
    if caption:
        image_payload["caption"] = caption

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "image",
        "image": image_payload,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(MESSAGES_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()


def is_user_in_24h_window(last_inbound_timestamp: Optional[Union[datetime, str]], now: Optional[datetime] = None) -> bool:
    """Evaluate whether last inbound timestamp is within active 24-hour customer service window."""
    if not last_inbound_timestamp:
        return False
        
    if isinstance(last_inbound_timestamp, str):
        try:
            dt = datetime.fromisoformat(last_inbound_timestamp.replace("Z", "+00:00"))
        except ValueError:
            return False
    else:
        dt = last_inbound_timestamp
        
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
        
    current_now = now or datetime.now(timezone.utc)
    if current_now.tzinfo is None:
        current_now = current_now.replace(tzinfo=timezone.utc)
        
    elapsed = current_now - dt
    return timedelta(seconds=0) <= elapsed <= timedelta(hours=24)


async def send_template_message(
    to: str,
    template_name: str = "irrigagent_daily_advisory",
    language_code: str = "fr",
    parameters: Optional[List[str]] = None,
    components: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Send a pre-approved Meta WhatsApp Cloud API Message Template with Quick Reply buttons."""
    if _is_mock_token(WHATSAPP_TOKEN):
        return {"messaging_product": "whatsapp", "contacts": [{"wa_id": to}], "messages": [{"id": "mock_wamid_template_999"}]}

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    
    if components is None:
        components = []
        if parameters:
            body_params = [{"type": "text", "text": str(p)} for p in parameters]
            components.append({"type": "body", "parameters": body_params})

        if template_name in ("irrigagent_daily_advisory", "daily_irrigation_advisory"):
            components.extend([
                {"type": "button", "sub_type": "quick_reply", "index": "0", "parameters": [{"type": "payload", "payload": "btn_approve"}]},
                {"type": "button", "sub_type": "quick_reply", "index": "1", "parameters": [{"type": "payload", "payload": "btn_skip"}]},
                {"type": "button", "sub_type": "quick_reply", "index": "2", "parameters": [{"type": "payload", "payload": "btn_modify"}]},
            ])

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
            "components": components,
        },
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(MESSAGES_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()


def is_meta_window_expired_error(exception: Exception) -> bool:
    """Check if exception represents Meta Cloud API error code 131026 (Customer Service Window Expired)."""
    if isinstance(exception, httpx.HTTPStatusError) and exception.response is not None:
        try:
            data = exception.response.json()
            err_code = data.get("error", {}).get("code")
            if err_code == 131026:
                return True
        except Exception:
            pass
    return False


async def send_message_with_window_fallback(
    to: str,
    text_body: str,
    template_name: str = "daily_irrigation_advisory",
    language_code: str = "fr",
    parameters: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Attempt free-form text delivery; fallback to template delivery if Meta error 131026 is caught."""
    try:
        return await send_text_message(to, text_body)
    except Exception as e:
        if is_meta_window_expired_error(e):
            return await send_template_message(
                to=to,
                template_name=template_name,
                language_code=language_code,
                parameters=parameters,
            )
        raise



