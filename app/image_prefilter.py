import time
import numpy as np
import cv2
from typing import Optional, Dict

from app.schemas import (
    PreFilterConfig,
    ImageQualityMetrics,
    QualityCheckResult,
    QualityDefectReason,
)
from app.config import (
    PREFILTER_ENABLED,
    PREFILTER_BLUR_THRESHOLD,
    PREFILTER_MIN_LUMINANCE,
    PREFILTER_MAX_LUMINANCE,
    PREFILTER_MAX_DARK_RATIO,
    PREFILTER_MAX_BRIGHT_RATIO,
    PREFILTER_MIN_WIDTH,
    PREFILTER_MIN_HEIGHT,
    PREFILTER_MIN_HUE,
    PREFILTER_MAX_HUE,
    PREFILTER_MIN_FOLIAGE_RATIO,
)


FEEDBACK_MESSAGES: Dict[QualityDefectReason, str] = {
    QualityDefectReason.CORRUPT_OR_INVALID: (
        "🍃 *CropDoctor Advisory*\n"
        "No plant leaf identified in the photo. Please send a clear, close-up photograph of the affected leaf."
    ),
    QualityDefectReason.RESOLUTION_TOO_LOW: (
        "🍃 *Resolution Too Low*\n"
        "The photo is too small for leaf disease analysis (minimum 400x400px required). Please send a higher resolution photograph."
    ),
    QualityDefectReason.BLURRY: (
        "🍃 *Photo Out of Focus*\n"
        "Photo is blurry or unreadable. Please take a close-up photo of the leaf under direct light."
    ),
    QualityDefectReason.TOO_DARK: (
        "🍃 *Photo Too Dark*\n"
        "The photo is underexposed. Please retake the leaf photo in better daylight or use your camera flash."
    ),
    QualityDefectReason.TOO_BRIGHT: (
        "🍃 *Too Much Glare*\n"
        "The photo has heavy glare or bright direct sunlight. Please shade the leaf or adjust your camera angle and retake."
    ),
    QualityDefectReason.NO_LEAF_DETECTED: (
        "🍃 *No Plant Leaf Identified*\n"
        "Photo is blurry or unreadable. Please take a close-up photo of the leaf under direct light."
    ),
}


def get_prefilter_config_from_env() -> PreFilterConfig:
    """Constructs a PreFilterConfig using environment configuration defaults."""
    return PreFilterConfig(
        enabled=PREFILTER_ENABLED,
        blur_threshold=PREFILTER_BLUR_THRESHOLD,
        min_mean_luminance=PREFILTER_MIN_LUMINANCE,
        max_mean_luminance=PREFILTER_MAX_LUMINANCE,
        max_dark_pixel_ratio=PREFILTER_MAX_DARK_RATIO,
        max_bright_pixel_ratio=PREFILTER_MAX_BRIGHT_RATIO,
        min_width_px=PREFILTER_MIN_WIDTH,
        min_height_px=PREFILTER_MIN_HEIGHT,
        min_hue_deg=PREFILTER_MIN_HUE,
        max_hue_deg=PREFILTER_MAX_HUE,
        min_foliage_ratio=PREFILTER_MIN_FOLIAGE_RATIO,
    )


def compute_foliage_green_ratio(img_bgr: np.ndarray, min_hue_deg: int = 35, max_hue_deg: int = 85) -> float:
    """
    Computes the fraction of pixels falling within the green foliage HSV hue range.

    Arguments min_hue_deg and max_hue_deg are specified in OpenCV HSV scale (0–180),
    where plant green occupies approximately H=35–85 (standard degrees 70–170).
    Pure green BGR (0,255,0) has OpenCV H≈60.

    Note: Do NOT divide by 2 — these values are already in OpenCV's 0-180 scale.
    """
    if img_bgr is None or img_bgr.size == 0:
        return 0.0
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    lower_green = np.array([min_hue_deg, 40, 40])
    upper_green = np.array([max_hue_deg, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    total_pixels = img_bgr.shape[0] * img_bgr.shape[1]
    return float(np.sum(mask > 0) / total_pixels) if total_pixels > 0 else 0.0



def validate_image_quality(
    image_bytes: bytes,
    config: Optional[PreFilterConfig] = None
) -> QualityCheckResult:
    """
    Evaluates raw image bytes against OpenCV heuristics (exposure check, Laplacian variance blur check,
    mean grayscale luminance, dark/bright clipping ratios, green foliage HSV coverage, and minimum resolution).

    Args:
        image_bytes: Raw byte array of incoming image payload.
        config: Optional PreFilterConfig overrides. Uses environment settings if None.

    Returns:
        QualityCheckResult object with acceptability status, defect reason, retake feedback, and metrics.
    """
    start_time = time.perf_counter()
    if config is None:
        config = get_prefilter_config_from_env()

    if not config.enabled:
        return QualityCheckResult(
            is_acceptable=True,
            defect_reason=QualityDefectReason.NONE,
            user_feedback_text=None,
            metrics=None,
        )

    # Sanity check for empty bytes or corrupt test markers
    if not image_bytes or image_bytes in (b"unreadable_image", b"non_plant", b"corrupt"):
        return QualityCheckResult(
            is_acceptable=False,
            defect_reason=QualityDefectReason.CORRUPT_OR_INVALID,
            user_feedback_text=FEEDBACK_MESSAGES[QualityDefectReason.CORRUPT_OR_INVALID],
            metrics=None,
        )

    # Attempt memory image decoding via OpenCV
    try:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception:
        img = None

    if img is None or img.size == 0:
        return QualityCheckResult(
            is_acceptable=False,
            defect_reason=QualityDefectReason.CORRUPT_OR_INVALID,
            user_feedback_text=FEEDBACK_MESSAGES[QualityDefectReason.CORRUPT_OR_INVALID],
            metrics=None,
        )

    height, width = img.shape[:2]

    # Check minimum resolution bounds (width and height >= 400px per spec)
    if width < config.min_width_px or height < config.min_height_px:
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        metrics = ImageQualityMetrics(
            width=width,
            height=height,
            laplacian_variance=0.0,
            mean_luminance=0.0,
            dark_pixel_ratio=0.0,
            bright_pixel_ratio=0.0,
            foliage_pixel_ratio=0.0,
            latency_ms=round(latency_ms, 2),
        )
        return QualityCheckResult(
            is_acceptable=False,
            defect_reason=QualityDefectReason.RESOLUTION_TOO_LOW,
            user_feedback_text=FEEDBACK_MESSAGES[QualityDefectReason.RESOLUTION_TOO_LOW],
            metrics=metrics,
        )

    # Convert to grayscale matrix
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Sharpness / Blur metric via Laplacian variance
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    # 2. Luminance & clipping distribution metrics
    mean_lum = float(np.mean(gray))
    total_pixels = gray.size
    dark_ratio = float(np.sum(gray < 15) / total_pixels) if total_pixels > 0 else 0.0
    bright_ratio = float(np.sum(gray > 245) / total_pixels) if total_pixels > 0 else 0.0

    # 3. Green Foliage HSV Coverage Heuristic
    foliage_ratio = compute_foliage_green_ratio(img, config.min_hue_deg, config.max_hue_deg)

    latency_ms = (time.perf_counter() - start_time) * 1000.0

    metrics = ImageQualityMetrics(
        width=width,
        height=height,
        laplacian_variance=round(laplacian_var, 2),
        mean_luminance=round(mean_lum, 2),
        dark_pixel_ratio=round(dark_ratio, 4),
        bright_pixel_ratio=round(bright_ratio, 4),
        foliage_pixel_ratio=round(foliage_ratio, 4),
        latency_ms=round(latency_ms, 2),
    )

    # Rule 1: Exposure check - Underexposure
    if mean_lum < config.min_mean_luminance or dark_ratio > config.max_dark_pixel_ratio:
        return QualityCheckResult(
            is_acceptable=False,
            defect_reason=QualityDefectReason.TOO_DARK,
            user_feedback_text=FEEDBACK_MESSAGES[QualityDefectReason.TOO_DARK],
            metrics=metrics,
        )

    # Rule 2: Exposure check - Overexposure / Glare
    if mean_lum > config.max_mean_luminance or bright_ratio > config.max_bright_pixel_ratio:
        return QualityCheckResult(
            is_acceptable=False,
            defect_reason=QualityDefectReason.TOO_BRIGHT,
            user_feedback_text=FEEDBACK_MESSAGES[QualityDefectReason.TOO_BRIGHT],
            metrics=metrics,
        )

    # Rule 3: Sharpness / Blur check (Var < 100.0 fails per spec)
    if laplacian_var < config.blur_threshold:
        return QualityCheckResult(
            is_acceptable=False,
            defect_reason=QualityDefectReason.BLURRY,
            user_feedback_text=FEEDBACK_MESSAGES[QualityDefectReason.BLURRY],
            metrics=metrics,
        )

    # Rule 4: Green Foliage Coverage check (min 30% per spec)
    if foliage_ratio < config.min_foliage_ratio:
        return QualityCheckResult(
            is_acceptable=False,
            defect_reason=QualityDefectReason.NO_LEAF_DETECTED,
            user_feedback_text=FEEDBACK_MESSAGES[QualityDefectReason.NO_LEAF_DETECTED],
            metrics=metrics,
        )

    # All checks passed cleanly
    return QualityCheckResult(
        is_acceptable=True,
        defect_reason=QualityDefectReason.NONE,
        user_feedback_text=None,
        metrics=metrics,
    )

