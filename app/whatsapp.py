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
        # Return dummy 1x1 image bytes for mock testing
        return b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00"

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
    """Extract sender number, text body, and image ID from Meta webhook POST payload."""
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
        
        return {
            "from": sender,
            "type": msg_type,
            "text": text_body,
            "image_id": image_id,
            "message_id": msg.get("id"),
        }
    except (KeyError, IndexError, AttributeError):
        return None
