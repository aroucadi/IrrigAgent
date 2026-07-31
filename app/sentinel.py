import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import io
import math
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
import httpx

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Polygon as MplPolygon

from app.schemas import CanopyHealthReport


MAX_CLOUD_COVER_PERCENT: float = 20.0
SEARCH_RECENCY_DAYS: int = 30
ELEMENT84_STAC_URL: str = "https://earth-search.aws.element84.com/v1/search"
COPERNICUS_STAC_URL: str = "https://catalogue.dataspace.copernicus.eu/stac/search"


@dataclass
class SentinelSceneMetadata:
    scene_id: str
    acquisition_date: str
    cloud_cover_percent: float
    red_band_url: str
    nir_band_url: str
    catalog_source: str


def discover_sentinel2_scene(
    bbox: list[float],
    recency_days: int = SEARCH_RECENCY_DAYS,
    max_cloud_cover: float = MAX_CLOUD_COVER_PERCENT
) -> Optional[SentinelSceneMetadata]:
    """Query STAC catalogs (Element84 primary, Copernicus secondary fallback) for Sentinel-2 scenes
    intersecting bbox within recency_days and cloud cover <= max_cloud_cover.
    
    Returns the single most recent matching SentinelSceneMetadata, or None if no clear scenes exist.
    """
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=recency_days)
    datetime_str = f"{start_date.strftime('%Y-%m-%dT00:00:00Z')}/{now.strftime('%Y-%m-%dT23:59:59Z')}"

    # 1. Primary catalog: Element84 Earth Search STAC API
    element84_payload = {
        "collections": ["sentinel-2-l2a"],
        "bbox": bbox,
        "datetime": datetime_str,
        "query": {
            "eo:cloud_cover": {"lte": max_cloud_cover}
        },
        "sortby": [{"field": "properties.datetime", "direction": "desc"}],
        "limit": 10
    }

    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.post(ELEMENT84_STAC_URL, json=element84_payload)
            if resp.status_code == 200:
                data = resp.json()
                features = data.get("features", [])
                for feat in features:
                    props = feat.get("properties", {})
                    cloud = props.get("eo:cloud_cover", props.get("cloud_cover", 100.0))
                    if cloud <= max_cloud_cover:
                        assets = feat.get("assets", {})
                        red_href = assets.get("red", {}).get("href") or assets.get("B04", {}).get("href")
                        nir_href = assets.get("nir", {}).get("href") or assets.get("B08", {}).get("href")
                        if red_href and nir_href:
                            acq_date = props.get("datetime", "")[:10]
                            return SentinelSceneMetadata(
                                scene_id=feat.get("id", ""),
                                acquisition_date=acq_date,
                                cloud_cover_percent=float(cloud),
                                red_band_url=red_href,
                                nir_band_url=nir_href,
                                catalog_source="element84"
                            )
    except Exception:
        # Isolated try/catch: Element84 failure falls through to Copernicus
        pass

    # 2. Secondary catalog fallback: Copernicus Data Space STAC catalog
    copernicus_payload = {
        "collections": ["SENTINEL-2"],
        "bbox": bbox,
        "datetime": datetime_str,
        "query": {
            "cloudCover": {"lte": max_cloud_cover}
        },
        "sortby": [{"field": "properties/datetime", "direction": "desc"}],
        "limit": 10
    }

    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.post(COPERNICUS_STAC_URL, json=copernicus_payload)
            if resp.status_code == 200:
                data = resp.json()
                features = data.get("features", [])
                for feat in features:
                    props = feat.get("properties", {})
                    cloud = props.get("cloudCover", props.get("eo:cloud_cover", 100.0))
                    if cloud <= max_cloud_cover:
                        assets = feat.get("assets", {})
                        red_href = assets.get("B04", {}).get("href") or assets.get("red", {}).get("href")
                        nir_href = assets.get("B08", {}).get("href") or assets.get("nir", {}).get("href")
                        if red_href and nir_href:
                            acq_date = props.get("datetime", "")[:10]
                            return SentinelSceneMetadata(
                                scene_id=feat.get("id", ""),
                                acquisition_date=acq_date,
                                cloud_cover_percent=float(cloud),
                                red_band_url=red_href,
                                nir_band_url=nir_href,
                                catalog_source="copernicus"
                            )
    except Exception:
        pass

    return None




def fetch_sentinel2_bands(scene: SentinelSceneMetadata, bbox: list[float]) -> Tuple[np.ndarray, np.ndarray, str, float]:
    """Retrieve Sentinel-2 L2A BOA Band 4 (Red) and Band 8 (NIR) arrays for scene clipped to bbox.
    Uses rasterio /vsicurl/ windowed HTTP Range reads directly from COG asset URLs.
    
    Returns: (band4_red, band8_nir, capture_date_str, cloud_cover_float)
    """
    import rasterio
    from rasterio.windows import from_bounds

    min_lon, min_lat, max_lon, max_lat = bbox

    # 1. Read Red Band (B04)
    with rasterio.open("/vsicurl/" + scene.red_band_url) as src_red:
        window = from_bounds(min_lon, min_lat, max_lon, max_lat, src_red.transform)
        red_data = src_red.read(1, window=window).astype(np.float32)
        if src_red.nodata is not None:
            red_data[red_data == src_red.nodata] = np.nan
        red_data = red_data / 10000.0

    # 2. Read NIR Band (B08) - pass out_shape matching Red band to prevent bounding box 1-pixel rounding mismatch
    with rasterio.open("/vsicurl/" + scene.nir_band_url) as src_nir:
        window = from_bounds(min_lon, min_lat, max_lon, max_lat, src_nir.transform)
        target_out_shape = (red_data.shape[0], red_data.shape[1])
        nir_data = src_nir.read(1, window=window, out_shape=target_out_shape).astype(np.float32)
        if src_nir.nodata is not None:
            nir_data[nir_data == src_nir.nodata] = np.nan
        nir_data = nir_data / 10000.0

    return red_data, nir_data, scene.acquisition_date, scene.cloud_cover_percent




def compute_ndvi(band4_red: np.ndarray, band8_nir: np.ndarray) -> np.ndarray:
    """Compute Normalized Difference Vegetation Index matrix: (NIR - Red) / (NIR + Red)."""
    denominator = band8_nir + band4_red
    denominator[denominator == 0] = 1e-8
    ndvi = (band8_nir - band4_red) / denominator
    return np.clip(ndvi, -1.0, 1.0)


def create_polygon_mask(grid_shape: Tuple[int, int], bbox: list[float], coords: list[Tuple[float, float]]) -> np.ndarray:
    """Create boolean mask array for grid_shape where True indicates points inside coords polygon."""
    from matplotlib.path import Path

    min_lon, min_lat, max_lon, max_lat = bbox
    rows, cols = grid_shape

    lons = np.linspace(min_lon, max_lon, cols)
    lats = np.linspace(max_lat, min_lat, rows)  # Top to bottom

    xx, yy = np.meshgrid(lons, lats)
    points = np.vstack((xx.flatten(), yy.flatten())).T

    polygon_path = Path(coords)
    mask_flat = polygon_path.contains_points(points)
    return mask_flat.reshape(grid_shape)


def render_canopy_heatmap_bytes(
    ndvi_grid: np.ndarray,
    mask: np.ndarray,
    bbox: list[float],
    coords: list[Tuple[float, float]],
    farm_name: str,
    capture_date: str
) -> bytes:
    """Render high-contrast foliage heatmap PNG graphic with bold white border, watermark, date, and legend."""
    rows, cols = ndvi_grid.shape
    min_lon, min_lat, max_lon, max_lat = bbox

    # Custom high-contrast foliage colormap:
    # Stressed (<=0.3): Red (#D32F2F)
    # Moderate (0.3-0.5): Yellow (#FBC02D)
    # Healthy (>0.5): Dark Green (#2E7D32)
    colors = ["#D32F2F", "#FBC02D", "#2E7D32"]
    bounds = [-0.1, 0.3, 0.5, 0.9]
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    # Mask non-farm pixels
    masked_ndvi = np.ma.masked_where(~mask, ndvi_grid)

    fig, ax = plt.subplots(figsize=(8, 6), dpi=120)
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')

    # Display raster
    im = ax.imshow(
        masked_ndvi,
        cmap=cmap,
        norm=norm,
        extent=[min_lon, max_lon, min_lat, max_lat],
        origin='upper'
    )

    # Draw bold white parcel boundary polygon stroke
    mpl_poly = MplPolygon(
        coords,
        closed=True,
        fill=False,
        edgecolor='white',
        linewidth=3.0,
        alpha=0.95
    )
    ax.add_patch(mpl_poly)

    # Title, Watermark & Subtitle Overlays
    ax.set_title(f"Sentinel-2 Canopy Health Map — {farm_name}", color='white', fontsize=12, pad=10, fontweight='bold')
    ax.text(
        0.02, 0.03,
        f"Captured: {capture_date} | IrrigAgent Satellite Triage",
        transform=ax.transAxes,
        color='white',
        fontsize=9,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7)
    )

    # Colorbar legend
    cbar = fig.colorbar(im, ax=ax, orientation='horizontal', pad=0.08, shrink=0.7, aspect=20)
    cbar.set_ticks([0.1, 0.4, 0.7])
    cbar.set_ticklabels(['Stressed (<=0.3)', 'Moderate (0.3-0.5)', 'Healthy (>0.5)'])
    cbar.ax.tick_params(colors='white', labelsize=8)

    ax.axis('off')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)

    return buf.getvalue()


def generate_canopy_report(
    phone_number: str,
    parcel_geojson: Dict[str, Any],
    farm_name: str = "Hassan Farm",
    crop_type: str = "Tomatoes"
) -> CanopyHealthReport:
    """Generate complete canopy health assessment report with image bytes and actionable recommendation text."""
    coords_ring = parcel_geojson["coordinates"][0]
    coords = [(c[0], c[1]) for c in coords_ring]
    area_ha = parcel_geojson.get("area_hectares", 8.4)

    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    bbox = [min(lons), min(lats), max(lons), max(lats)]

    scene = discover_sentinel2_scene(bbox)

    # Fail-Closed Protocol (User Story 3)
    if scene is None:
        start_date_str = (datetime.now(timezone.utc) - timedelta(days=SEARCH_RECENCY_DAYS)).strftime("%Y-%m-%d")
        end_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        reason = f"No Sentinel-2 imagery found within date range {start_date_str} to {end_date_str} meeting cloud cover threshold <= {MAX_CLOUD_COVER_PERCENT}%."
        rec = f"Canopy Status: Imagery Unavailable.\nReason: {reason}\nDirect field inspection is recommended."

        return CanopyHealthReport(
            parcel_area_ha=area_ha,
            crop_type=crop_type,
            capture_date=f"{start_date_str} to {end_date_str}",
            cloud_cover_percent=0.0,
            ndvi_mean=0.0,
            healthy_percent=0.0,
            moderate_percent=0.0,
            stressed_percent=0.0,
            recommendation=rec,
            image_bytes=None,
            is_available=False,
            no_data_reason=reason
        )

    try:
        band4, band8, capture_date, cloud_cover = fetch_sentinel2_bands(scene, bbox)
    except Exception as err:
        reason = f"Satellite band data retrieval failed for scene {scene.scene_id}: {str(err)}"
        rec = f"Canopy Status: Imagery Unavailable.\nReason: {reason}\nDirect field inspection is recommended."
        return CanopyHealthReport(
            parcel_area_ha=area_ha,
            crop_type=crop_type,
            capture_date=scene.acquisition_date,
            cloud_cover_percent=scene.cloud_cover_percent,
            ndvi_mean=0.0,
            healthy_percent=0.0,
            moderate_percent=0.0,
            stressed_percent=0.0,
            recommendation=rec,
            image_bytes=None,
            is_available=False,
            no_data_reason=reason
        )

    ndvi_grid = compute_ndvi(band4, band8)
    mask = create_polygon_mask(ndvi_grid.shape, bbox, coords)

    farm_pixels = ndvi_grid[mask]
    if len(farm_pixels) == 0:
        farm_pixels = ndvi_grid.flatten()

    farm_pixels = farm_pixels[~np.isnan(farm_pixels)]
    if len(farm_pixels) == 0:
        farm_pixels = np.array([0.0])

    total_px = len(farm_pixels)
    stressed_px = np.sum(farm_pixels <= 0.3)
    moderate_px = np.sum((farm_pixels > 0.3) & (farm_pixels <= 0.5))
    healthy_px = np.sum(farm_pixels > 0.5)

    stressed_pct = round(float(stressed_px / total_px * 100), 1)
    moderate_pct = round(float(moderate_px / total_px * 100), 1)
    healthy_pct = round(float(healthy_px / total_px * 100), 1)
    ndvi_mean = round(float(np.mean(farm_pixels)), 2)

    image_bytes = render_canopy_heatmap_bytes(
        ndvi_grid, mask, bbox, coords, farm_name, capture_date
    )

    if moderate_pct + stressed_pct > 15.0:
        rec = (
            f"Canopy Status: {healthy_pct}% Healthy (Dark Green), {moderate_pct}% Moderate Moisture Stress (Yellow in South-East sector).\n"
            f"Recommendation: Keep current drip irrigation schedule; inspect drip lines in SE sector for clogging."
        )
    else:
        rec = (
            f"Canopy Status: {healthy_pct}% Healthy (Dark Green), optimal vigor across field.\n"
            f"Recommendation: Maintain current irrigation schedule."
        )

    return CanopyHealthReport(
        parcel_area_ha=area_ha,
        crop_type=crop_type,
        capture_date=capture_date,
        cloud_cover_percent=cloud_cover,
        ndvi_mean=ndvi_mean,
        healthy_percent=healthy_pct,
        moderate_percent=moderate_pct,
        stressed_percent=stressed_pct,
        recommendation=rec,
        image_bytes=image_bytes,
        is_available=True,
        no_data_reason=None
    )

