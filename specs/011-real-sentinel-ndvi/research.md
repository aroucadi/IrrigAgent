# Research & Technology Decisions: Real Sentinel Imagery Discovery and NDVI Computation

**Feature**: `011-real-sentinel-ndvi` | **Date**: 2026-07-30

## 1. Dependency Decision: COG Band Pixel Extraction

### Options Evaluated

1. **Option 1 (Chosen): Windowed HTTP Range-Request Reads via `rasterio` (`/vsicurl/`)**
   - **Mechanism**: Sentinel-2 Level-2A assets hosted on AWS Element84 (`sentinel-cogs.s3.us-west-2.amazonaws.com`) are Cloud-Optimized GeoTIFFs (COGs). Using `rasterio.open("/vsicurl/" + asset_url)`, `rasterio` issues targeted HTTP Range requests (`GET` with `Range: bytes=...`) to download only the tile bytes and header data for the farm's small bounding box pixel window.
   - **Dependency**: Add `rasterio>=1.3.0` to `requirements.txt`.
   - **Container & Docker Impact**: Standard PyPI `rasterio` Linux x86_64 wheels (`manylinux2014`) bundle compiled GDAL C-libraries directly inside the wheel. No OS-level system package installation (`apt-get install gdal-bin libgdal-dev`) is required in `Dockerfile`. Dockerfile remains `FROM python:3.11-slim` with a modest ~50MB image size increment.
   - **Performance**: Fetches only ~50KB to 200KB of pixel data per band instead of downloading full 100MB+ scene files, reducing network band fetch latency to ~1.0–2.0 seconds.

2. **Option 2 (Rejected): Full System GDAL + OS Package Installation**
   - **Mechanism**: Installing system GDAL (`apt-get install gdal-bin libgdal-dev`) and compiling/linking rasterio.
   - **Drawback**: Adds >300MB to Docker container image, increases container build time by 2–4 minutes, and creates system dependency drift between local Windows environment and Cloud Run Linux container.

3. **Option 3 (Rejected): Pre-rendered Visual/NDVI Asset Fallback**
   - **Mechanism**: Using pre-rendered thumbnail/visual assets directly from the STAC item's assets dictionary without raw band math.
   - **Drawback**: Violates core spec requirement (User Story 2) requiring actual Red (B04) and NIR (B08) band reflectance math. Pre-rendered thumbnails are lossy 8-bit PNG/JPEG images unsuitable for precise NDVI calculations.

---

## 2. STAC Catalog API Discovery & Fallback Strategy

- **Primary Source**: Element84 Earth Search STAC API (`https://earth-search.aws.element84.com/v1/search`), Collection: `sentinel-2-l2a`.
- **Secondary Source**: Copernicus Data Space STAC catalog (`https://catalogue.dataspace.copernicus.eu/stac/search`).
- **Resilience & Fallback Pattern**:
  - Isolated `httpx.AsyncClient` calls wrapped in try/except blocks per source.
  - Per-source timeout of 5.0 seconds.
  - Search Parameters: Bounding box (`[min_lon, min_lat, max_lon, max_lat]`), datetime range (last 30 days formatted `YYYY-MM-DDT00:00:00Z/YYYY-MM-DDT23:59:59Z`), `eo:cloud_cover` <= 20%, sorted by `datetime` descending.
  - If Element84 returns no items, times out, or raises an HTTP error, the discovery function immediately queries Copernicus before determining availability.

---

## 3. Fail-Closed Protocol Strategy

- **Threshold Constants**:
  - `MAX_CLOUD_COVER_PERCENT = 20.0`
  - `SEARCH_RECENCY_DAYS = 30`
- **Fail-Closed Condition**:
  - Triggered when zero candidate scenes are found across all STAC catalogs meeting recency and cloud cover criteria.
- **Fail-Closed Payload**:
  - `is_available = False`
  - `image_bytes = None`
  - `healthy_percent = 0.0`, `moderate_percent = 0.0`, `stressed_percent = 0.0`
  - `no_data_reason = "No Sentinel-2 imagery found within the last 30 days below 20% cloud cover threshold."`
  - `recommendation = "No clear satellite imagery currently available for this field (searched last 30 days, max 20% cloud cover). Field-level inspection recommended."`

---

## 4. Storage & Caching Decision

- **Decision**: Fresh calculation per request for pilot scope (2-3 pilot farms).
- **Rationale**: Keeps architecture simple and stateless. Request volume is low during pilot testing. Caching can be introduced in a future pass if STAC rate limits or Cloud Run execution costs warrant it.

---

## 5. Performance & Webhook SLA Alignment

- **Execution Latency Budget**:
  - STAC discovery query: ~300ms
  - COG band Range reads (B04 + B08 window): ~1.5s
  - NDVI array math & Matplotlib heatmap generation: ~400ms
  - Total end-to-end latency: ~2.2s – 2.5s.
- **SLA Match**: Well under Meta WhatsApp 15-second HTTP webhook timeout limit. Webhook handlers can return synchronously or dispatch via `BackgroundTasks` matching existing project patterns in `main.py`.

---

## 6. Unit Testing & Mocking Strategy

- **STAC API Mocking**: Mock `httpx.AsyncClient.post` responses using `unittest.mock.patch` returning realistic STAC ItemCollection JSON structures (including scene ID, datetime, cloud cover %, and asset URLs for B04 and B08).
- **Band Data Mocking**: Mock `rasterio.open` or band extraction helper using `unittest.mock.patch` returning deterministic 2D `numpy.ndarray` reflectance values.
- **Verification Tests**:
  - `test_real_sentinel_discovery_element84_success`: Asserts Element84 selection.
  - `test_real_sentinel_discovery_fallback_to_copernicus`: Asserts fallback to Copernicus when Element84 fails.
  - `test_real_sentinel_fail_closed_no_scenes`: Asserts fail-closed response when cloud cover > 20% or 0 scenes returned.
  - `test_real_sentinel_distinct_inputs_produce_distinct_results`: Asserts two different mock inputs yield distinct non-synthetic outputs (satisfying SC-003).
