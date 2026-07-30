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
    NO_LEAF_DETECTED = "NO_LEAF_DETECTED"


class PreFilterConfig(BaseModel):
    enabled: bool = Field(default=True, description="Master feature flag for pre-filter evaluation")
    blur_threshold: float = Field(default=100.0, description="Minimum Laplacian variance required for sharpness")
    min_mean_luminance: float = Field(default=40.0, description="Minimum mean grayscale intensity (0-255)")
    max_mean_luminance: float = Field(default=220.0, description="Maximum mean grayscale intensity (0-255)")
    max_dark_pixel_ratio: float = Field(default=0.40, description="Maximum allowed ratio of pixels < 15 intensity")
    max_bright_pixel_ratio: float = Field(default=0.35, description="Maximum allowed ratio of pixels > 245 intensity")
    min_width_px: int = Field(default=400, description="Minimum allowed image width in pixels")
    min_height_px: int = Field(default=400, description="Minimum allowed image height in pixels")
    min_hue_deg: int = Field(default=35, description="Minimum green foliage HSV hue angle in degrees")
    max_hue_deg: int = Field(default=85, description="Maximum green foliage HSV hue angle in degrees")
    min_foliage_ratio: float = Field(default=0.30, description="Minimum required green foliage pixel ratio")


class ImageQualityMetrics(BaseModel):
    width: int = Field(description="Width of image in pixels")
    height: int = Field(description="Height of image in pixels")
    laplacian_variance: float = Field(description="Computed sharpness score (higher is sharper)")
    mean_luminance: float = Field(description="Average grayscale brightness (0.0 to 255.0)")
    dark_pixel_ratio: float = Field(description="Ratio of near-black pixels (0.0 to 1.0)")
    bright_pixel_ratio: float = Field(description="Ratio of near-white/glare pixels (0.0 to 1.0)")
    foliage_pixel_ratio: float = Field(default=0.0, description="Ratio of pixels in foliage green HSV range")
    latency_ms: float = Field(description="Total pre-filter execution time in milliseconds")


class QualityCheckResult(BaseModel):
    is_acceptable: bool = Field(description="True if image passed all heuristics and can proceed to AI classifier")
    defect_reason: QualityDefectReason = Field(default=QualityDefectReason.NONE, description="Primary quality defect if failed")
    user_feedback_text: Optional[str] = Field(default=None, description="Actionable retake instructions if failed")
    metrics: Optional[ImageQualityMetrics] = Field(default=None, description="Raw numerical diagnostics")


class VisionClassificationResult(BaseModel):
    vision_engine: str = Field(description="Active classification engine")
    pathogen_identified: str = Field(description="Primary disease identifier or ONSSA code")
    symptom_name_fr: Optional[str] = Field(default=None, description="French/Darija symptom description")
    raw_confidence: float = Field(description="Uncalibrated output score 0.0 to 1.0")
    calibrated_confidence: float = Field(description="Temperature-scaled confidence score 0.0 to 1.0")
    confidence_tier: str = Field(description="Tier classification: high, medium, low")
    fail_closed_active: bool = Field(description="True if calibrated confidence < 0.75 suppressed active chemical names")
    onssa_product_pointer: Optional[str] = Field(default=None, description="Authorized ONSSA chemical product")
    disclaimer_included: bool = Field(default=True, description="Verification of mandatory ONSSA disclaimer")
    response_text: str = Field(description="Final WhatsApp advisory message text")


class BoundingBox(BaseModel):
    xmin: float = Field(ge=0.0, le=1.0)
    ymin: float = Field(ge=0.0, le=1.0)
    xmax: float = Field(ge=0.0, le=1.0)
    ymax: float = Field(ge=0.0, le=1.0)


class IAVDatasetRecord(BaseModel):
    sample_id: str = Field(description="Unique IAV record identifier")
    image_path: Optional[str] = Field(default=None, description="Path to image asset")
    crop_type: str = Field(description="Target crop category (tomatoes or citrus)")
    disease_onssa_code: str = Field(description="ONSSA primary disease registration code")
    severity_index: int = Field(ge=1, le=5, description="Disease severity rating Grade 1 to 5")
    bounding_boxes: list[BoundingBox] = Field(default_factory=list, description="Lesion bounding box list")
    region: str = Field(default="Souss-Massa", description="Collection region (Souss-Massa or Gharb)")
    cultivar: Optional[str] = Field(default=None, description="Moroccan crop cultivar name")




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
    is_available: bool = True
    no_data_reason: Optional[str] = None



class VoiceIntentStatus(str, Enum):
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"


class VoiceIntentType(str, Enum):
    MODIFY_IRRIGATION = "MODIFY_IRRIGATION"
    INCREASE_IRRIGATION = "INCREASE_IRRIGATION"
    DECREASE_IRRIGATION = "DECREASE_IRRIGATION"
    SKIP_IRRIGATION = "SKIP_IRRIGATION"


class PendingVoiceIntentPayload(BaseModel):
    intent_type: VoiceIntentType = Field(default=VoiceIntentType.MODIFY_IRRIGATION)
    proposed_adjustment_minutes: int = Field(default=15)
    confidence_score: float = Field(ge=0.0, le=1.0)
    transcribed_text: str
    created_at: str
    expires_at: str
    status: VoiceIntentStatus = Field(default=VoiceIntentStatus.AWAITING_CONFIRMATION)


class PendingVoiceIntentDoc(BaseModel):
    pending_voice_intent: PendingVoiceIntentPayload

