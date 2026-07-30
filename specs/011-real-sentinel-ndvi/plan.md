# Implementation Plan: Real Sentinel Imagery Discovery and NDVI Computation

**Branch**: `011-real-sentinel-ndvi` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/011-real-sentinel-ndvi/spec.md)

**Input**: Feature specification from `/specs/011-real-sentinel-ndvi/spec.md`

## Summary

Replace synthetic random data generation in `app/sentinel.py` (`fetch_sentinel2_bands`) with real satellite imagery discovery and real NDVI band computation, resolving BUG-002 from `backlog.md`. The implementation queries Element84's Earth Search STAC API for Sentinel-2 Level-2A scenes with automated fallback to the Copernicus Data Space STAC catalog. For selected clear scenes (cloud cover <= 20%), real Red (B04) and NIR (B08) Cloud-Optimized GeoTIFF (COG) band pixels are retrieved via windowed HTTP Range requests (`rasterio` `/vsicurl/`) and clipped to the farm parcel polygon for NDVI calculation `(NIR - Red) / (NIR + Red)`. If zero clear scenes exist within 30 days, the system executes a fail-closed protocol returning a clear explanation without generating heatmaps or synthetic data.

---

## Technical Context

**Language/Version**: Python 3.11+ (matching project standard)

**Primary Dependencies**:
- `httpx==0.27.2`: STAC REST API discovery queries for Element84 and Copernicus catalogs.
- `rasterio>=1.3.0`: Partial/windowed HTTP Range-request band reads directly against remote Cloud-Optimized GeoTIFF (COG) asset URLs via `/vsicurl/`.

**Dependency Decision (DOCUMENTED IN RESEARCH.MD)**:
- **Selected Path**: **Option 1 (Windowed HTTP Range Requests via `rasterio`)**.
- **Container & Dockerfile Impact**: PyPI `rasterio` Linux x86_64 wheels (`manylinux2014`) ship precompiled GDAL binaries bundled directly inside the Python wheel. Therefore, **no OS-level `apt-get install gdal-bin libgdal-dev` system packages are needed** in `Dockerfile`. Dockerfile remains `FROM python:3.11-slim`. Image size increases by ~50MB and build times remain fast.

**Storage**: Fresh computation per request for pilot tier (no persistent Firestore caching added in this pass, per plan architecture guidance).

**Testing**: Pytest with `httpx` and `rasterio` mocking (following `tests/unit/test_weather.py` pattern) ensuring 100% offline test suite execution.

**Target Platform**: GCP Cloud Run (`python:3.11-slim` container).

**Project Type**: Web service (FastAPI backend).

**Performance Goals**: End-to-end scene discovery + windowed band fetch + NDVI rendering in **< 3.0 seconds**, well within Meta WhatsApp 15-second webhook SLA.

**Constraints**:
- 100% keyless (Element84 and Copernicus STAC public APIs).
- Hard constraint: Zero synthetic/random data reachable outside named test fixtures.
- Fail-closed output when 0 usable scenes exist.

**Scale/Scope**: Solo founder pilot tier (2-3 active pilot farms).

---

## Constitution Check

*GATE: Must pass before execution.*

- [x] **I. Human-in-the-Loop**: Informational canopy report only; no automated hardware/solenoid action triggered.
- [x] **II. Rule-Based First**: Pure deterministic array math `(NIR - Red) / (NIR + Red)`; zero LLM dependency.
- [x] **III. Mandatory ONSSA Disclaimer**: N/A for canopy health; if referenced in disease triage, ONSSA disclaimer rules remain untouched.
- [x] **IV. Sandbox-Only Messaging**: Delivery stays strictly within Meta WhatsApp Cloud API sandbox tier.
- [x] **V. Strict Scope Boundary**: No hardware control, payment billing, or soil sensors introduced.
- [x] **VI. End-to-End Demoability**: Testable via pytest and runnable over WhatsApp sandbox webhook.
- [x] **VII. Infrastructure as Code**: Application container dependency addition only (`requirements.txt`); no cloud infrastructure changes required.
- [x] **VIII. Quality, Security & Automated Verification Gates**: 100% pass rate maintained on `pytest tests/`, zero secrets in code, deterministic test assertions.

---

## Project Structure

### Documentation (this feature)

```text
specs/011-real-sentinel-ndvi/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technology decisions & rasterio COG evaluation
├── data-model.md        # SentinelSceneMetadata & updated CanopyHealthReport schema
├── quickstart.md        # Verification & test execution guide
└── contracts/
    └── sentinel-api-contract.md # STAC REST API & internal sentinel module interfaces
```

### Source Code (repository root)

```text
app/
├── sentinel.py          # Implement real STAC discovery, windowed COG band reads & fail-closed logic
├── schemas.py           # Update CanopyHealthReport with is_available & no_data_reason fields
└── main.py              # WhatsApp webhook handler integration (unchanged API contract)

requirements.txt         # Add rasterio>=1.3.0

tests/
└── unit/
    └── test_sentinel_canopy_heatmap.py # Unit & integration tests for STAC discovery, fallback & fail-closed
```

**Structure Decision**: Single Python project structure in `app/`, with unit test suite in `tests/unit/`.

---

## Implementation Outline & Tasks

### Step 1: Update Schema & Dependencies
- Add `rasterio>=1.3.0` to `requirements.txt`.
- Update `CanopyHealthReport` in `app/schemas.py` to add `is_available: bool = True` and `no_data_reason: Optional[str] = None`.

### Step 2: Implement Real STAC Discovery (`app/sentinel.py`)
- Define named constants: `MAX_CLOUD_COVER_PERCENT = 20.0`, `SEARCH_RECENCY_DAYS = 30`.
- Create `SentinelSceneMetadata` dataclass.
- Implement `discover_sentinel2_scene(bbox: list[float], recency_days: int = 30, max_cloud_cover: float = 20.0) -> Optional[SentinelSceneMetadata]`.
- Query Element84 `POST https://earth-search.aws.element84.com/v1/search`.
- Wrap in isolated try/except with 5s timeout; fall back to Copernicus STAC `POST https://catalogue.dataspace.copernicus.eu/stac/search` if Element84 returns no items or errors.
- Select single most recent scene with `eo:cloud_cover` <= 20%.

### Step 3: Implement COG Windowed Band Extraction (`app/sentinel.py`)
- Implement `fetch_sentinel2_bands(scene: SentinelSceneMetadata, bbox: list[float]) -> Tuple[np.ndarray, np.ndarray, str, float]`.
- Use `rasterio.open("/vsicurl/" + asset_url)` to perform windowed read of Band 04 (Red) and Band 08 (NIR) covering `bbox`.
- Return actual Red/NIR numpy pixel arrays along with true capture date and true cloud cover percentage.

### Step 4: Implement Fail-Closed Protocol & Report Orchestration
- Update `generate_canopy_report()`:
  - Call scene discovery.
  - If no scene is returned (`None`), build fail-closed `CanopyHealthReport`: `is_available=False`, `image_bytes=None`, `healthy_percent=0.0`, `moderate_percent=0.0`, `stressed_percent=0.0`, `no_data_reason="..."`, `recommendation="..."`.
  - If usable scene returned, retrieve band arrays via `fetch_sentinel2_bands`, compute polygon-masked NDVI array, calculate actual health percentages, render heatmap bytes, and populate `CanopyHealthReport` with true capture date and true cloud cover %.

### Step 5: Test Suite Verification (`tests/unit/test_sentinel_canopy_heatmap.py`)
- Write `test_real_sentinel_discovery_element84_success` asserting Element84 scene selection.
- Write `test_real_sentinel_discovery_fallback_to_copernicus` asserting Copernicus fallback on Element84 failure.
- Write `test_real_sentinel_fail_closed_no_scenes` asserting fail-closed report when cloud cover > 20% or 0 scenes returned.
- Write `test_real_sentinel_distinct_inputs_produce_distinct_results` asserting two different mock inputs produce distinct output statistics (satisfying SC-003).
- Execute full test suite `pytest tests/` to confirm 100% pass rate.
