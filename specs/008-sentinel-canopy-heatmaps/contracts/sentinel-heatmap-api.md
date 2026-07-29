# Contract: Sentinel-2 Canopy Heatmap Service API

Internal Python Service Interface for processing satellite imagery and generating canopy heatmaps.

## Service Signature (`app/sentinel.py`)

### 1. `process_canopy_heatmap(phone_number: str, parcel_geojson: dict) -> CanopyHealthReport`

#### Arguments:
- `phone_number` (str): Farmer's E.164 phone number.
- `parcel_geojson` (dict): Validated GeoJSON Polygon object containing field coordinates and area.

#### Returns:
`CanopyHealthReport`:
```python
class CanopyHealthReport(BaseModel):
    parcel_area_ha: float
    crop_type: str
    capture_date: str
    cloud_cover_percent: float
    ndvi_mean: float
    healthy_percent: float
    moderate_percent: float
    stressed_percent: float
    recommendation: str
    media_id: Optional[str] = None
    image_bytes: Optional[bytes] = None
```

#### Behavior:
1. Extract bounding box from `parcel_geojson`.
2. Query Sentinel-2 L2A BOA satellite catalog for lowest cloud cover scene ($\le 20\%$) within past 5 days.
3. Download Band 4 (Red, 10m) and Band 8 (NIR, 10m) raster matrices.
4. Calculate matrix $NDVI = (B08 - B04) / (B08 + B04)$.
5. Clip raster matrix strictly to `parcel_geojson` geometry using raster mask.
6. Count pixel distribution across NDVI bands:
   - Stressed ($\le 0.3$)
   - Moderate ($0.3 - 0.5$)
   - Healthy ($> 0.6$)
7. Render PNG map image with:
   - Customized high-contrast foliage color palette (Red `#D32F2F`, Yellow `#FBC02D`, Dark Green `#2E7D32`)
   - Bold white field boundary stroke
   - Farm name watermark + capture date
   - Color scale legend bar
8. Upload PNG bytes via `app/whatsapp.py` Meta Cloud API `upload_media()`.
9. Formulate actionable recommendation text caption based on dominant stress sector.
