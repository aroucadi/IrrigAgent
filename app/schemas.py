from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class HealthCheckResponse(BaseModel):
    status: str
    app: str
    version: str
    voice_teaser_enabled: bool


class FarmProfile(BaseModel):
    phone: str
    region: str
    crop: str
    flow_rate_lph: float
    baseline_minutes: int


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
