# Interface Contract: WhatsApp Webhook API

**Endpoint**: `https://<service-url>/webhook`  
**Protocol**: HTTPS  
**Content-Type**: `application/json`

---

## 1. Webhook Handshake (GET `/webhook`)

Called by Meta App Dashboard when validating the webhook endpoint URL.

### Request Query Parameters
| Parameter | Type | Description |
|---|---|---|
| `hub.mode` | String | Must equal `"subscribe"` |
| `hub.verify_token` | String | Verification secret matching `VERIFY_TOKEN` env var |
| `hub.challenge` | String | Random challenge string sent by Meta |

### Response
- **200 OK**: Plain text response containing the raw `hub.challenge` string.
- **403 Forbidden**: Returned if `hub.verify_token` fails to match.

---

## 2. Incoming Webhook Event (POST `/webhook`)

Called by Meta every time a verified sandbox user sends a text message or photo image.

### Expected Payload Structure (Text Reply)
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
              "phone_number_id": "PHONE_NUMBER_ID"
            },
            "contacts": [
              {
                "profile": { "name": "Hassan" },
                "wa_id": "212600000000"
              }
            ],
            "messages": [
              {
                "from": "212600000000",
                "id": "wamid.HBgLMjEyNjAwMDAwMDAwFQIAERgSQjE2M...",
                "timestamp": "1774782000",
                "text": { "body": "1" },
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

### Expected Payload Structure (Leaf Photo Image)
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
            "messages": [
              {
                "from": "212600000000",
                "id": "wamid.HBgLMjEyNjAwMDAwMDAwFQIAERgSQjE2M...",
                "timestamp": "1774782000",
                "image": {
                  "caption": "spot on leaf",
                  "mime_type": "image/jpeg",
                  "sha256": "...",
                  "id": "MEDIA_ID_12345"
                },
                "type": "image"
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

### Response
- **200 OK**: JSON response `{"status": "ok"}` (Meta requires HTTP 200 within 20s to prevent delivery retries).
