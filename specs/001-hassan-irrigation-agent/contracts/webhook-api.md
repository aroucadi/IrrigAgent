# Webhook API Interface Contract: Meta WhatsApp Cloud API

**Branch**: `001-hassan-irrigation-agent` | **Date**: 2026-07-28 | **Spec**: [spec.md](../spec.md)

## Endpoints

### 1. Webhook Verification (`GET /webhook`)

Meta WhatsApp Cloud API sends a GET request when configuring the webhook URL.

**Query Parameters**:
- `hub.mode`: String, must equal `"subscribe"`
- `hub.verify_token`: String, matched against local `WHATSAPP_VERIFY_TOKEN`
- `hub.challenge`: Integer/String, echoed verbatim on successful verification

**Response**:
- Status `200 OK` with body equal to `hub.challenge` string.
- Status `403 Forbidden` if verify token mismatch.

---

### 2. Webhook Inbound Message Payload (`POST /webhook`)

Meta WhatsApp Cloud API sends POST notifications for incoming messages.

**Headers**:
- `Content-Type: application/json`
- `X-Hub-Signature-256: sha256=...` (HMAC verification)

**Text Reply Payload Example (Option 1 Approval)**:
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15550000000",
              "phone_number_id": "123456789"
            },
            "contacts": [{"profile": {"name": "Hassan"}, "wa_id": "212600000000"}],
            "messages": [
              {
                "from": "212600000000",
                "id": "wamid.HBgL...",
                "timestamp": "1722180000",
                "text": {"body": "1"},
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

**Image Message Payload Example (CropDoctor Triage)**:
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "changes": [
        {
          "value": {
            "messages": [
              {
                "from": "212600000000",
                "id": "wamid.HBgL...",
                "timestamp": "1722180000",
                "image": {
                  "caption": "What disease is this?",
                  "mime_type": "image/jpeg",
                  "sha256": "...",
                  "id": "media_image_123"
                },
                "type": "image"
              }
            ]
          }
        }
      ]
    }
  ]
}
```

**Synchronous Response**:
- Status `200 OK` (HTTP body `{"status": "ok"}`) within <1.0s.
- Text confirmation sent via WhatsApp Cloud API POST `/messages`.
- If `ENABLE_DARIJA_VOICE_TEASER=true`, an asynchronous task synthesizes audio and calls `/messages` with `"type": "audio"`.
