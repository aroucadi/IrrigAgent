from app.decision import evaluate_irrigation_recommendation


def test_heavy_rain_recommendation_20mm():
    weather = {"et0": 4.0, "precipitation_mm": 20.0, "temp_max_c": 22.0}
    action, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather, "fresh")
    assert action == "skip_rain"
    assert "SKIP irrigation" in msg


def test_heavy_rain_boundary_15mm_exact():
    """Verify >=15mm rainfall auto-skip rule boundary condition per FR-021."""
    weather_15mm = {"et0": 4.0, "precipitation_mm": 15.0, "temp_max_c": 22.0}
    action, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather_15mm, "fresh")
    assert action == "skip_rain"
    assert "SKIP irrigation" in msg

    weather_below_15mm = {"et0": 4.0, "precipitation_mm": 14.9, "temp_max_c": 22.0}
    action_below, _ = evaluate_irrigation_recommendation("tomatoes", 10.0, weather_below_15mm, "fresh")
    assert action_below != "skip_rain"


def test_high_et0_recommendation():
    weather = {"et0": 6.0, "precipitation_mm": 0.0, "temp_max_c": 32.0}
    action, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather, "fresh")
    assert action == "adjust_water"
    assert "Increase irrigation" in msg


def test_standard_recommendation():
    weather = {"et0": 4.0, "precipitation_mm": 2.0, "temp_max_c": 24.0}
    action, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather, "fresh")
    assert action == "approve_standard"
    assert "Maintain standard" in msg


def test_estimated_data_notice():
    weather = {"et0": 4.5, "precipitation_mm": 0.0, "temp_max_c": 25.0}
    _, msg = evaluate_irrigation_recommendation("tomatoes", 10.0, weather, "estimated")
    assert "Estimated ET₀ data used" in msg
