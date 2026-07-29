from datetime import date, timedelta
from app.fao56 import calculate_crop_etc, get_crop_entry, FAO56_CROP_CATALOG, FALLBACK_NOTICE_TEXT


def test_fao56_catalog_entries():
    """Verify all required crops exist in FAO-56 catalog."""
    for crop in ["tomatoes", "citrus", "watermelon", "olives", "potatoes"]:
        entry = get_crop_entry(crop)
        assert entry is not None
        assert entry.kc_ini > 0
        assert entry.kc_mid > 0
        assert entry.kc_end > 0


def test_etc_calculation_tomatoes_initial_stage():
    """Verify ETc calculation during initial stage for tomatoes (Kc = 0.60)."""
    today = date(2026, 7, 29)
    # Planting date 15 days ago (Initial stage: 0..30 days)
    p_date = (today - timedelta(days=15)).strftime("%Y-%m-%d")
    result = calculate_crop_etc("tomatoes", et0_mm=5.0, planting_date_str=p_date, calculation_date=today)

    assert result.et0_mm == 5.0
    assert result.kc_applied == 0.60
    assert result.etc_mm == 3.00  # 5.0 * 0.60
    assert result.growth_stage == "initial"
    assert result.days_since_planting == 15
    assert result.notice is None


def test_etc_calculation_tomatoes_mid_season_stage():
    """Verify ETc calculation during mid-season stage for tomatoes (Kc = 1.15)."""
    today = date(2026, 7, 29)
    # Planting date 80 days ago (Initial: 30, Dev: 40 -> Mid: 71..115 days)
    p_date = (today - timedelta(days=80)).strftime("%Y-%m-%d")
    result = calculate_crop_etc("tomatoes", et0_mm=5.0, planting_date_str=p_date, calculation_date=today)

    assert result.et0_mm == 5.0
    assert result.kc_applied == 1.15
    assert result.etc_mm == 5.75  # 5.0 * 1.15
    assert result.growth_stage == "mid_season"
    assert result.days_since_planting == 80


def test_etc_calculation_development_interpolation():
    """Verify linear interpolation during development stage (Tomatoes: 30..70 days, Kc 0.60 -> 1.15)."""
    today = date(2026, 7, 29)
    # 50 days elapsed -> 20 days into 40-day dev stage -> midpoint Kc = 0.60 + 0.5 * (1.15 - 0.60) = 0.875 -> rounded to 0.88
    p_date = (today - timedelta(days=50)).strftime("%Y-%m-%d")
    result = calculate_crop_etc("tomatoes", et0_mm=5.0, planting_date_str=p_date, calculation_date=today)

    assert result.growth_stage == "development"
    assert result.kc_applied == 0.88
    assert result.etc_mm == round(5.0 * 0.875, 2)


def test_etc_calculation_late_season_interpolation():
    """Verify linear interpolation during late season stage for tomatoes."""
    today = date(2026, 7, 29)
    # 130 days elapsed -> Initial 30 + Dev 40 + Mid 45 = 115 days -> 15 days into 30-day late stage (midpoint)
    # Kc_mid 1.15 -> Kc_end 0.80 -> midpoint = 1.15 + 0.5 * (0.80 - 1.15) = 0.975 -> rounded 0.98
    p_date = (today - timedelta(days=130)).strftime("%Y-%m-%d")
    result = calculate_crop_etc("tomatoes", et0_mm=5.0, planting_date_str=p_date, calculation_date=today)

    assert result.growth_stage == "late_season"
    assert result.kc_applied == 0.97


def test_etc_calculation_post_harvest_bounds():
    """Verify post-harvest bounds hold Kc = Kc_end."""
    today = date(2026, 7, 29)
    # 200 days elapsed (Total cycle 145 days)
    p_date = (today - timedelta(days=200)).strftime("%Y-%m-%d")
    result = calculate_crop_etc("tomatoes", et0_mm=5.0, planting_date_str=p_date, calculation_date=today)

    assert result.growth_stage == "post_harvest"
    assert result.kc_applied == 0.80


def test_etc_calculation_perennial_citrus():
    """Verify adult perennial orchard uses Kc_ini / perennial baseline."""
    result = calculate_crop_etc("citrus", et0_mm=4.0)

    assert result.growth_stage == "perennial"
    assert result.kc_applied == 0.70
    assert result.etc_mm == 2.80  # 4.0 * 0.70
    assert result.notice is None


def test_etc_calculation_missing_planting_date_fallback():
    """Verify fallback to Kc = 1.00 and notice prompt when planting date is missing."""
    result = calculate_crop_etc("tomatoes", et0_mm=5.0, planting_date_str=None)

    assert result.growth_stage == "unknown"
    assert result.kc_applied == 1.00
    assert result.etc_mm == 5.00
    assert result.notice == FALLBACK_NOTICE_TEXT


def test_etc_calculation_unrecognized_crop_fallback():
    """Verify fallback to Kc = 1.00 when crop type is unrecognized."""
    result = calculate_crop_etc("exotic_fruit", et0_mm=4.5)

    assert result.growth_stage == "unknown"
    assert result.kc_applied == 1.00
    assert result.etc_mm == 4.50
    assert result.notice == FALLBACK_NOTICE_TEXT
