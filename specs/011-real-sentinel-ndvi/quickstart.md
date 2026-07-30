# Quickstart & Verification Guide: Real Sentinel Imagery Discovery and NDVI Computation

**Feature**: `011-real-sentinel-ndvi` | **Date**: 2026-07-30

## 1. Environment & Setup

Ensure virtual environment is active and project dependencies are installed:

```bash
# Verify Python version (3.11+)
python --version

# Install updated dependencies (including rasterio)
pip install -r requirements.txt
```

---

## 2. Automated Test Verification

Run the dedicated Sentinel satellite pipeline test suite using `pytest`:

```bash
# Run unit tests for real Sentinel discovery, band math, fallback, and fail-closed protocol
pytest tests/unit/test_sentinel_canopy_heatmap.py -v

# Run full project test suite to verify 100% zero-broken-tests policy
pytest tests/
```

---

## 3. Key Verification Scenarios

### Scenario 1: Primary Discovery Success (SC-001)
- **Action**: Call `generate_canopy_report()` with a mocked Element84 STAC response containing a valid 4.1% cloud scene captured on `2026-07-28`.
- **Expected Outcome**:
  - `report.is_available` is `True`
  - `report.capture_date` equals `"2026-07-28"`
  - `report.cloud_cover_percent` equals `4.1`
  - `report.image_bytes` is a non-empty PNG byte stream

### Scenario 2: Fail-Closed No Imagery Available (SC-002)
- **Action**: Call `generate_canopy_report()` with mocked STAC responses where all scenes have >20% cloud cover or zero scenes exist.
- **Expected Outcome**:
  - `report.is_available` is `False`
  - `report.image_bytes` is `None`
  - `report.no_data_reason` explains cloud cover / missing scene status
  - `report.healthy_percent`, `moderate_percent`, `stressed_percent` are `0.0`

### Scenario 3: Deterministic Input Sensitivity (SC-003)
- **Action**: Pass two distinct mocked geographic parcel geometries and date ranges to `generate_canopy_report()`.
- **Expected Outcome**: Computed NDVI mean reflectance values differ deterministically between the two runs, proving output depends on input data rather than synthetic hardcoded patterns.

### Scenario 4: Primary API Fallback to Copernicus (SC-004)
- **Action**: Simulate HTTP 500 / timeout error from Element84 primary STAC catalog while Copernicus secondary STAC catalog returns a valid clear scene.
- **Expected Outcome**: System successfully retries against Copernicus and returns a valid `CanopyHealthReport`.
