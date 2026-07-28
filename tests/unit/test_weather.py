import asyncio
from unittest.mock import patch
import httpx

from app.weather import get_et0_forecast
from app.decision import evaluate_irrigation_recommendation


def test_weather_fallback_after_3_retries_and_notice():
    """Verify that when Open-Meteo fails after 3 retries, fallback ET0 baseline is used
    AND outgoing WhatsApp recommendation text contains 'Estimated ET₀ data used' notice per FR-020.
    """
    async def _test():
        with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("API unavailable")):
            weather_data, data_quality = await get_et0_forecast(30.4, -9.5)
            
            # 1. Assert fallback data quality and baseline ET0
            assert data_quality == "estimated"
            assert weather_data["et0"] == 4.5
            
            # 2. Evaluate recommendation with fallback quality
            action, rec_msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather_data, data_quality)
            
            # 3. Assert outgoing message explicitly contains estimated data notice per FR-020
            assert "Estimated ET₀ data used" in rec_msg
    asyncio.run(_test())
