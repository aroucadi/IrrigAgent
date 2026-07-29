import pytest
from app.parcel_validation import calculate_shoelace_geodesic_area_ha, validate_parcel_polygon


def test_shoelace_area_calculation():
    # 4-corner polygon in Agadir region (approx 8.4 ha)
    coords = [
        (-9.5981, 30.4278),
        (-9.5950, 30.4280),
        (-9.5952, 30.4250),
        (-9.5983, 30.4251),
    ]
    area = calculate_shoelace_geodesic_area_ha(coords)
    assert 7.0 <= area <= 10.0
    assert isinstance(area, float)


def test_polygon_validation_valid():
    pins = [
        {"lat": 30.4278, "lon": -9.5981},
        {"lat": 30.4280, "lon": -9.5950},
        {"lat": 30.4250, "lon": -9.5952},
        {"lat": 30.4251, "lon": -9.5983},
    ]
    is_valid, error, geojson = validate_parcel_polygon(pins)
    assert is_valid is True
    assert error == ""
    assert geojson["type"] == "Polygon"
    assert len(geojson["coordinates"][0]) == 5  # Closed 4-corner ring
    assert 7.0 <= geojson["area_hectares"] <= 10.0


def test_polygon_validation_self_intersecting():
    # Figure-8 sequence causing self-crossing edges
    pins = [
        {"lat": 30.4278, "lon": -9.5981},
        {"lat": 30.4250, "lon": -9.5950},
        {"lat": 30.4280, "lon": -9.5952},
        {"lat": 30.4251, "lon": -9.5983},
    ]
    is_valid, error, geojson = validate_parcel_polygon(pins)
    assert is_valid is False
    assert "cross each other" in error.lower() or "self-intersecting" in error.lower()


def test_polygon_validation_too_small():
    # Tiny micro-plot (approx 0.001 ha)
    pins = [
        {"lat": 30.427800, "lon": -9.598100},
        {"lat": 30.427810, "lon": -9.598100},
        {"lat": 30.427810, "lon": -9.598110},
        {"lat": 30.427800, "lon": -9.598110},
    ]
    is_valid, error, geojson = validate_parcel_polygon(pins)
    assert is_valid is False
    assert "out of bounds" in error.lower()


def test_polygon_validation_too_large():
    # Huge macro-region (approx 1000 ha)
    pins = [
        {"lat": 30.4000, "lon": -9.6000},
        {"lat": 30.4000, "lon": -9.2000},
        {"lat": 30.1000, "lon": -9.2000},
        {"lat": 30.1000, "lon": -9.6000},
    ]
    is_valid, error, geojson = validate_parcel_polygon(pins)
    assert is_valid is False
    assert "out of bounds" in error.lower()


def test_polygon_validation_fewer_than_3_pins():
    pins = [
        {"lat": 30.4278, "lon": -9.5981},
        {"lat": 30.4280, "lon": -9.5950},
    ]
    is_valid, error, geojson = validate_parcel_polygon(pins)
    assert is_valid is False
    assert "at least 3 corner pins" in error.lower()
