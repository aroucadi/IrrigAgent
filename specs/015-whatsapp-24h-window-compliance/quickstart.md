# Quickstart & Automated Verification Guide: WhatsApp 24-Hour Window Compliance

## Overview
This guide provides actionable commands and automated test procedures to verify customer service window tracking, template message dispatch, and Meta error 131026 fallback logic.

---

## 1. Unit & Integration Test Suite Execution

Run the targeted pytest test suite to verify 24-hour window calculations and template dispatch payloads:

```bash
pytest tests/test_whatsapp_24h_window.py -v
```

### Test Coverage Requirements
1. **Window Active Test**: Inbound message received within 24h evaluates `is_user_in_24h_window() == True`.
2. **Window Expired Test**: Inbound message received >24h ago evaluates `is_user_in_24h_window() == False`.
3. **Template Payload Validation**: `send_template_message()` constructs valid Meta JSON payload with `"type": "template"`, French `fr` language code, and positional parameters.
4. **Error 131026 Handling**: Meta Cloud API response with code `131026` triggers window expiration state update and automatic template fallback retry.

---

## 2. Live Verification Procedure (P1 User Story)

To verify actual Meta API behavior today using sandbox environment:

```python
import asyncio
from app.whatsapp import send_text_message, send_template_message

async def verify_live_behavior():
    # 1. Attempt free-form message to a sandbox recipient outside 24h window
    recipient = "212600000000"
    print("Testing free-form dispatch outside 24h window...")
    try:
        res = await send_text_message(recipient, "Test advisory outside 24h window")
        print("Free-form response:", res)
    except Exception as e:
        print("Caught expected Meta window restriction error:", e)

    # 2. Test template message dispatch
    print("Testing template message dispatch...")
    res_template = await send_template_message(
        to=recipient,
        template_name="daily_irrigation_advisory",
        language_code="fr",
        parameters=["Ferme Hassan", "4.5 mm", "45 min"]
    )
    print("Template response:", res_template)

if __name__ == "__main__":
    asyncio.run(verify_live_behavior())
```
