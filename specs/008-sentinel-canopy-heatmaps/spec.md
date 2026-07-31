# Feature Specification: Sentinel-2 Canopy Heatmaps (Multi-Pin WhatsApp Interaction)

**Feature Branch**: `008-sentinel-canopy-heatmaps`

**Created**: 2026-07-29

**Status**: Implemented

**Input**: User description: "Feature 1: Section 3.3 — Sentinel-2 Canopy Heatmaps (Multi-Pin WhatsApp Interaction). Farmers define their field corners by sending standard WhatsApp Location Pins step-by-step. Validation rules: min 3 pins, simple polygon check (no self-intersection), Shoelace area calculation bounded 0.1-200 ha, persist GeoJSON polygon in Firestore. Fetch Copernicus Sentinel-2 L2A imagery (lowest cloud cover past 5 days), compute NDVI, map to high-contrast foliage color palette clipped to parcel boundary with overlays, and deliver via WhatsApp with status and actionable recommendation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Pin WhatsApp Parcel Boundary Collection (Priority: P1)

A farm manager wants to define the exact geographical boundary of their field directly within WhatsApp without leaving the messaging app or using complex Web GIS tools, so that satellite imagery can be accurately cropped to their farm.

**Why this priority**: Precise parcel boundaries are essential for cropping satellite raster imagery and masking surrounding non-farm background (roads, desert). A conversational WhatsApp pin collection state machine is the core UX enabler for farmers.

**Independent Test**: Can be fully tested by sending "/parcel" to the WhatsApp bot, following prompts to send location pins step by step, and confirming that each corner is acknowledged and recorded sequentially.

**Acceptance Scenarios**:

1. **Given** a registered farm manager on WhatsApp, **When** they send "/parcel" or "add boundary", **Then** the system transitions to pin collection state and prompts for PIN 1.
2. **Given** a active pin collection session, **When** the user sends a WhatsApp location attachment, **Then** the coordinate (latitude, longitude) is validated, stored, and the system prompts for the next pin corner with current count.
3. **Given** a pin collection session with at least 3 valid pins recorded, **When** the user sends "DONE" (or sends an additional location pin), **Then** pin collection ends and polygon validation begins.
4. **Given** an active pin collection session, **When** the user sends "/cancel" or invalid location data, **Then** the user receives clear feedback and can reset or correct the pin sequence.

---

### User Story 2 - Automated Parcel Polygon Validation & Persistence (Priority: P1)

A farm manager completing pin entry needs instant verification that their field boundary is topologically valid, within supported physical size limits, and accurately calculated in hectares.

**Why this priority**: Invalid geometry (e.g., self-crossing polygons, under 3 points) or impossible parcel sizes break satellite raster extraction algorithms and must be caught immediately before persistence.

**Independent Test**: Can be tested by providing valid and invalid pin sequences (e.g., figure-8 crossing polygon, 2 pins only, sub-0.1 ha micro-plot, >200 ha macro-region) and verifying rejection rules, area calculations, and static map preview confirmation.

**Acceptance Scenarios**:

1. **Given** 3 or more recorded corner pins, **When** polygon closure is triggered, **Then** the system verifies non-self-intersection, calculates total area via Shoelace formula, and confirms area falls between 0.1 ha and 200 ha.
2. **Given** a valid parcel polygon, **When** validation succeeds, **Then** the GeoJSON polygon representation and area in hectares are persisted to the farm profile in Firestore and a confirmation message with static map preview is sent.
3. **Given** a self-intersecting pin sequence or fewer than 3 pins, **When** polygon closure is attempted, **Then** the system rejects the polygon, explains the error, and allows the user to re-start or re-enter corner pins.
4. **Given** a polygon with calculated area outside bounds (<0.1 ha or >200 ha), **When** validation runs, **Then** the system rejects the submission with a clear boundary size warning.

---

### User Story 3 - Sentinel-2 Satellite Canopy Heatmap Pipeline (Priority: P2)

A farm manager requests a vegetation vigor assessment for their parcel, prompting the system to fetch recent Sentinel-2 satellite imagery, compute normalized vegetation indices, and render a field-cropped heatmap.

**Why this priority**: Translates raw satellite spectral bands into actionable canopy health visualizations specifically tailored to the registered field boundary.

**Independent Test**: Can be tested by requesting a canopy heatmap for a validated parcel, triggering Sentinel-2 spectral fetch, computing NDVI, applying color mapping, and verifying output image boundaries, scale bar, and watermarks.

**Acceptance Scenarios**:

1. **Given** a validated farm parcel polygon, **When** a canopy heatmap report is requested, **Then** the system queries Sentinel-2 Bottom-of-Atmosphere imagery, selecting the lowest cloud-cover scene from the past 5 days.
2. **Given** retrieved satellite spectral bands B04 (Red) and B08 (NIR), **When** processed, **Then** NDVI is computed across the raster grid and clipped strictly to the field parcel boundary.
3. **Given** calculated NDVI values, **When** rendered into a map graphic, **Then** values are colored according to foliage vigor tiers (Red for stressed $\le 0.3$, Yellow for moderate $0.3-0.5$, Dark Green for healthy $>0.6$), with bold polygon border stroke, farm watermark, date stamp, and color legend overlay.
4. **Given** persistent cloud cover (>20% obscured) across all available scenes in the past 5 days, **When** processing occurs, **Then** the user is notified of low quality due to weather and provided the latest available scene with a cloud advisory note.

---

### User Story 4 - WhatsApp Canopy Report Delivery & Actionable Triage (Priority: P2)

A farm manager receives the generated canopy heatmap image on WhatsApp alongside a clear Darija/French/English textual breakdown of vigor status percentages and targeted irrigation advice.

**Why this priority**: Raw maps alone are insufficient; farmers require readable percentage breakdowns (e.g. % healthy vs % stressed) and specific field sector inspection recommendations delivered straight to WhatsApp.

**Independent Test**: Can be tested by triggering report dispatch, verifying image media upload to Meta Cloud API, and checking text caption structure for canopy status metrics and actionable drip line advice.

**Acceptance Scenarios**:

1. **Given** a rendered canopy heatmap PNG image, **When** uploaded via Meta Cloud API media endpoint, **Then** the image is dispatched to the farmer's WhatsApp chat with a structured markdown caption.
2. **Given** the field NDVI pixel distribution, **When** generating the message text, **Then** the caption details field area, crop type, percentage healthy vs moderate stress, and sector location of anomalies.
3. **Given** identified stress sectors (e.g. 15% moderate moisture stress in SE sector), **When** forming recommendations, **Then** actionable inspection guidance (e.g. check drip lines for clogging) is included in the advisory.

---

### Edge Cases

- What happens when a farmer sends pins in a random self-intersecting criss-cross order? System detects non-simple polygon self-intersection and guides the farmer to send pins sequentially around the field perimeter.
- How does system handle cloud cover covering >20% of the field over the 5-day window? System alerts user of cloud obstruction, selects the clearest scene available, and includes a cloud-cover caveat in the report summary.
- What happens if the farmer stops mid-way through pin collection and resumes hours later? Session state persists for 1 hour; after 1 hour of inactivity, incomplete pin sessions auto-expire with a prompt to restart.
- How does the system handle location pins with low GPS accuracy (e.g., cellular tri-angulation error radius >30m)? System checks location metadata accuracy radius (if present in WhatsApp payload) and warns the farmer if GPS precision is degraded.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a WhatsApp state machine (`COLLECTING_PINS`) triggered by "/parcel" or "add boundary" command to collect field corner location pins step-by-step.
- **FR-002**: System MUST validate and record each received WhatsApp location attachment coordinate (latitude/longitude) and prompt for the next corner pin.
- **FR-003**: System MUST require a minimum of 3 location pins ($N \ge 3$) to attempt field boundary polygon closure upon receiving "DONE" or additional pin completion.
- **FR-004**: System MUST perform a simple polygon check to ensure boundary edges do not cross or self-intersect before accepting a parcel.
- **FR-005**: System MUST compute parcel surface area using the Shoelace formula and enforce strict bounds ($0.1 \text{ ha} \le \text{Area} \le 200 \text{ ha}$).
- **FR-006**: System MUST persist validated parcel boundaries as GeoJSON Polygon objects with calculated hectare area and ISO timestamp in the farm's Firestore record.
- **FR-007**: System MUST generate and send a confirmation message with static map preview displaying calculated field area upon successful parcel registration.
- **FR-008**: System MUST query Copernicus Sentinel-2 L2A Bottom-of-Atmosphere imagery to retrieve spectral bands B04 (Red) and B08 (NIR) for the farm bounding box, selecting the scene with lowest cloud cover over the previous 5 days.
- **FR-009**: System MUST compute NDVI grid values ($(B08 - B04) / (B08 + B04)$) and strictly mask/crop the raster to the registered farm parcel GeoJSON boundary.
- **FR-010**: System MUST render high-contrast foliage heatmaps mapping NDVI ranges $[-0.1, 0.9]$ to foliage colors (Red $\le 0.3$, Yellow $0.3-0.5$, Dark Green $> 0.6$) overlaid with a bold field boundary line, farm watermark, capture date, and color scale legend.
- **FR-011**: System MUST upload rendered heatmap graphics to Meta Cloud API media endpoints and deliver them directly to WhatsApp.
- **FR-012**: System MUST accompany heatmap images with structured text summaries detailing capture date, field area, crop type, canopy health percentages, and actionable sector-level irrigation recommendations.

### Key Entities *(include if feature involves data)*

- **Parcel Boundary**: Represents a field's geographic extent. Attributes include GeoJSON Polygon coordinates, calculated area in hectares, perimeter vertex count, and update timestamp.
- **Pin Collection Session**: Represents an active WhatsApp location gathering workflow. Attributes include sender phone number, session state (`IDLE`, `COLLECTING_PINS`, `VALIDATING`), array of stored coordinates, and creation/expiration timestamps.
- **Sentinel-2 Scene**: Metadata and raster data from satellite acquisition. Attributes include scene ID, sensing date, cloud cover percentage, bounding box, and band matrices (B04, B08).
- **Canopy Heatmap Report**: Generated analytical result for a parcel. Attributes include report timestamp, overall NDVI mean/variance, canopy vigor tier distribution (% healthy, % moderate, % stressed), rendered image media ID, and text recommendations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Farm managers can register a complete 4-corner field boundary via WhatsApp location pins in under 3 minutes.
- **SC-002**: 100% of invalid geometry submissions (self-intersecting, <3 corners, area <0.1 ha or >200 ha) are blocked at validation with user-understandable WhatsApp error messages.
- **SC-003**: Sentinel-2 canopy heatmap rendering and WhatsApp media delivery complete within 30 seconds of user request under normal API operation.
- **SC-004**: Field area calculation using the Shoelace formula matches standard geospatial benchmark measurements within a 2% margin of error.
- **SC-005**: Generated heatmap imagery strictly clips non-farm background (roads, neighboring fields, desert) to ensure 0% data leakage from outside the farm polygon.

## Assumptions

- Farmers possess mobile devices capable of sending standard native location attachments in WhatsApp.
- Copernicus Sentinel-2 L2A satellite data APIs are accessible and updated regularly (typical 5-day revisit time).
- Farm parcels are simple, contiguous polygons without inner holes or detached multi-polygons in v1.
- WhatsApp sandbox/Cloud API media upload endpoints support standard PNG image formats up to 5 MB.
- Field crops (e.g. tomatoes, citrus, olives) exhibit measurable NDVI variation between healthy foliage and moisture stress.
