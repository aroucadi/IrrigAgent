# Component Interface Contracts: Sentinel Satellite Discovery & NDVI

**Feature**: `011-real-sentinel-ndvi` | **Date**: 2026-07-30

## 1. External STAC API Request / Response Contracts

### Primary STAC API: Element84 Earth Search
- **Endpoint**: `POST https://earth-search.aws.element84.com/v1/search`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "collections": ["sentinel-2-l2a"],
    "bbox": [-9.5983, 30.4250, -9.5950, 30.4280],
    "datetime": "2026-06-30T00:00:00Z/2026-07-30T23:59:59Z",
    "query": {
      "eo:cloud_cover": { "lte": 20 }
    },
    "sortby": [
      { "field": "properties.datetime", "direction": "desc" }
    ],
    "limit": 5
  }
  ```
- **Expected Response (200 OK)**:
  ```json
  {
    "type": "FeatureCollection",
    "features": [
      {
        "id": "S2A_30RZT_20260728_0_L2A",
        "properties": {
          "datetime": "2026-07-28T10:40:21Z",
          "eo:cloud_cover": 4.15
        },
        "assets": {
          "red": { "href": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/30/R/ZT/2026/7/S2A_30RZT_20260728_0_L2A/B04.tif" },
          "nir": { "href": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/30/R/ZT/2026/7/S2A_30RZT_20260728_0_L2A/B08.tif" }
        }
      }
    ]
  }
  ```

---

### Secondary STAC API: Copernicus Data Space Catalog
- **Endpoint**: `POST https://catalogue.dataspace.copernicus.eu/stac/search`
- **Headers**: `Content-Type: application/json`
- **Request Body**: (Identical STAC search geometry payload)

---

## 2. Internal Python Module API Contracts (`app/sentinel.py`)

### `discover_sentinel2_scene(bbox: list[float], recency_days: int = 30, max_cloud_cover: float = 20.0) -> Optional[SentinelSceneMetadata]`
Query STAC catalogs (Element84 primary, Copernicus fallback). Return most recent scene meeting criteria, or `None` if no clear scenes exist.

### `fetch_sentinel2_bands(scene: SentinelSceneMetadata, bbox: list[float]) -> Tuple[np.ndarray, np.ndarray, str, float]`
Retrieve B04 (Red) and B08 (NIR) band pixel arrays for `bbox` from `scene` asset URLs via windowed HTTP Range reads. Return `(red_array, nir_array, capture_date_str, cloud_cover_float)`.

### `generate_canopy_report(phone_number: str, parcel_geojson: Dict[str, Any], farm_name: str = "Hassan Farm", crop_type: str = "Tomatoes") -> CanopyHealthReport`
Orchestrate scene discovery, band retrieval, NDVI polygon masking, and report generation. Returns `CanopyHealthReport` with real capture parameters or fail-closed state (`is_available=False`).
