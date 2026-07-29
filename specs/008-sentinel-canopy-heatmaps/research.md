# Research: Sentinel-2 Canopy Heatmaps & Multi-Pin WhatsApp Interaction

## Technical Research & Decisions

### 1. WhatsApp Location Pin State Machine
- **Decision**: Store active pin collection state in Firestore under `farm_sessions/{phone_number}` with fields: `state: "COLLECTING_PINS"`, `pins: [{"lat": float, "lon": float}, ...]`, `started_at`, `updated_at`.
- **Rationale**: Firestore fits the existing IrrigAgent architecture, allowing stateful multi-turn interactions over stateless WhatsApp webhooks without external cache infrastructure (Redis).
- **Alternatives Considered**: In-memory Python dict (lost on Cloud Run auto-scaling/restarts), Redis (violates minimalist GCP Cloud Run + Firestore constraint).

### 2. Polygon Geometry Validation & Area Calculation
- **Decision**: Use Python `shapely` library (`Polygon`, `is_valid`, `is_simple`) for self-intersection check and Shoelace / Geodesic area computation (using PyPROJ or Shapely `geod.geometry_area_perimeter` for accurate WGS84 hectare calculation).
- **Rationale**: `shapely` is the standard, well-tested Python geospatial library. Converting lat/lon WGS84 coordinates to EPSG:3857 or utilizing PyPROJ `Geod(ellps="WGS84")` ensures Shoelace area calculation is exact in hectares without projection distortion errors.
- **Alternatives Considered**: Raw custom Python Shoelace math (error-prone for geodesic planar distortion), GDAL (heavy C-library dependency).

### 3. Sentinel-2 Satellite Imagery Provider & Retrieval
- **Decision**: Integrate Copernicus Data Space Ecosystem (CDSE) STAC / OData API or Sentinel Hub API with a fallback to OpenEO / Sentinel-2 L2A BOA (Bottom-of-Atmosphere) Cloud-Optimized GeoTIFFs (COGs).
- **Rationale**: Copernicus Data Space Ecosystem provides free open access to Sentinel-2 L2A 10m resolution bands (B04 Red, B08 NIR) with cloud mask assets (SCL / QA60). Filtering by bounding box and cloud cover percentage ($\le 20\%$) over the past 5 days ensures optimal scene selection.
- **Alternatives Considered**: Google Earth Engine (requires GEE service account credentials), AWS Open Data Sentinel-2 S3 bucket (requires manual index querying).

### 4. NDVI Raster Processing & Color Heatmap Rendering
- **Decision**: Use `numpy` for array band math ($NDVI = \frac{B08 - B04}{B08 + B04}$), `rasterio` / `PIL` / `matplotlib` for raster masking (clipping strictly to parcel polygon using `rasterio.mask.mask`), and custom colormap mapping:
  - Stressed ($\le 0.3$): High-contrast Red (`#D32F2F`)
  - Moderate ($0.3 - 0.5$): High-contrast Yellow (`#FBC02D`)
  - Healthy Canopy ($> 0.6$): High-contrast Dark Green (`#2E7D32`)
- **Rationale**: Matplotlib/PIL combined with Rasterio enables seamless overlaying of bold white polygon boundary line, farm watermark, capture date, and color legend bar into a high-resolution PNG image.
- **Alternatives Considered**: Serverless Mapbox/Leaflet headless browser screenshot (heavy, requires browser automation), pure PIL (lacks built-in raster matrix manipulation).

### 5. WhatsApp Media Dispatch
- **Decision**: Leverage existing `app/whatsapp.py` infrastructure, extending it with `upload_whatsapp_media(image_bytes, mime_type="image/png")` to hit Meta Cloud API `POST /{phone_number_id}/media`, then sending an image message `send_whatsapp_image(to, media_id, caption)`.
- **Rationale**: Reuses ratified WhatsApp Cloud API integration patterns in alignment with project technical constraints.
- **Alternatives Considered**: Hosting PNG on public GCS bucket and sending image URL (Meta Cloud API media upload is more reliable and direct for sandbox tier).
