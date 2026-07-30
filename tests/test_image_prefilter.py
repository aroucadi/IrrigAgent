import pytest
import numpy as np
import cv2
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import QualityDefectReason
from app.image_prefilter import validate_image_quality, compute_foliage_green_ratio
from app.cropdoctor import perform_cropdoctor_triage


def _create_sharp_image_bytes(width=400, height=400) -> bytes:
    """
    Helper to generate a sharp synthetic green image (simulates leaf photo).
    Uses green base color so foliage HSV ratio check ≥ 30% is satisfied.
    Uses dark grid stripes to produce high Laplacian variance (sharpness check).
    """
    img = np.zeros((height, width, 3), dtype=np.uint8)
    # Green base: BGR (40, 160, 40) → OpenCV HSV H≈60 → within foliage range [35,85]
    img[:, :, 0] = 40   # blue
    img[:, :, 1] = 160  # green
    img[:, :, 2] = 40   # red
    # Add sharp dark stripes for high Laplacian variance
    step_y = max(5, height // 10)
    step_x = max(5, width // 10)
    for i in range(0, height, step_y):
        img[i, :, :] = 10
    for j in range(0, width, step_x):
        img[:, j, :] = 10
    success, encoded = cv2.imencode(".jpg", img)
    assert success
    return encoded.tobytes()


def _create_green_leaf_image_bytes(width=400, height=400) -> bytes:
    """Helper to generate a sharp image with >30% green foliage HSV coverage."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    # Fill majority with a green tone (BGR: approx HSV hue ~60 deg = pure green)
    img[:, :, 1] = 180  # strong green channel
    img[:, :, 0] = 40   # low blue
    img[:, :, 2] = 40   # low red
    # Add sharp edge features for blur check
    for i in range(0, height, 20):
        img[i, :, 1] = 30
    success, encoded = cv2.imencode(".jpg", img)
    assert success
    return encoded.tobytes()


def _create_non_foliage_image_bytes(width=400, height=400) -> bytes:
    """Helper to generate a sharp image with NO green foliage (e.g. concrete/soil)."""
    img = np.full((height, width, 3), 128, dtype=np.uint8)
    # Red-brown tone - no green HSV presence
    img[:, :, 2] = 200  # high red
    img[:, :, 1] = 80   # low green
    img[:, :, 0] = 40   # low blue
    # Add sharp edge features for blur check
    for i in range(0, height, 20):
        img[i, :, :] = 30
    success, encoded = cv2.imencode(".jpg", img)
    assert success
    return encoded.tobytes()



def _create_blurry_image_bytes(width=400, height=400) -> bytes:
    """Helper to generate an out-of-focus synthetic image with balanced luminance."""
    img = np.full((height, width, 3), 128, dtype=np.uint8)
    # Add soft circle and heavy Gaussian blur
    cv2.circle(img, (200, 200), 80, (150, 150, 150), -1)
    blurred = cv2.GaussianBlur(img, (45, 45), 20.0)
    success, encoded = cv2.imencode(".jpg", blurred)
    assert success
    return encoded.tobytes()


def _create_dark_image_bytes(width=400, height=400) -> bytes:
    """Helper to generate an underexposed dark synthetic image."""
    img = np.full((height, width, 3), 10, dtype=np.uint8)
    success, encoded = cv2.imencode(".jpg", img)
    assert success
    return encoded.tobytes()


def _create_bright_image_bytes(width=400, height=400) -> bytes:
    """Helper to generate an overexposed bright/glare synthetic image."""
    img = np.full((height, width, 3), 245, dtype=np.uint8)
    success, encoded = cv2.imencode(".jpg", img)
    assert success
    return encoded.tobytes()


def test_sharp_image_passes():
    """Verify sharp image passes pre-filter checks."""
    image_bytes = _create_sharp_image_bytes()
    result = validate_image_quality(image_bytes)

    assert result.is_acceptable is True
    assert result.defect_reason == QualityDefectReason.NONE
    assert result.user_feedback_text is None
    assert result.metrics is not None
    assert result.metrics.laplacian_variance > 100.0


def test_blurry_image_rejected():
    """Verify blurry image is rejected with BLURRY defect."""
    image_bytes = _create_blurry_image_bytes()
    result = validate_image_quality(image_bytes)

    assert result.is_acceptable is False
    assert result.defect_reason == QualityDefectReason.BLURRY
    assert result.user_feedback_text is not None
    assert "blurry" in result.user_feedback_text.lower() or "focus" in result.user_feedback_text.lower()
    assert result.metrics is not None
    assert result.metrics.laplacian_variance < 100.0


def test_dark_image_rejected():
    """Verify underexposed image is rejected with TOO_DARK defect."""
    image_bytes = _create_dark_image_bytes()
    result = validate_image_quality(image_bytes)

    assert result.is_acceptable is False
    assert result.defect_reason == QualityDefectReason.TOO_DARK
    assert result.user_feedback_text is not None
    assert "dark" in result.user_feedback_text.lower() or "underexposed" in result.user_feedback_text.lower()


def test_bright_image_rejected():
    """Verify overexposed image is rejected with TOO_BRIGHT defect."""
    image_bytes = _create_bright_image_bytes()
    result = validate_image_quality(image_bytes)

    assert result.is_acceptable is False
    assert result.defect_reason == QualityDefectReason.TOO_BRIGHT
    assert result.user_feedback_text is not None
    assert "glare" in result.user_feedback_text.lower() or "bright" in result.user_feedback_text.lower()


def test_corrupt_or_invalid_bytes():
    """Verify corrupt byte streams are handled safely."""
    for bad_bytes in [b"", b"invalid_bytes_payload", b"unreadable_image"]:
        result = validate_image_quality(bad_bytes)
        assert result.is_acceptable is False
        assert result.defect_reason == QualityDefectReason.CORRUPT_OR_INVALID


def test_resolution_too_low():
    """Verify image below minimum width/height (< 400px) is rejected."""
    small_bytes = _create_sharp_image_bytes(width=100, height=100)
    result = validate_image_quality(small_bytes)

    assert result.is_acceptable is False
    assert result.defect_reason == QualityDefectReason.RESOLUTION_TOO_LOW


def test_resolution_threshold_exactly_400px():
    """Verify image at exactly 400x400 passes the resolution check."""
    boundary_bytes = _create_green_leaf_image_bytes(width=400, height=400)
    result = validate_image_quality(boundary_bytes)
    # If the image passes all quality criteria, it must not fail resolution
    assert result.defect_reason != QualityDefectReason.RESOLUTION_TOO_LOW


def test_compute_foliage_green_ratio_high_green():
    """Verify green foliage ratio computation returns high ratio for green image."""
    green_img = np.zeros((200, 200, 3), dtype=np.uint8)
    green_img[:, :, 1] = 180  # strong green
    green_img[:, :, 0] = 40
    green_img[:, :, 2] = 40
    ratio = compute_foliage_green_ratio(green_img, min_hue_deg=35, max_hue_deg=85)
    assert ratio >= 0.30, f"Expected foliage ratio >= 0.30, got {ratio}"


def test_compute_foliage_green_ratio_non_green():
    """Verify foliage ratio returns low value for non-green image."""
    red_img = np.zeros((200, 200, 3), dtype=np.uint8)
    red_img[:, :, 2] = 200  # red dominant
    red_img[:, :, 1] = 60
    red_img[:, :, 0] = 30
    ratio = compute_foliage_green_ratio(red_img, min_hue_deg=35, max_hue_deg=85)
    assert ratio < 0.30, f"Expected foliage ratio < 0.30 for non-green image, got {ratio}"


@pytest.mark.asyncio
async def test_cropdoctor_integration_bypasses_gemini():
    """Verify perform_cropdoctor_triage returns early on pre-filter failure without calling Gemini."""
    blurry_bytes = _create_blurry_image_bytes()
    response = await perform_cropdoctor_triage(blurry_bytes, crop_type="tomatoes")

    assert response["is_unreadable"] is True
    assert response["pathogen_identified"] == "unreadable"
    assert response["confidence_score"] == 0.0
    assert response["prefilter_defect"] == "BLURRY"
    assert "prefilter_metrics" in response


def test_rest_endpoint_prefilter():
    """Verify POST /cropdoctor/prefilter REST endpoint."""
    client = TestClient(app)
    sharp_bytes = _create_sharp_image_bytes()

    res = client.post(
        "/cropdoctor/prefilter",
        files={"file": ("leaf.jpg", sharp_bytes, "image/jpeg")}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_acceptable"] is True
    assert data["defect_reason"] == "NONE"
    assert "metrics" in data


def test_prefilter_latency_under_300ms():
    """Verify SC-001: Quality Gate evaluation completes in under 300ms."""
    sharp_bytes = _create_sharp_image_bytes(width=400, height=400)
    result = validate_image_quality(sharp_bytes)
    assert result.is_acceptable is True
    assert result.metrics is not None
    assert result.metrics.latency_ms < 300.0, f"Quality Gate latency {result.metrics.latency_ms}ms exceeded 300ms"

