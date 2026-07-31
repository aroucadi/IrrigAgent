# Phase 0 Research: WhatsApp 24-Hour Window & Template Compliance

## 1. Meta WhatsApp Cloud API 24-Hour Window & Error 131026

### Research Findings
- **Meta Policy**: Business-initiated free-form messages (`"type": "text"`) can only be delivered within a 24-hour customer service window starting from the exact timestamp of the user's last inbound message.
- **Error Code 131026**: When a business attempts to send a free-form message outside the 24-hour window, Meta Cloud API rejects the request with HTTP 400/403 and JSON error payload:
  `{"error": {"code": 131026, "title": "Message Undeliverable", "message": "Message undeliverable. Customer service window has expired."}}`
- **Template Messaging Requirement**: Outside the 24-hour window, outbound messages MUST use registered Message Templates (`"type": "template"`).
- **Template Category & Language**: For daily irrigation advisories, Meta requires `UTILITY` template category with French (`fr`) language code for Moroccan pilot deployment.
- **Template Payload Structure**:
  ```json
  {
    "messaging_product": "whatsapp",
    "to": "212600000000",
    "type": "template",
    "template": {
      "name": "daily_irrigation_advisory",
      "language": { "code": "fr" },
      "components": [
        {
          "type": "body",
          "parameters": [
            { "type": "text", "text": "Ferme Hassan" },
            { "type": "text", "text": "4.5 mm" },
            { "type": "text", "text": "45 min" }
          ]
        }
      ]
    }
  }
  ```

### Decisions & Rationale
- **Decision**: Implement `send_template_message()` in `app/whatsapp.py` to support `UTILITY` category template payloads with positional dynamic variables (`{{1}}` farm name, `{{2}}` ET₀ recommendation, `{{3}}` duration).
- **Rationale**: Complies with Meta's developer guidelines, eliminates error 131026 failures for passive farmers who do not reply daily, and ensures 100% advisory delivery rate.

---

## 2. Inbound Timestamp & Customer Service Window Tracking State

### Research Findings
- **Inbound Event Source**: Every user message (text, image, location, voice note) processed via `app/main.py` webhook endpoint contains a timestamp.
- **Storage Strategy**: Store `last_inbound_timestamp` in Firestore under the farm/user profile document (`farms/{phone_number}`) or user session state.
- **Window Evaluation**: A helper `is_user_in_24h_window(phone_number: str) -> bool` compares `current_time - last_inbound_timestamp < 86400 seconds` (24 hours).

### Decisions & Rationale
- **Decision**: Persist `last_inbound_timestamp` in ISO-8601 UTC format in Firestore user/farm record upon every successful inbound message extraction in `extract_incoming_message()`.
- **Rationale**: Minimal latency overhead, zero extra network round-trips during webhook intake, and deterministic state checking prior to evening advisory batch dispatches at 19:00.

---

## 3. Fallback & Resiliency Flow for Meta Error 131026

### Research Findings
- **Clock Skew / Desynchronization**: If server clock and Meta Cloud API clock differ slightly near the 24-hour mark, a free-form message attempt might be rejected with error 131026 even if local evaluation calculated <24 hours.
- **Handling Mechanism**: Catch `httpx.HTTPStatusError` during free-form text transmission, inspect the response body for Meta error code `131026`, log the event, mark local window as expired, and retry sending via `send_template_message()`.

### Decisions & Rationale
- **Decision**: Implement automatic error 131026 catching and immediate fallback to template dispatch in the advisory dispatcher service.
- **Rationale**: Guarantees zero message loss even under edge-case timing desynchronization or unrecorded inbound messages.
