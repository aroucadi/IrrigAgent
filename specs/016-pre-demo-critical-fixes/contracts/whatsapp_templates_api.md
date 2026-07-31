# Interface Contract: WhatsApp Cloud API Template Messaging

## 1. Outbound Template Message Endpoint

- **Method**: `POST`
- **URL**: `https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages`
- **Headers**:
  - `Authorization: Bearer {WHATSAPP_TOKEN}`
  - `Content-Type: application/json`

### Request Body (Template Messaging)

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "212600000000",
  "type": "template",
  "template": {
    "name": "irrigagent_daily_advisory",
    "language": {
      "code": "fr"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "Standard weather forecast (4.5 mm ETc [ET₀ 4.5 × Kc 1.0]). Recommendation: Maintain standard irrigation schedule tomorrow."
          },
          {
            "type": "text",
            "text": ""
          }
        ]
      },
      {
        "type": "button",
        "sub_type": "quick_reply",
        "index": "0",
        "parameters": [
          {
            "type": "payload",
            "payload": "btn_approve"
          }
        ]
      },
      {
        "type": "button",
        "sub_type": "quick_reply",
        "index": "1",
        "parameters": [
          {
            "type": "payload",
            "payload": "btn_skip"
          }
        ]
      },
      {
        "type": "button",
        "sub_type": "quick_reply",
        "index": "2",
        "parameters": [
          {
            "type": "payload",
            "payload": "btn_modify"
          }
        ]
      }
    ]
  }
}
```

### Success Response (`200 OK`)

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
      "id": "wamid.HBgL..."
    }
  ]
}
```

### Out-of-Window / Template Error Response (`400 Bad Request` or `403 Forbidden`)

```json
{
  "error": {
    "message": "(#131026) Message outside the 24-hour window",
    "type": "OAuthException",
    "code": 131026,
    "error_data": {
      "details": "Message details..."
    },
    "fbtrace_id": "A..."
  }
}
```
