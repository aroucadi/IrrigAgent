import numpy as np
import pytest
from unittest.mock import patch, MagicMock
import httpx

from app.sentinel import (
    compute_ndvi,
    fetch_sentinel2_bands,
    create_polygon_mask,
    generate_canopy_report,
    discover_sentinel2_scene,
    SentinelSceneMetadata,
    MAX_CLOUD_COVER_PERCENT,
)


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
    assert np.sum(mask) > 0


def test_real_sentinel_discovery_element84_success():
    bbox = [-9.5983, 30.4250, -9.5950, 30.4280]
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "type": "FeatureCollection",
        "features": [
            {
                "id": "S2A_30RZT_20260728_0_L2A",
                "properties": {
                    "datetime": "2026-07-28T10:40:21Z",
                    "eo:cloud_cover": 4.2
                },
                "assets": {
                    "red": {"href": "https://example.com/B04.tif"},
                    "nir": {"href": "https://example.com/B08.tif"}
                }
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_response):
        scene = discover_sentinel2_scene(bbox)
        assert scene is not None
        assert scene.scene_id == "S2A_30RZT_20260728_0_L2A"
        assert scene.acquisition_date == "2026-07-28"
        assert scene.cloud_cover_percent == 4.2
        assert scene.catalog_source == "element84"
        assert scene.red_band_url == "https://example.com/B04.tif"
        assert scene.nir_band_url == "https://example.com/B08.tif"


def test_real_sentinel_discovery_fallback_to_copernicus():
    bbox = [-9.5983, 30.4250, -9.5950, 30.4280]

    # Element84 fails (returns HTTP 500 or Exception)
    def side_effect(url, **kwargs):
        if "element84" in url:
            raise httpx.ConnectError("Element84 unavailable")
        mock_copernicus = MagicMock()
        mock_copernicus.status_code = 200
        mock_copernicus.json.return_value = {
            "type": "FeatureCollection",
            "features": [
                {
                    "id": "S2B_COP_20260725_0_L2A",
                    "properties": {
                        "datetime": "2026-07-25T11:00:00Z",
                        "cloudCover": 12.0
                    },
                    "assets": {
                        "B04": {"href": "https://copernicus.example.com/B04.tif"},
                        "B08": {"href": "https://copernicus.example.com/B08.tif"}
                    }
                }
            ]
        }
        return mock_copernicus

    with patch("httpx.Client.post", side_effect=side_effect):
        scene = discover_sentinel2_scene(bbox)
        assert scene is not None
        assert scene.scene_id == "S2B_COP_20260725_0_L2A"
        assert scene.acquisition_date == "2026-07-25"
        assert scene.cloud_cover_percent == 12.0
        assert scene.catalog_source == "copernicus"


def test_sentinel2_bands_retrieval():
    bbox = [-9.5983, 30.4250, -9.5950, 30.4280]
    scene = SentinelSceneMetadata(
        scene_id="TEST_SCENE",
        acquisition_date="2026-07-28",
        cloud_cover_percent=3.5,
        red_band_url="https://example.com/B04.tif",
        nir_band_url="https://example.com/B08.tif",
        catalog_source="element84"
    )

    mock_src_red = MagicMock()
    mock_src_red.nodata = 0
    mock_src_red.transform = MagicMock()
    mock_src_red.read.return_value = (np.ones((100, 100)) * 1000).astype(np.uint16)
    mock_src_red.__enter__.return_value = mock_src_red

    mock_src_nir = MagicMock()
    mock_src_nir.nodata = 0
    mock_src_nir.transform = MagicMock()
    mock_src_nir.read.return_value = (np.ones((100, 100)) * 5000).astype(np.uint16)
    mock_src_nir.__enter__.return_value = mock_src_nir


    def rasterio_open_mock(path, **kwargs):
        if "B04" in path:
            return mock_src_red
        return mock_src_nir

    mock_rasterio = MagicMock()
    mock_rasterio.open.side_effect = rasterio_open_mock
    mock_windows = MagicMock()
    mock_windows.from_bounds.return_value = MagicMock()

    with patch.dict("sys.modules", {"rasterio": mock_rasterio, "rasterio.windows": mock_windows}):
        red, nir, date_str, cloud_cover = fetch_sentinel2_bands(scene, bbox)
        assert red.shape == (100, 100)
        assert nir.shape == (100, 100)
        assert date_str == "2026-07-28"
        assert cloud_cover == 3.5
        assert np.isclose(red[0, 0], 0.1)  # 1000 / 10000.0
        assert np.isclose(nir[0, 0], 0.5)  # 5000 / 10000.0


def test_real_sentinel_fail_closed_no_scenes():
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

    # STAC discovery returns None (0 scenes below 20% cloud cover)
    with patch("app.sentinel.discover_sentinel2_scene", return_value=None):
        report = generate_canopy_report("+212600000000", parcel_geojson, "Cloudy Farm", "Tomatoes")
        assert report.is_available is False
        assert report.image_bytes is None
        assert report.healthy_percent == 0.0
        assert report.moderate_percent == 0.0
        assert report.stressed_percent == 0.0
        assert report.no_data_reason is not None
        assert "No Sentinel-2 imagery found" in report.no_data_reason
        assert "Imagery Unavailable" in report.recommendation


def test_generate_canopy_report_success():
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

    mock_scene = SentinelSceneMetadata(
        scene_id="SCENE_CLEAR",
        acquisition_date="2026-07-28",
        cloud_cover_percent=1.8,
        red_band_url="https://example.com/B04.tif",
        nir_band_url="https://example.com/B08.tif",
        catalog_source="element84"
    )
    mock_red = np.full((100, 100), 0.1, dtype=np.float32)
    mock_nir = np.full((100, 100), 0.6, dtype=np.float32)

    with patch("app.sentinel.discover_sentinel2_scene", return_value=mock_scene), \
         patch("app.sentinel.fetch_sentinel2_bands", return_value=(mock_red, mock_nir, "2026-07-28", 1.8)):
        report = generate_canopy_report("+212600000000", parcel_geojson, "Agadir Tomato Farm", "Tomatoes")
        assert report.is_available is True
        assert report.parcel_area_ha == 8.4
        assert report.crop_type == "Tomatoes"
        assert report.capture_date == "2026-07-28"
        assert report.cloud_cover_percent == 1.8
        assert report.image_bytes is not None
        assert len(report.image_bytes) > 0
        assert report.healthy_percent == 100.0  # NDVI = (0.6 - 0.1)/(0.6 + 0.1) = 0.71 > 0.5


def test_real_sentinel_distinct_inputs_produce_distinct_results():
    """SC-003 Assertion: Two distinct band inputs produce two distinct non-synthetic output statistics."""
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

    mock_scene = SentinelSceneMetadata("S1", "2026-07-28", 0.5, "url4", "url8", "element84")

    # Dataset A: High vigor (Red=0.1, NIR=0.7 => NDVI=0.75)
    red_a = np.full((100, 100), 0.1, dtype=np.float32)
    nir_a = np.full((100, 100), 0.7, dtype=np.float32)

    # Dataset B: Stressed vigor (Red=0.2, NIR=0.3 => NDVI=0.20)
    red_b = np.full((100, 100), 0.2, dtype=np.float32)
    nir_b = np.full((100, 100), 0.3, dtype=np.float32)

    with patch("app.sentinel.discover_sentinel2_scene", return_value=mock_scene):
        with patch("app.sentinel.fetch_sentinel2_bands", return_value=(red_a, nir_a, "2026-07-28", 0.5)):
            report_a = generate_canopy_report("+212600000000", parcel_geojson, "Farm A")

        with patch("app.sentinel.fetch_sentinel2_bands", return_value=(red_b, nir_b, "2026-07-28", 0.5)):
            report_b = generate_canopy_report("+212600000000", parcel_geojson, "Farm B")

    assert report_a.ndvi_mean != report_b.ndvi_mean
    assert report_a.healthy_percent == 100.0
    assert report_b.stressed_percent == 100.0
