import pytest
from app.parcel_validation import calculate_shoelace_geodesic_area_ha, validate_parcel_polygon
from app.regex_parser import is_parcel_cancel_command


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


def test_polygon_validation_pins_too_close():
    # Pins less than 5m apart (~0.00001 deg lat is ~1.1m)
    pins = [
        {"lat": 30.427800, "lon": -9.598100},
        {"lat": 30.427801, "lon": -9.598100},  # ~1.1m apart
        {"lat": 30.425000, "lon": -9.595200},
        {"lat": 30.425100, "lon": -9.598300},
    ]
    is_valid, error, geojson = validate_parcel_polygon(pins)
    assert is_valid is False
    assert "too close together" in error.lower() or "<5m" in error.lower()


def test_polygon_validation_fewer_than_3_pins():
    pins = [
        {"lat": 30.4278, "lon": -9.5981},
        {"lat": 30.4280, "lon": -9.5950},
    ]
    is_valid, error, geojson = validate_parcel_polygon(pins)
    assert is_valid is False
    assert "at least 3 corner pins" in error.lower()


def test_parcel_restart_command_regex():
    """Verify multi-lingual restart and reset boundary command triggers (FR-010)."""
    assert is_parcel_cancel_command("restart boundary") is True
    assert is_parcel_cancel_command("restart") is True
    assert is_parcel_cancel_command("recommencer") is True
    assert is_parcel_cancel_command("réinitialiser") is True
    assert is_parcel_cancel_command(" بدايات جديدة ") is False  # trailing typo
    assert is_parcel_cancel_command("بداية جديدة") is True
    assert is_parcel_cancel_command("/cancel") is True
    assert is_parcel_cancel_command("random message") is False
