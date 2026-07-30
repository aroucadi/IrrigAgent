import httpx
from typing import Optional, Dict, Any
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
    """Extract sender number, text body, image ID, or location attachment from Meta webhook POST payload."""
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
        image_id = msg.get("image", {}).get("id") if msg_type == "image" else None
        location_data = msg.get("location") if msg_type == "location" else None
        audio_obj = msg.get("audio") or msg.get("voice") or {}
        audio_id = audio_obj.get("id") if msg_type in ("audio", "voice") else None
        audio_duration = int(audio_obj.get("seconds") or audio_obj.get("duration") or 0) if msg_type in ("audio", "voice") else 0

        return {
            "from": sender,
            "type": msg_type,
            "text": text_body,
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

