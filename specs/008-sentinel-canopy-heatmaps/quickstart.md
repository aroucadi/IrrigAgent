# Quickstart Validation Guide: Sentinel-2 Canopy Heatmaps & Multi-Pin Parcel Collection

This guide details how to validate the multi-pin location collection state machine, parcel polygon geometry validation, and Sentinel-2 canopy heatmap rendering pipeline.

## Prerequisites

1. Active Python 3.11 virtual environment (`.venv`).
2. Installed dependencies: `pytest`, `shapely`, `pydantic`, `numpy`, `rasterio` (or `pillow`/`matplotlib` for visual rendering test).

## Validation Scenarios

### 1. Multi-Pin WhatsApp Collection State Machine & Shoelace Area Calculation
Run unit test suite verifying step-by-step pin state persistence and polygon geometry checks:

```bash
pytest tests/unit/test_parcel_pin_collection.py -v
```

Expected Output:
- 4 pin collection steps transition state correctly (`IDLE` -> `COLLECTING_PINS` -> `VALIDATING` -> `IDLE`).
- Shoelace area calculation for standard 4-corner 8.4 ha tomato parcel returns $8.40 \pm 0.1$ ha.
- Self-intersecting polygon (figure-8 sequence) fails `is_simple` check and returns error.
- Micro-parcel (<0.1 ha) and macro-parcel (>200 ha) fail boundary validation rules.

### 2. Sentinel-2 NDVI Calculation & Masking Pipeline
Run unit test suite verifying satellite band math and raster image generation:

```bash
pytest tests/unit/test_sentinel_canopy_heatmap.py -v
```

Expected Output:
- $NDVI = (B08 - B04) / (B08 + B04)$ calculation is exact across test matrices.
- Non-farm pixels outside parcel polygon boundary are masked/transparent.
- High-contrast color mapping maps $\le 0.3$ to Red, $0.3-0.5$ to Yellow, and $>0.6$ to Dark Green.
- Generated PNG heatmap artifact contains watermark and scale legend bar.

### 3. WhatsApp Integration Webhook Flow (End-to-End Simulation)
Run integration test suite simulating WhatsApp webhook location attachments:

```bash
pytest tests/integration/test_whatsapp_sentinel_flow.py -v
```

Expected Output:
- Sequential HTTP POST requests containing location payloads update session state.
- Receiving "DONE" triggers polygon validation, GeoJSON persistence in Firestore mockup, and sends static map preview payload.
- Sending "/heatmap" triggers satellite pipeline mock and responds with media upload call and formatted text caption.

### 4. Direct Manual Verification Script
Run the scratch test script to inspect a rendered heatmap output locally:

```bash
python scripts/demo_sentinel_heatmap.py
```

Check output PNG saved at `data/sample_heatmap_output.png`.
