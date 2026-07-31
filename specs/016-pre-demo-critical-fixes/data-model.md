# Data Model & Schema Specification: Pre-Demo Critical Fixes

## 1. WhatsApp Cloud API Outbound Template Message Schema

### Template Dispatch Payload Structure (`send_template_message`)

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "{{phone_number}}",
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
            "text": "{{parameter_1_recommendation_text}}"
          },
          {
            "type": "text",
            "text": "{{parameter_2_data_quality_notice}}"
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

### Placeholder Mapping for `irrigagent_daily_advisory`

- **`{{1}}`**: Irrigation Recommendation Core Text (e.g. *"Standard weather forecast (4.5 mm ETc [ET₀ 4.5 × Kc 1.0]). Recommendation: Maintain standard irrigation schedule tomorrow."*)
- **`{{2}}`**: Optional Data Quality / Weather Notice (e.g. *"⚠️ Notice: Estimated ET₀ data used due to weather service delay."* or empty string `""`).

---

## 2. Inbound Webhook Button Postback Schema

### Meta Cloud API Interactive Quick Reply Button Click Payload

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "123456789",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15550269870",
              "phone_number_id": "100609346387085"
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
                "id": "wamid.HBgL...",
                "timestamp": "1722420000",
                "type": "interactive",
                "interactive": {
                  "type": "button_reply",
                  "button_reply": {
                    "id": "btn_approve",
                    "title": "Approve"
                  }
                }
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

### Extracted Dictionary Representation (`extract_incoming_message`)

```python
{
    "from": "212600000000",
    "type": "interactive",
    "text": "1",  # Mapped from button_reply.id ("btn_approve" -> "1", "btn_skip" -> "2", "btn_modify" -> "3")
    "button_id": "btn_approve",
    "button_title": "Approve",
    "image_id": None,
    "audio_id": None,
    "audio_duration": 0,
    "location": None,
    "message_id": "wamid.HBgL...",
}
```

---

## 3. Daily Job Response Schema Update

`DailyAdvisoryJobResponse` in `app/schemas.py`:
- `status`: str (e.g. `"success"`)
- `processed_count`: int
- `dispatched_count`: int
- `failed_count`: int
- `skipped_count`: int

---

## 4. Dependencies Schema (`requirements.txt`)

- `fastapi==0.115.0`
- `uvicorn[standard]==0.30.6`
- `python-multipart>=0.0.12` *(NEW — CRIT-006)*
- `httpx==0.27.2`
- `google-cloud-firestore==2.19.0`
- `google-genai>=0.1.0`
- `pydantic==2.9.2`
- `google-cloud-texttospeech>=2.16.0`
- `pytest==8.3.3`
- `pytest-asyncio==0.24.0`
- `rasterio>=1.3.0`
- `numpy>=1.24.0`
