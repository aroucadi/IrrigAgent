import pytest
from unittest.mock import AsyncMock, patch
from app.config import JOB_SECRET_TOKEN
from app.main import receive_webhook, trigger_daily_recommendations
from app.firestore_client import get_farm_profile, save_farm_profile

@pytest.mark.asyncio
async def test_opt_out_and_opt_in_webhook_flow():
    phone = "+212688990011"
    profile = {
        "phone_number": phone,
        "opted_out": False,
        "onboarding_incomplete": False
    }
    await save_farm_profile(profile)

    # 1. Send /stop command
    stop_payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "type": "text",
                        "text": {"body": "/stop"}
                    }]
                }
            }]
        }]
    }

    with patch("app.main.send_text_message", new_callable=AsyncMock) as mock_send:
        res = await receive_webhook(AsyncMock(json=AsyncMock(return_value=stop_payload)), AsyncMock())
        assert res["status"] == "opted_out"
        mock_send.assert_called_once()
        assert "unsubscribed" in mock_send.call_args[0][1].lower()

    updated = await get_farm_profile(phone)
    assert updated["opted_out"] is True

    # 2. Send /start command to resume
    start_payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "type": "text",
                        "text": {"body": "/start"}
                    }]
                }
            }]
        }]
    }

    with patch("app.main.send_text_message", new_callable=AsyncMock) as mock_send_start:
        res_start = await receive_webhook(AsyncMock(json=AsyncMock(return_value=start_payload)), AsyncMock())
        assert res_start["status"] == "opted_in"
        mock_send_start.assert_called_once()
        assert "welcome back" in mock_send_start.call_args[0][1].lower()

    resumed = await get_farm_profile(phone)
    assert resumed["opted_out"] is False


@pytest.mark.asyncio
async def test_daily_batch_skips_opted_out_farm():
    opted_out_phone = "+212699001122"
    active_phone = "+212699001123"

    await save_farm_profile({"phone_number": opted_out_phone, "opted_out": True, "location": {"latitude": 30.4, "longitude": -9.5}, "crop_type": "tomatoes", "acreage_hectares": 5.0})
    await save_farm_profile({"phone_number": active_phone, "opted_out": False, "location": {"latitude": 30.4, "longitude": -9.5}, "crop_type": "tomatoes", "acreage_hectares": 5.0})

    with patch("app.main.list_active_farm_profiles", new_callable=AsyncMock) as mock_list, \
         patch("app.main.get_et0_forecast", return_value=({"et0": 4.5, "precipitation_mm": 0.0}, "fresh")), \
         patch("app.main.send_template_message", new_callable=AsyncMock) as mock_send_tpl:
        mock_list.return_value = [
            {"phone_number": opted_out_phone, "opted_out": True},
            {"phone_number": active_phone, "opted_out": False, "location": {"latitude": 30.4, "longitude": -9.5}, "crop_type": "tomatoes", "acreage_hectares": 5.0}
        ]
        
        resp = await trigger_daily_recommendations(AsyncMock(), authorization=f"Bearer {JOB_SECRET_TOKEN}")
        assert resp.processed_count == 1
        assert mock_send_tpl.call_count == 1
        assert mock_send_tpl.call_args[1]["to"] == active_phone

