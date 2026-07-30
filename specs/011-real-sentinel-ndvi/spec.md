# Feature Specification: Real Sentinel Imagery Discovery and NDVI Computation

**Feature Branch**: `011-real-sentinel-ndvi`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "Create a new feature spec — do not modify or bundle this into any existing spec. This replaces the synthetic data generation currently in app/sentinel.py with real satellite imagery discovery and real NDVI computation. This directly resolves BUG-002 from backlog.md..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Real Scene Discovery for Farm Parcel (Priority: P1)

As the system, I want to query real satellite catalogs for the most recent, usable Sentinel-2 imagery covering a farm's registered parcel, so that canopy health reports are based on actual satellite observations rather than fabricated data.

**Why this priority**: Core foundation required to replace synthetic random data generation with real satellite observation data for canopy health analysis.

**Independent Test**: Can be fully tested by providing parcel coordinates and asserting that the system queries the primary satellite catalog (with automatic fallback to the secondary catalog) and selects the single most recent scene meeting cloud cover criteria.

**Acceptance Scenarios**:

1. **Given** a farm parcel bounding box, **When** imagery discovery is executed and usable clear scenes (cloud cover <= 20% within 30 days) exist in the primary catalog, **Then** the single most recent scene is selected for processing.
2. **Given** the primary catalog returns no usable scenes or encounters a service failure, **When** imagery discovery executes, **Then** the system automatically queries the secondary catalog using an isolated fallback pattern and selects the most recent clear scene.

---

### User Story 2 - Real NDVI Computation from Satellite Bands (Priority: P1)

As the system, I want to compute NDVI from the real Red and Near-Infrared (NIR) band pixel data of the selected satellite scene, clipped to the farm's actual parcel polygon, so that the canopy health report reflects the real field conditions.

**Why this priority**: Ensures the canopy health index and spatial heatmap are computed from actual spectral reflectance values of the target farm field.

**Independent Test**: Can be fully tested by passing a selected scene asset reference, retrieving Red (B04) and NIR (B08) band pixel arrays, applying the parcel polygon mask, and validating that output statistics and capture metadata reflect true scene parameters.

**Acceptance Scenarios**:

1. **Given** a selected Sentinel-2 scene asset reference, **When** band processing executes, **Then** real Red (B04) and NIR (B08) pixel values are retrieved, masked to the parcel boundary, and processed using standard NDVI formula `(NIR - Red) / (NIR + Red)`.
2. **Given** computed NDVI pixel values and scene metadata, **When** the canopy health report is generated, **Then** the report includes the true capture date, actual cloud cover percentage, and spatial heatmap breakdown.

---

### User Story 3 - Fail-Closed When No Usable Real Imagery Exists (Priority: P2)

As a farmer, if no recent, clear-enough satellite imagery is available for my location, I want to be told that plainly, rather than receiving a report based on fabricated or outdated data.

**Why this priority**: Prevents misleading farm managers with false health reports when atmospheric conditions or satellite pass schedules yield no reliable observation data.

**Independent Test**: Can be fully tested by simulating scenarios where all available scenes exceed cloud cover thresholds or no scenes match the search window, verifying the system returns an explicit no-data response without generating heatmaps or health recommendations.

**Acceptance Scenarios**:

1. **Given** a query for a parcel where all returned scenes exceed the maximum cloud cover threshold or no scenes exist in the search window, **When** discovery completes, **Then** the system returns a fail-closed status stating clear imagery is unavailable, including the searched date range and reason.
2. **Given** a fail-closed no-imagery response, **When** output formatting occurs, **Then** no heatmap image, health percentages, or action recommendations are produced.

---

### Edge Cases

- What happens when the primary STAC catalog API times out or returns HTTP 5xx errors? The system catches the error independently per source and immediately attempts discovery via the secondary STAC catalog without failing the entire request flow.
- What happens when a scene passes cloud thresholds globally but the specific farm parcel within the scene is obscured by heavy cloud cover? Atmospheric pixel masking flags unresolvable pixels, ensuring unmasked clear field pixels are processed or triggering a fail-closed response if insufficient valid pixels remain.
- What happens when band asset downloads experience network interruption? Band retrieval operations utilize robust retries with explicit timeouts before gracefully triggering a fail-closed response.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST query the primary STAC catalog (Element84 Earth Search) for Sentinel-2 Level-2A scenes intersecting the farm parcel bounding box within a configurable recency window (default: 30 days), ordered by capture timestamp descending.
- **FR-002**: System MUST fall back to querying the secondary STAC catalog (Copernicus Data Space) if the primary catalog yields zero usable scenes or encounters API errors/timeouts.
- **FR-003**: System MUST isolate API client calls per catalog source using individual timeout limits so failure of one source does not block querying alternative sources.
- **FR-004**: System MUST filter candidate scenes against a configurable maximum acceptable cloud cover threshold (default: 20%), defined as a named constant.
- **FR-005**: System MUST select the single most recent candidate scene that satisfies both the recency window and cloud cover threshold.
- **FR-006**: System MUST retrieve real pixel data from Cloud-Optimized GeoTIFF (COG) Red (B04) and NIR (B08) band assets referenced by the selected scene metadata, explicitly excluding thumbnail/preview assets.
- **FR-007**: System MUST clip and mask band pixel arrays using the farm's validated spatial parcel polygon geometry.
- **FR-008**: System MUST compute NDVI values for each pixel within the parcel polygon using the mathematical formula `(NIR - Red) / (NIR + Red)`.
- **FR-009**: System MUST populate the output canopy health report with the selected scene's actual capture timestamp and true cloud cover percentage.
- **FR-010**: System MUST return a fail-closed "no clear imagery available" response whenever zero scenes meet cloud cover and recency criteria across all queried catalogs.
- **FR-011**: Fail-closed responses MUST contain the search date range and failure rationale, and MUST NOT contain heatmap image bytes, percentage health breakdowns, or agronomic recommendations.
- **FR-012**: System MUST NOT use pseudo-random numbers (`np.random`), fixed seeds, sine/cosine artificial math, or synthetic fallbacks anywhere within the production satellite discovery and NDVI pipeline.

### Key Entities

- **Satellite Catalog Query**: Represents the spatial (bounding box) and temporal (date range) search request submitted to STAC endpoints, along with catalog preference order.
- **Scene Metadata**: Represents the metadata payload of a returned satellite scene, including scene identifier, capture timestamp, cloud cover percentage, and COG band asset URL references.
- **Band Asset Request**: Represents the retrieval request for specific spectral band pixel data (B04 Red, B08 NIR) corresponding to the target field geometry.
- **Canopy Health Report**: Represents the structured evaluation containing computed NDVI spatial distributions, crop stress classification percentages, actual capture date, cloud cover metadata, or explicit fail-closed status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given a valid farm location with clear Sentinel-2 coverage, 100% of generated canopy health reports reflect actual band reflectance calculations, true capture timestamps, and real cloud cover metrics.
- **SC-002**: When zero valid clear scenes exist for a search window, 100% of responses execute the fail-closed protocol without generating heatmap image files or synthetic approximations.
- **SC-003**: Executing scene discovery and NDVI calculation with distinct geographic coordinates or date ranges produces distinct, non-identical reflectance statistics in automated verification tests.
- **SC-004**: Simulated total failure or timeout of the primary STAC catalog results in 100% automatic retry and query execution against the secondary STAC catalog.

## Assumptions

- Target farm parcels have valid spatial polygon geometries convertible to geographic bounding boxes.
- Public, keyless STAC catalog services (Element84 Earth Search and Copernicus Data Space) remain accessible via standardized HTTP REST interfaces without requiring paid API tokens.
- Existing heatmap color rendering and percentage categorization routines remain mathematically valid when receiving real NDVI array inputs.
- Satellite data retrieval latency is managed via async execution or explicit timeout boundaries consistent with application responsiveness requirements.
