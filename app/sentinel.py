import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import io
import math
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Polygon as MplPolygon

from app.schemas import CanopyHealthReport


def fetch_sentinel2_bands(bbox: list[float]) -> Tuple[np.ndarray, np.ndarray, str, float]:
    """Retrieve or generate synthetic Sentinel-2 L2A BOA Band 4 (Red) and Band 8 (NIR) arrays.
    
    bbox: [min_lon, min_lat, max_lon, max_lat]
    """
    grid_size = 100
    np.random.seed(42)  # Deterministic seed for reproducible testing

    # Generate synthetic Red (0.05 - 0.25) and NIR (0.20 - 0.65) reflectance matrices
    x = np.linspace(-2, 2, grid_size)
    y = np.linspace(-2, 2, grid_size)
    xx, yy = np.meshgrid(x, y)

    # Simulated canopy vigor spatial distribution with a stressed SE sector
    vigor_pattern = 0.5 + 0.3 * np.sin(xx) * np.cos(yy) - 0.2 * (xx > 0.5) * (yy < -0.5)
    vigor_pattern = np.clip(vigor_pattern, 0.1, 0.9)

    band4_red = 0.25 - 0.20 * vigor_pattern + np.random.uniform(0.0, 0.02, (grid_size, grid_size))
    band8_nir = 0.15 + 0.50 * vigor_pattern + np.random.uniform(0.0, 0.03, (grid_size, grid_size))

    capture_date = "2026-07-26"
    cloud_cover = 2.4  # %

    return band4_red, band8_nir, capture_date, cloud_cover


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

    band4, band8, capture_date, cloud_cover = fetch_sentinel2_bands(bbox)
    ndvi_grid = compute_ndvi(band4, band8)
    mask = create_polygon_mask(ndvi_grid.shape, bbox, coords)

    farm_pixels = ndvi_grid[mask]
    if len(farm_pixels) == 0:
        farm_pixels = ndvi_grid.flatten()

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
        image_bytes=image_bytes
    )
