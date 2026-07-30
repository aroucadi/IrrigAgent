# Walkthrough: Real Sentinel Imagery Discovery and NDVI Computation

**Feature**: `011-real-sentinel-ndvi` | **Date**: 2026-07-30 | **Status**: Completed & Verified

## Overview

Successfully replaced the synthetic data generator in `app/sentinel.py` with real satellite imagery discovery and real NDVI band computation, resolving **BUG-002** from `backlog.md`.

---

## Key Changes Made

### 1. Dependencies & Data Schemas
- **[requirements.txt](file:///d:/rouca/DVM/workPlace/IrrigAgent/requirements.txt)**: Added `rasterio>=1.3.0` for windowed COG HTTP Range reads.
- **[app/schemas.py](file:///d:/rouca/DVM/workPlace/IrrigAgent/app/schemas.py)**: Added `is_available: bool = True` and `no_data_reason: Optional[str] = None` to `CanopyHealthReport`.

### 2. Core Sentinel Module (`app/sentinel.py`)
- **Constants & Metadata Dataclass**: Defined `MAX_CLOUD_COVER_PERCENT = 20.0`, `SEARCH_RECENCY_DAYS = 30`, and `SentinelSceneMetadata`.
- **`discover_sentinel2_scene(bbox)`**: Queries Element84 Earth Search STAC API (`https://earth-search.aws.element84.com/v1/search`) for `sentinel-2-l2a` scenes within the last 30 days and cloud cover <= 20%. Isolated try/except block automatically falls back to querying the Copernicus Data Space STAC catalog (`https://catalogue.dataspace.copernicus.eu/stac/search`) if Element84 yields 0 scenes or errors.
- **`fetch_sentinel2_bands(scene, bbox)`**: Performs windowed Range reads for Red (B04) and NIR (B08) Cloud-Optimized GeoTIFF (COG) band assets using `rasterio` (`/vsicurl/`), scaling raw reflectance values.
- **`generate_canopy_report(...)`**: Orchestrates discovery, real band math `(NIR - Red) / (NIR + Red)`, parcel polygon raster masking, and actual metadata pass-through (true capture date, true cloud cover %).
- **Fail-Closed Protocol**: Returns a structured report with `is_available=False`, `image_bytes=None`, and explanatory text when 0 usable scenes exist.

### 3. Webhook Handler (`app/main.py`)
- Updated `/heatmap` handler to check `report.is_available`. When imagery is unavailable, sends an informative text message with `no_data_reason` rather than attempting image upload.

### 4. Automated Tests (`tests/unit/test_sentinel_canopy_heatmap.py`)
- `test_real_sentinel_discovery_element84_success`: Verifies Element84 scene selection.
- `test_real_sentinel_discovery_fallback_to_copernicus`: Verifies Copernicus STAC fallback when Element84 fails.
- `test_sentinel2_bands_retrieval`: Verifies COG band pixel array extraction and scaling.
- `test_real_sentinel_fail_closed_no_scenes`: Verifies fail-closed response when 0 clear scenes exist.
- `test_generate_canopy_report_success`: Verifies full report pipeline with true capture metadata.
- `test_real_sentinel_distinct_inputs_produce_distinct_results` (**SC-003**): Verifies two distinct mock inputs produce non-synthetic, distinct NDVI results (fails against old hardcoded implementation).

---

## Verification & Test Results

```bash
pytest tests/
```

**Output**:
```text
131 passed, 1 warning in 16.15s
```

- **Zero-Broken-Tests Gate**: 131/131 unit and integration tests passing.
- **Deterministic Math & SC Verification**: SC-001, SC-002, SC-003, and SC-004 verified.
