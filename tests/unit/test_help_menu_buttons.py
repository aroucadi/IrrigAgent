import pytest
from unittest.mock import AsyncMock, patch
from app.main import receive_webhook, app
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.mark.asyncio
async def test_universal_help_command_triggers_menu():
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "+212611223344",
                        "type": "text",
                        "text": {"body": "/help"}
                    }]
                }
            }]
        }]
    }

    with patch("app.main.send_interactive_buttons_message", new_callable=AsyncMock) as mock_send_btn:
        res = await receive_webhook(AsyncMock(json=AsyncMock(return_value=payload)), AsyncMock())
        assert res["status"] == "help_menu_dispatched"
        mock_send_btn.assert_called_once()
        args, kwargs = mock_send_btn.call_args
        assert args[0] == "+212611223344"
        assert "Main Menu" in kwargs.get("header_text", "") or "Main Menu" in args[1]


from app.firestore_client import save_farm_profile

@pytest.mark.asyncio
async def test_menu_button_selection_routing():
    phone = "+212611223344"
    await save_farm_profile({"phone_number": phone, "onboarding_incomplete": False})

    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "type": "interactive",
                        "interactive": {
                            "type": "button_reply",
                            "button_reply": {
                                "id": "MENU_PARCEL",
                                "title": "Setup Boundary"
                            }
                        }
                    }]
                }
            }]
        }]
    }


    with patch("app.main.send_text_message", new_callable=AsyncMock) as mock_send_text:
        res = await receive_webhook(AsyncMock(json=AsyncMock(return_value=payload)), AsyncMock())
        assert res["status"] == "pin_collection_started"
        mock_send_text.assert_called_once()
        assert "Send PIN 1" in mock_send_text.call_args[0][1]
