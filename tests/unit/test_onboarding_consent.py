import pytest
from unittest.mock import AsyncMock, patch
from app.main import receive_webhook
from app.firestore_client import get_farm_profile

@pytest.mark.asyncio
async def test_onboarding_flow_with_explicit_consent_and_no_silent_overrides():
    phone = "+212677889900"

    # 1. New user initial message -> Prompt for location pin + display plain-language consent statement
    msg1 = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "type": "text",
                        "text": {"body": "Salam"}
                    }]
                }
            }]
        }]
    }

    with patch("app.main.send_text_message", new_callable=AsyncMock) as mock_send:
        res1 = await receive_webhook(AsyncMock(json=AsyncMock(return_value=msg1)), AsyncMock())
        assert res1["status"] == "onboarding_location_prompted"
        sent_text = mock_send.call_args[0][1]
        assert "Data Rights" in sent_text or "Privacy" in sent_text or "données sont utilisées" in sent_text
        assert "Location Pin" in sent_text or "Localisation" in sent_text

    prof1 = await get_farm_profile(phone)
    assert prof1["onboarding_incomplete"] is True
    assert prof1["onboarding_step"] == "AWAITING_LOCATION"
    assert prof1["consent_accepted"] is True

    # 2. User sends location pin -> Prompt for crop via interactive buttons
    loc_msg = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "type": "location",
                        "location": {"latitude": 31.6295, "longitude": -7.9811}
                    }]
                }
            }]
        }]
    }

    with patch("app.main.send_interactive_buttons_message", new_callable=AsyncMock) as mock_send_btn:
        res2 = await receive_webhook(AsyncMock(json=AsyncMock(return_value=loc_msg)), AsyncMock())
        assert res2["status"] == "onboarding_location_saved"
        mock_send_btn.assert_called_once()
        buttons = mock_send_btn.call_args[1].get("buttons", [])
        assert any(b["id"] == "CROP_TOMATOES" for b in buttons)

    prof2 = await get_farm_profile(phone)
    assert prof2["location"] == {"latitude": 31.6295, "longitude": -7.9811}
    assert prof2["onboarding_step"] == "AWAITING_CROP"

    # 3. User taps Tomatoes crop button -> Prompt for field size in hectares
    crop_msg = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "type": "interactive",
                        "interactive": {
                            "type": "button_reply",
                            "button_reply": {"id": "CROP_CITRUS", "title": "Citrus"}
                        }
                    }]
                }
            }]
        }]
    }

    with patch("app.main.send_text_message", new_callable=AsyncMock) as mock_send_area:
        res3 = await receive_webhook(AsyncMock(json=AsyncMock(return_value=crop_msg)), AsyncMock())
        assert res3["status"] == "onboarding_crop_saved"
        assert "superficie" in mock_send_area.call_args[0][1].lower() or "hectares" in mock_send_area.call_args[0][1].lower()

    prof3 = await get_farm_profile(phone)
    assert prof3["crop_type"] == "citrus"
    assert prof3["onboarding_step"] == "AWAITING_AREA"

    # 4. User replies with "12.5 ha" area -> Onboarding completes
    area_msg = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "type": "text",
                        "text": {"body": "12.5 ha"}
                    }]
                }
            }]
        }]
    }

    with patch("app.main.send_text_message", new_callable=AsyncMock) as mock_send_done:
        res4 = await receive_webhook(AsyncMock(json=AsyncMock(return_value=area_msg)), AsyncMock())
        assert res4["status"] == "onboarding_completed"
        assert "Configuration terminée" in mock_send_done.call_args[0][1]

    final_prof = await get_farm_profile(phone)
    assert final_prof["onboarding_incomplete"] is False
    assert final_prof["onboarding_step"] == "COMPLETED"
    assert final_prof["crop_type"] == "citrus"
    assert final_prof["acreage_hectares"] == 12.5
    assert final_prof["location"] == {"latitude": 31.6295, "longitude": -7.9811}
