from datetime import date, timedelta
from app.decision import evaluate_irrigation_recommendation


def test_heavy_rain_recommendation_20mm():
    weather = {"et0": 4.0, "precipitation_mm": 20.0, "temp_max_c": 22.0}
    action, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather, data_quality="fresh")
    assert action == "skip_rain"
    assert "SKIP irrigation" in msg


def test_heavy_rain_boundary_15mm_exact():
    """Verify >=15mm rainfall auto-skip rule boundary condition per FR-021."""
    weather_15mm = {"et0": 4.0, "precipitation_mm": 15.0, "temp_max_c": 22.0}
    action, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather_15mm, data_quality="fresh")
    assert action == "skip_rain"
    assert "SKIP irrigation" in msg

    weather_below_15mm = {"et0": 4.0, "precipitation_mm": 14.9, "temp_max_c": 22.0}
    action_below, _ = evaluate_irrigation_recommendation("tomatoes", 10.0, weather_below_15mm, data_quality="fresh")
    assert action_below != "skip_rain"


def test_high_etc_recommendation_with_planting_date():
    """Verify high ETc (mid-season tomatoes: ET0=5.0, Kc=1.15 -> ETc=5.75 >= 5.5) triggers adjust_water."""
    today = date.today()
    p_date = (today - timedelta(days=80)).strftime("%Y-%m-%d")
    weather = {"et0": 5.0, "precipitation_mm": 0.0, "temp_max_c": 32.0}
    action, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather, planting_date=p_date, data_quality="fresh")
    assert action == "adjust_water"
    assert "High crop water demand expected (5.75 mm ETc" in msg
    assert "Increase irrigation" in msg


def test_standard_recommendation_with_planting_date():
    """Verify initial stage tomatoes (ET0=4.0, Kc=0.60 -> ETc=2.40 < 5.5) triggers approve_standard."""
    today = date.today()
    p_date = (today - timedelta(days=15)).strftime("%Y-%m-%d")
    weather = {"et0": 4.0, "precipitation_mm": 2.0, "temp_max_c": 24.0}
    action, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather, planting_date=p_date, data_quality="fresh")
    assert action == "approve_standard"
    assert "Standard weather forecast (2.4 mm ETc" in msg or "Standard weather forecast (2.40 mm ETc" in msg or "2.4" in msg
    assert "Maintain standard" in msg


def test_missing_planting_date_fallback_notice_appended():
    """Verify missing planting date appends update notice to advisory message."""
    weather = {"et0": 4.5, "precipitation_mm": 0.0, "temp_max_c": 25.0}
    _, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather, planting_date=None, data_quality="fresh")
    assert "Planting date unrecorded" in msg


def test_estimated_data_notice():
    weather = {"et0": 4.5, "precipitation_mm": 0.0, "temp_max_c": 25.0}
    _, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather, data_quality="estimated")
    assert "Estimated ET₀ data used" in msg


def test_extreme_heatwave_warning_appended():
    """Verify max temp >= 40°C appends heatwave warning section."""
    weather = {"et0": 6.0, "precipitation_mm": 0.0, "temp_max_c": 41.5, "temp_min_c": 24.0}
    action, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather, preferred_language="fr")
    assert "Alerte Canicule" in msg
    assert "41.5" in msg
    assert "1 = Approve" in msg


def test_frost_warning_appended():
    """Verify min temp <= 2°C appends frost warning section."""
    weather = {"et0": 2.0, "precipitation_mm": 0.0, "temp_max_c": 14.0, "temp_min_c": 1.0}
    action, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather, preferred_language="fr")
    assert "Alerte Gel" in msg
    assert "1.0" in msg
    assert "1 = Approve" in msg


def test_no_extreme_weather_warning_within_normal_range():
    """Verify temperatures within normal bounds (2°C - 40°C) do not append extreme warnings."""
    weather = {"et0": 4.5, "precipitation_mm": 0.0, "temp_max_c": 32.0, "temp_min_c": 16.0}
    _, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather)
    assert "Alerte Canicule" not in msg
    assert "Alerte Gel" not in msg


def test_extreme_weather_and_rainfall_skip_coexistence():
    """Verify extreme weather warning and rainfall skip logic co-exist in the same message."""
    weather = {"et0": 3.0, "precipitation_mm": 18.0, "temp_max_c": 42.0, "temp_min_c": 20.0}
    action, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather, preferred_language="en")
    assert action == "skip_rain"
    assert "SKIP irrigation" in msg
    assert "Extreme Heat Warning" in msg
    assert "1 = Approve" in msg
