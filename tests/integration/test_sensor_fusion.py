import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.firestore_client import get_farm_sensor_state

client = TestClient(app)


def test_telemetry_sensor_endpoint_valid():
    payload = {
        "farm_id": "+212600000000",
        "timestamp": "2026-07-31T14:00:00Z",
        "soil_moisture_vwc": 16.5,
        "depth_cm": 15,
        "battery_level": 94
    }
    response = client.post("/telemetry/sensor", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["farm_id"] == "+212600000000"
    assert data["soil_moisture_vwc"] == 16.5


@pytest.mark.asyncio
async def test_telemetry_sensor_persistence():
    payload = {
        "farm_id": "+212699887766",
        "timestamp": "2026-07-31T14:30:00Z",
        "soil_moisture_vwc": 14.2,
        "depth_cm": 15,
        "battery_level": 88
    }
    response = client.post("/telemetry/sensor", json=payload)
    assert response.status_code == 200

    state = await get_farm_sensor_state("+212699887766")
    assert state is not None
    assert state["soil_moisture_vwc"] == 14.2
    assert state["battery_level"] == 88


def test_telemetry_sensor_endpoint_invalid_vwc():
    payload = {
        "farm_id": "+212600000000",
        "timestamp": "2026-07-31T14:00:00Z",
        "soil_moisture_vwc": 150.0  # Invalid > 100%
    }
    response = client.post("/telemetry/sensor", json=payload)
    assert response.status_code == 422
