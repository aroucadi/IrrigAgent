# Contract: WhatsApp Location Webhook & Multi-Pin State Machine

## 1. Incoming WhatsApp Location Attachment Payload

When a farmer sends a location pin via WhatsApp, Meta Cloud API sends a webhook payload to `/webhook` or `/whatsapp/webhook`:

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
      "changes": [
        {
          "value": "whatsapp_business_account",
          "field": "messages",
          "messaging_product": "whatsapp",
          "metadata": {
            "display_phone_number": "15550555555",
            "phone_number_id": "123456789"
          },
          "contacts": [
            {
              "profile": {
                "name": "Farmer Hassan"
              },
              "wa_id": "212600000000"
            }
          ],
          "messages": [
            {
              "from": "212600000000",
              "id": "wamid.HBgLMjEyNjAwMDAwMDAwFQIAEhgWM0FCODRGNzM1ODE0QUQ1RTRBQkE2QQA=",
              "timestamp": "1785254400",
              "type": "location",
              "location": {
                "latitude": 30.4278,
                "longitude": -9.5981,
                "name": "Location",
                "address": "Agadir Region"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

## 2. Text Trigger Commands

- Initiating Pin Collection: Text matching regex `^/(parcel|boundary)$` or `(?i)add boundary`
- Completing Pin Collection: Text matching regex `^(DONE|done|finish|fin)$`
- Canceling Session: Text matching regex `^/(cancel|reset)$` or `(?i)cancel`
- Requesting Heatmap: Text matching regex `^/(heatmap|sentinel|canopy)$` or `(?i)canopy map`

## 3. Outgoing Conversational Responses

### A. Initial Prompt (Trigger Received)
```text
📍 Send PIN 1 (Corner 1 of your field)
```

### B. Intermediate Pin Acknowledgment
```text
✅ Pin {N} recorded! Now send PIN {N+1} (Corner {N+1})
```

### C. Pin 3 Acknowledgment (Minimum Reached)
```text
✅ Pin 3 recorded! Send PIN 4 or reply 'DONE' to close parcel boundary.
```

### D. Geometry Validation Failure (Self-Intersection)
```text
❌ Invalid boundary: Field edges cross each other (self-intersection). Please reply /parcel to try again and send corner pins sequentially around your field perimeter.
```

### E. Area Out of Bounds Failure
```text
❌ Invalid field area ({area_ha} ha): Field size must be between 0.1 ha and 200 ha. Reply /parcel to try again.
```

### F. Boundary Confirmation & Static Map Preview
```text
🎉 Field boundary recorded successfully!
Area: {area_ha} hectares
Corners: {count} points

Send /heatmap anytime to generate a Sentinel-2 Canopy Health Map.
```
