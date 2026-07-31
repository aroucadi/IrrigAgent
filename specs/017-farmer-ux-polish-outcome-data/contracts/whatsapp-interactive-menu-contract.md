# Interface Contract: WhatsApp Interactive Menus & Buttons

**Feature Directory**: `specs/017-farmer-ux-polish-outcome-data`  
**Date**: 2026-07-31  

---

## 1. Voice Intent Confirmation Payload (Free-Form Open Window)

**Recipient**: WhatsApp Cloud API `/messages`  
**Type**: `interactive` (button)  
**Constraint**: Titles MUST be <= 20 characters.

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "+212600000000",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "header": {
      "type": "text",
      "text": "🌾 Voice Request Confirmation"
    },
    "body": {
      "text": "Transcribed: \"Zid 15 dqiqa f l-sqi ghadan\"\nProposed Adjustment: +15 minutes"
    },
    "action": {
      "buttons": [
        {
          "type": "reply",
          "reply": {
            "id": "CONFIRM_VOICE_INTENT",
            "title": "Confirm"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "CANCEL_VOICE_INTENT",
            "title": "Cancel"
          }
        }
      ]
    }
  }
}
```

---

## 2. Main Help Menu Payload (`/help`, `help`, `menu`)

**Type**: `interactive` (button or list message)

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "+212600000000",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "header": {
      "type": "text",
      "text": "🌾 IrrigAgent Main Menu"
    },
    "body": {
      "text": "Select an action below or reply with a command anytime:"
    },
    "action": {
      "buttons": [
        {
          "type": "reply",
          "reply": {
            "id": "MENU_PARCEL",
            "title": "🗺️ Setup Boundary"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "MENU_HEATMAP",
            "title": "🛰️ Crop Health"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "MENU_PROFILE",
            "title": "👤 Update Profile"
          }
        }
      ]
    }
  }
}
```

---

## 3. Onboarding Crop Selection Payload

**Type**: `interactive` (button)

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "+212600000000",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "header": {
      "type": "text",
      "text": "🌱 Select Primary Crop"
    },
    "body": {
      "text": "Please choose your primary crop type for accurate water calculation:"
    },
    "action": {
      "buttons": [
        {
          "type": "reply",
          "reply": {
            "id": "CROP_TOMATOES",
            "title": "Tomatoes"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "CROP_CITRUS",
            "title": "Citrus"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "CROP_OLIVES",
            "title": "Olives"
          }
        }
      ]
    }
  }
}
```

---

## 4. Outcome-Feedback Quick-Reply Payload

**Type**: `interactive` (button)  
**Constraint**: Titles MUST be <= 20 characters.

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "+212600000000",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "header": {
      "type": "text",
      "text": "💧 Yesterday's Irrigation Check"
    },
    "body": {
      "text": "Did you irrigate as recommended yesterday?"
    },
    "action": {
      "buttons": [
        {
          "type": "reply",
          "reply": {
            "id": "FB_YES",
            "title": "Yes"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "FB_LESS",
            "title": "Less"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "FB_MORE",
            "title": "More"
          }
        }
      ]
    }
  }
}
```
*Note: A 4th option ("Skipped") can be sent via list message or secondary button flow if 3-button limit applies on standard interactive button component.*
