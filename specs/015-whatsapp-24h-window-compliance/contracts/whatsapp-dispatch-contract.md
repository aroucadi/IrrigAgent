# Interface Contract: WhatsApp Template Dispatch API

## Overview
Defines the external interface contract for Meta WhatsApp Cloud API template messaging and window state management in IrrigAgent.

---

## 1. Outbound Template Message Payload

### Endpoint
`POST https://graph.facebook.com/{GRAPH_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages`

### Headers
```http
Authorization: Bearer {WHATSAPP_TOKEN}
Content-Type: application/json
```

### Request Body (`type: template`)
```json
{
  "messaging_product": "whatsapp",
  "to": "212600000000",
  "type": "template",
  "template": {
    "name": "daily_irrigation_advisory",
    "language": {
      "code": "fr"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "Ferme Hassan"
          },
          {
            "type": "text",
            "text": "4.5 mm"
          },
          {
            "type": "text",
            "text": "45 min"
          }
        ]
      }
    ]
  }
}
```

### Successful Response (HTTP 200 OK)
```json
{
  "messaging_product": "whatsapp",
  "contacts": [
    {
      "input": "212600000000",
      "wa_id": "212600000000"
    }
  ],
  "messages": [
    {
      "id": "wamid.HBgLMjEyNjAwMDAwMDAwFQIAERgSQTU1RjVDQzNFQTdBOTdDMDhB..."
    }
  ]
}
```

---

## 2. Window Expiration Error Response (HTTP 400 / 403)

### Meta API Error 131026 Payload
```json
{
  "error": {
    "message": "(#131026) Message undeliverable. Customer service window has expired.",
    "type": "OAuthException",
    "code": 131026,
    "error_data": {
      "messaging_product": "whatsapp",
      "details": "Message undeliverable. Customer service window has expired."
    },
    "fbtrace_id": "A1b2C3d4E5f"
  }
}
```

---

## 3. Internal Service Contract (`app/whatsapp.py`)

### Method Signature
```python
async def send_template_message(
    to: str,
    template_name: str = "daily_irrigation_advisory",
    language_code: str = "fr",
    parameters: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Send an approved WhatsApp Message Template payload via Meta Cloud API."""
```

```python
def is_user_in_24h_window(last_inbound_timestamp: Optional[datetime], now: Optional[datetime] = None) -> bool:
    """Evaluate whether the last inbound timestamp is within the active 24-hour customer service window."""
```
