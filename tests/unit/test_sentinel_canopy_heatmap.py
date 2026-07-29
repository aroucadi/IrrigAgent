import numpy as np
import pytest
from app.sentinel import compute_ndvi, fetch_sentinel2_bands, create_polygon_mask, generate_canopy_report


def test_compute_ndvi_exact():
    # NIR=0.8, Red=0.2 -> (0.8 - 0.2) / (0.8 + 0.2) = 0.6 / 1.0 = 0.6
    band4_red = np.array([[0.2]])
    band8_nir = np.array([[0.8]])
    ndvi = compute_ndvi(band4_red, band8_nir)
    assert np.isclose(ndvi[0, 0], 0.6)


def test_compute_ndvi_clipped():
    band4_red = np.array([[0.0]])
    band8_nir = np.array([[0.9]])
    ndvi = compute_ndvi(band4_red, band8_nir)
    assert -1.0 <= ndvi[0, 0] <= 1.0


def test_sentinel2_bands_retrieval():
    bbox = [-9.5983, 30.4250, -9.5950, 30.4280]
    red, nir, date_str, cloud_cover = fetch_sentinel2_bands(bbox)
    assert red.shape == (100, 100)
    assert nir.shape == (100, 100)
    assert isinstance(date_str, str)
    assert 0.0 <= cloud_cover <= 20.0


def test_polygon_raster_mask():
    bbox = [-9.5983, 30.4250, -9.5950, 30.4280]
    coords = [
        (-9.5981, 30.4278),
        (-9.5950, 30.4280),
        (-9.5952, 30.4250),
        (-9.5983, 30.4251),
        (-9.5981, 30.4278),
    ]
    mask = create_polygon_mask((100, 100), bbox, coords)
    assert mask.shape == (100, 100)
    assert np.sum(mask) > 0  # At least some pixels inside polygon


def test_generate_canopy_report():
    parcel_geojson = {
        "type": "Polygon",
        "coordinates": [[
            [-9.5981, 30.4278],
            [-9.5950, 30.4280],
            [-9.5952, 30.4250],
            [-9.5983, 30.4251],
            [-9.5981, 30.4278]
        ]],
        "area_hectares": 8.4
    }
    report = generate_canopy_report("+212600000000", parcel_geojson, "Agadir Tomato Farm", "Tomatoes")
    assert report.parcel_area_ha == 8.4
    assert report.crop_type == "Tomatoes"
    assert report.image_bytes is not None
    assert len(report.image_bytes) > 0
    assert "Canopy Status" in report.recommendation
