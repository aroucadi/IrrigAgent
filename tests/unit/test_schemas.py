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
