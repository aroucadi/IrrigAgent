from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any


class HealthCheckResponse(BaseModel):
    status: str
    app: str
    version: str
    voice_teaser_enabled: bool


class FarmProfile(BaseModel):
    phone_number: str
    location: Optional[Any] = Field(default="Agadir")
    crop_type: str = Field(default="tomatoes")
    acreage_hectares: float = Field(default=10.0, gt=0)
    preferred_language: str = Field(default="french")



class DailyAdvisoryJobResponse(BaseModel):
    status: str
    processed_count: int = Field(default=0, serialization_alias="processed_count")
    skipped_count: int = Field(default=0, serialization_alias="skipped_count")
    dispatched_count: Optional[int] = None
    failed_count: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True)


class WebhookVerification(BaseModel):
    hub_mode: str = Field(..., alias="hub.mode")
    hub_challenge: str = Field(..., alias="hub.challenge")
    hub_verify_token: str = Field(..., alias="hub.verify_token")

    model_config = ConfigDict(populate_by_name=True)
