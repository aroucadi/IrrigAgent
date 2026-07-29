from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any


class QualityDefectReason(str, Enum):
    NONE = "NONE"
    CORRUPT_OR_INVALID = "CORRUPT_OR_INVALID"
    BLURRY = "BLURRY"
    TOO_DARK = "TOO_DARK"
    TOO_BRIGHT = "TOO_BRIGHT"
    RESOLUTION_TOO_LOW = "RESOLUTION_TOO_LOW"


class PreFilterConfig(BaseModel):
    enabled: bool = Field(default=True, description="Master feature flag for pre-filter evaluation")
    blur_threshold: float = Field(default=100.0, description="Minimum Laplacian variance required for sharpness")
    min_mean_luminance: float = Field(default=40.0, description="Minimum mean grayscale intensity (0-255)")
    max_mean_luminance: float = Field(default=220.0, description="Maximum mean grayscale intensity (0-255)")
    max_dark_pixel_ratio: float = Field(default=0.40, description="Maximum allowed ratio of pixels < 15 intensity")
    max_bright_pixel_ratio: float = Field(default=0.35, description="Maximum allowed ratio of pixels > 245 intensity")
    min_width_px: int = Field(default=200, description="Minimum allowed image width in pixels")
    min_height_px: int = Field(default=200, description="Minimum allowed image height in pixels")


class ImageQualityMetrics(BaseModel):
    width: int = Field(description="Width of image in pixels")
    height: int = Field(description="Height of image in pixels")
    laplacian_variance: float = Field(description="Computed sharpness score (higher is sharper)")
    mean_luminance: float = Field(description="Average grayscale brightness (0.0 to 255.0)")
    dark_pixel_ratio: float = Field(description="Ratio of near-black pixels (0.0 to 1.0)")
    bright_pixel_ratio: float = Field(description="Ratio of near-white/glare pixels (0.0 to 1.0)")
    latency_ms: float = Field(description="Total pre-filter execution time in milliseconds")


class QualityCheckResult(BaseModel):
    is_acceptable: bool = Field(description="True if image passed all heuristics and can proceed to AI classifier")
    defect_reason: QualityDefectReason = Field(default=QualityDefectReason.NONE, description="Primary quality defect if failed")
    user_feedback_text: Optional[str] = Field(default=None, description="Actionable retake instructions if failed")
    metrics: Optional[ImageQualityMetrics] = Field(default=None, description="Raw numerical diagnostics")



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
    planting_date: Optional[str] = None
    is_mature_orchard: bool = False


class FAO56CropEntry(BaseModel):
    crop_type: str
    display_name: str
    kc_ini: float
    kc_mid: float
    kc_end: float
    stage_lengths_days: dict[str, int]
    is_perennial: bool = False


class ETcCalculationResult(BaseModel):
    et0_mm: float
    kc_applied: float
    etc_mm: float
    growth_stage: str
    days_since_planting: Optional[int] = None
    notice: Optional[str] = None




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


class SessionState(str, Enum):
    IDLE = "IDLE"
    COLLECTING_PINS = "COLLECTING_PINS"
    VALIDATING = "VALIDATING"


class LocationPin(BaseModel):
    latitude: float
    longitude: float
    timestamp: Optional[str] = None


class PinCollectionSession(BaseModel):
    phone_number: str
    state: SessionState = SessionState.IDLE
    pins: list[LocationPin] = Field(default_factory=list)
    started_at: Optional[str] = None
    updated_at: Optional[str] = None


class ParcelBoundary(BaseModel):
    type: str = "Polygon"
    coordinates: list[list[list[float]]]
    area_hectares: float
    perimeter_m: Optional[float] = None
    updated_at: Optional[str] = None


class SentinelScene(BaseModel):
    scene_id: str
    acquisition_date: str
    cloud_cover_percentage: float
    bbox: list[float]
    bands: Optional[dict[str, Any]] = None


class CanopyHealthReport(BaseModel):
    parcel_area_ha: float
    crop_type: str = "Tomatoes"
    capture_date: str
    cloud_cover_percent: float = 0.0
    ndvi_mean: float
    healthy_percent: float
    moderate_percent: float
    stressed_percent: float
    recommendation: str
    media_id: Optional[str] = None
    image_bytes: Optional[bytes] = None
