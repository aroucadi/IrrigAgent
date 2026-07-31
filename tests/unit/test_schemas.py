from pydantic import ValidationError
import pytest
from app.schemas import FarmProfile, HealthCheckResponse, DailyAdvisoryJobResponse


def test_farm_profile_schema_valid():
    profile = FarmProfile(
        phone_number="+212600000000",
        location="Berrechid",
        crop_type="tomatoes",
        acreage_hectares=10.0,
        preferred_language="french",
    )
    assert profile.phone_number == "+212600000000"
    assert profile.crop_type == "tomatoes"
    assert profile.acreage_hectares == 10.0
    assert profile.preferred_language == "french"


def test_farm_profile_schema_invalid_acreage():
    with pytest.raises(ValidationError):
        FarmProfile(
            phone_number="+212600000000",
            location="Berrechid",
            crop_type="tomatoes",
            acreage_hectares=0.0,  # invalid: gt=0 constraint
        )


def test_farm_profile_schema_defaults():
    profile = FarmProfile(phone_number="+212611223344")
    assert profile.crop_type == "tomatoes"
    assert profile.acreage_hectares == 10.0
    assert profile.preferred_language == "french"


def test_sensor_telemetry_payload_valid():
    from app.schemas import SensorTelemetryPayload
    telemetry = SensorTelemetryPayload(
        farm_id="+212600000000",
        timestamp="2026-07-31T14:00:00Z",
        soil_moisture_vwc=16.5,
        depth_cm=15,
        battery_level=94
    )
    assert telemetry.farm_id == "+212600000000"
    assert telemetry.soil_moisture_vwc == 16.5
    assert telemetry.depth_cm == 15
    assert telemetry.battery_level == 94


def test_sensor_telemetry_payload_invalid_vwc():
    from app.schemas import SensorTelemetryPayload
    with pytest.raises(ValidationError):
        SensorTelemetryPayload(
            farm_id="+212600000000",
            timestamp="2026-07-31T14:00:00Z",
            soil_moisture_vwc=105.0  # Invalid: > 100%
        )

    with pytest.raises(ValidationError):
        SensorTelemetryPayload(
            farm_id="+212600000000",
            timestamp="2026-07-31T14:00:00Z",
            soil_moisture_vwc=-5.0  # Invalid: < 0%
        )


def test_sensor_telemetry_payload_defaults():
    from app.schemas import SensorTelemetryPayload
    telemetry = SensorTelemetryPayload(
        farm_id="+212600000000",
        timestamp="2026-07-31T14:00:00Z",
        soil_moisture_vwc=22.0
    )
    assert telemetry.depth_cm == 15
    assert telemetry.battery_level == 100

