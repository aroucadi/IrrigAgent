import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.config import JOB_SECRET_TOKEN

client = TestClient(app)


# --- Test Fixtures & Sample Profiles ---
FARM_PROFILE_A = {
    "phone_number": "+212611111111",
    "crop_type": "tomatoes",
    "acreage_hectares": 10.0,
    "location": {"latitude": 30.4278, "longitude": -9.5981},
    "preferred_language": "french",
}

FARM_PROFILE_B = {
    "phone_number": "+212622222222",
    "crop_type": "citrus",
    "acreage_hectares": 25.0,
    "location": {"latitude": 34.8941, "longitude": -2.3278},
    "preferred_language": "darija",
}

MOCK_WEATHER_DATA = {
    "et0_today": 4.5,
    "temp_max": 28.0,
    "humidity_avg": 55.0,
    "rain_mm": 0.0,
}


@pytest.mark.asyncio
async def test_daily_batch_unauthorized():
    """Verify endpoint rejects requests without valid Bearer JOB_SECRET_TOKEN."""
    response = client.post("/jobs/daily-recommendations")
    assert response.status_code == 401

    response_bad_token = client.post(
        "/jobs/daily-recommendations",
        headers={"Authorization": "Bearer invalid_secret_token"},
    )
    assert response_bad_token.status_code == 401


@pytest.mark.asyncio
async def test_daily_batch_multi_farm_differentiation():
    """Verify triggering daily batch job for multiple farms generates distinct farm recommendations without cross-contamination."""
    with (
        patch("app.main.list_active_farm_profiles", new=AsyncMock(return_value=[FARM_PROFILE_A, FARM_PROFILE_B])),
        patch("app.main.get_et0_forecast", new=AsyncMock(return_value=(MOCK_WEATHER_DATA, "fresh"))),
        patch("app.main.save_recommendation", new=AsyncMock(return_value="rec_123")) as mock_save,
        patch("app.main.is_user_in_24h_window", return_value=True),
        patch("app.main.send_text_message", new=AsyncMock(return_value={"status": "sent"})) as mock_send,
    ):
        response = client.post(
            "/jobs/daily-recommendations",
            headers={"Authorization": f"Bearer {JOB_SECRET_TOKEN}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["dispatched_count"] == 2
        assert data["failed_count"] == 0

        # Verify recommendations saved against distinct farm phone numbers
        assert mock_save.call_count == 2
        saved_phones = [call[0][0]["phone_number"] for call in mock_save.call_args_list]
        assert "+212611111111" in saved_phones
        assert "+212622222222" in saved_phones

        # Verify outbound WhatsApp messages dispatched to both farms
        assert mock_send.call_count == 2
        sent_phones = [call[0][0] for call in mock_send.call_args_list]
        assert "+212611111111" in sent_phones
        assert "+212622222222" in sent_phones


@pytest.mark.asyncio
async def test_daily_batch_single_farm_failure_resilience():
    """Verify fault isolation: outbound dispatch failure on Farm A does not halt processing or dispatch for Farm B."""
    async def mock_send_message_side_effect(phone, text):
        if phone == "+212611111111":
            raise RuntimeError("Graph API simulated connection error for Farm A")
        return {"status": "sent"}

    with (
        patch("app.main.list_active_farm_profiles", new=AsyncMock(return_value=[FARM_PROFILE_A, FARM_PROFILE_B])),
        patch("app.main.get_et0_forecast", new=AsyncMock(return_value=(MOCK_WEATHER_DATA, "fresh"))),
        patch("app.main.save_recommendation", new=AsyncMock(return_value="rec_123")) as mock_save,
        patch("app.main.is_user_in_24h_window", return_value=True),
        patch("app.main.send_text_message", new=AsyncMock(side_effect=mock_send_message_side_effect)) as mock_send,
    ):
        response = client.post(
            "/jobs/daily-recommendations",
            headers={"Authorization": f"Bearer {JOB_SECRET_TOKEN}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["dispatched_count"] == 1
        assert data["failed_count"] == 1

        # Recommendations were evaluated and saved for both farms
        assert mock_save.call_count == 2

        # Send attempt occurred for both farms
        assert mock_send.call_count == 2


@pytest.mark.asyncio
async def test_daily_batch_all_farms_failure_resilience():
    """Verify endpoint completes gracefully with zero dispatches when all send attempts fail."""
    with (
        patch("app.main.list_active_farm_profiles", new=AsyncMock(return_value=[FARM_PROFILE_A, FARM_PROFILE_B])),
        patch("app.main.get_et0_forecast", new=AsyncMock(return_value=(MOCK_WEATHER_DATA, "fresh"))),
        patch("app.main.save_recommendation", new=AsyncMock(return_value="rec_123")),
        patch("app.main.is_user_in_24h_window", return_value=True),
        patch("app.main.send_text_message", new=AsyncMock(side_effect=RuntimeError("Global network outage"))),
    ):
        response = client.post(
            "/jobs/daily-recommendations",
            headers={"Authorization": f"Bearer {JOB_SECRET_TOKEN}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["dispatched_count"] == 0
        assert data["failed_count"] == 2


@pytest.mark.asyncio
async def test_daily_batch_template_message_when_window_closed():
    """Verify daily batch job uses send_template_message when 24h window is closed."""
    with (
        patch("app.main.list_active_farm_profiles", new=AsyncMock(return_value=[FARM_PROFILE_A])),
        patch("app.main.get_et0_forecast", new=AsyncMock(return_value=(MOCK_WEATHER_DATA, "fresh"))),
        patch("app.main.save_recommendation", new=AsyncMock(return_value="rec_123")),
        patch("app.main.is_user_in_24h_window", return_value=False),
        patch("app.main.send_template_message", new=AsyncMock(return_value={"status": "sent"})) as mock_send_template,
    ):
        response = client.post(
            "/jobs/daily-recommendations",
            headers={"Authorization": f"Bearer {JOB_SECRET_TOKEN}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["dispatched_count"] == 1
        assert mock_send_template.call_count == 1

