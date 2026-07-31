import asyncio
import httpx
from typing import Dict, Any, Tuple

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"


async def get_et0_forecast(latitude: float, longitude: float) -> Tuple[Dict[str, Any], str]:
    """Fetch next-day forecast weather & ET0 from Open-Meteo.
    
    Retries up to 3 times with short backoff (1s / 2s / 3s).
    Returns (forecast_dict, data_quality) where data_quality is 'fresh' or 'estimated'.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["et0_fao_evapotranspiration", "precipitation_sum", "temperature_2m_max", "temperature_2m_min"],
        "timezone": "auto",
        "forecast_days": 2,
    }

    backoffs = [1, 2, 3]
    
    for attempt in range(len(backoffs) + 1):
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(OPEN_METEO_BASE_URL, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    daily = data.get("daily", {})
                    et0_list = daily.get("et0_fao_evapotranspiration", [4.5, 4.5])
                    precip_list = daily.get("precipitation_sum", [0.0, 0.0])
                    temp_max_list = daily.get("temperature_2m_max", [25.0, 25.0])
                    temp_min_list = daily.get("temperature_2m_min", [15.0, 15.0])
                    
                    et0_val = et0_list[1] if len(et0_list) > 1 else et0_list[0]
                    precip_val = precip_list[1] if len(precip_list) > 1 else precip_list[0]
                    temp_max_val = temp_max_list[1] if len(temp_max_list) > 1 else temp_max_list[0]
                    temp_min_val = temp_min_list[1] if len(temp_min_list) > 1 else temp_min_list[0]
                    
                    return {
                        "et0": float(et0_val or 4.5),
                        "precipitation_mm": float(precip_val or 0.0),
                        "temp_max_c": float(temp_max_val or 25.0),
                        "temp_min_c": float(temp_min_val or 15.0),
                        "temperature_2m_max": float(temp_max_val or 25.0),
                        "temperature_2m_min": float(temp_min_val or 15.0),
                    }, "fresh"
        except Exception:
            pass

        if attempt < len(backoffs):
            await asyncio.sleep(backoffs[attempt])

    # Fallback to baseline yesterday estimates if Open-Meteo fails after retries
    return {
        "et0": 4.5,
        "precipitation_mm": 0.0,
        "temp_max_c": 26.0,
        "temp_min_c": 15.0,
        "temperature_2m_max": 26.0,
        "temperature_2m_min": 15.0,
    }, "estimated"
