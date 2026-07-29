from datetime import date, datetime
from typing import Optional, Dict
from app.schemas import FAO56CropEntry, ETcCalculationResult

# FAO-56 Published Crop Coefficients & Stage Duration Guidelines
FAO56_CROP_CATALOG: Dict[str, FAO56CropEntry] = {
    "tomatoes": FAO56CropEntry(
        crop_type="tomatoes",
        display_name="Tomatoes (Fresh / Industrial)",
        kc_ini=0.60,
        kc_mid=1.15,
        kc_end=0.80,
        stage_lengths_days={"initial": 30, "dev": 40, "mid": 45, "late": 30},
        is_perennial=False,
    ),
    "citrus": FAO56CropEntry(
        crop_type="citrus",
        display_name="Citrus Orchard (Adult)",
        kc_ini=0.70,
        kc_mid=0.65,
        kc_end=0.70,
        stage_lengths_days={"initial": 60, "dev": 90, "mid": 120, "late": 95},
        is_perennial=True,
    ),
    "watermelon": FAO56CropEntry(
        crop_type="watermelon",
        display_name="Watermelon",
        kc_ini=0.40,
        kc_mid=1.00,
        kc_end=0.75,
        stage_lengths_days={"initial": 20, "dev": 30, "mid": 30, "late": 20},
        is_perennial=False,
    ),
    "olives": FAO56CropEntry(
        crop_type="olives",
        display_name="Olives (Adult Grove)",
        kc_ini=0.65,
        kc_mid=0.70,
        kc_end=0.65,
        stage_lengths_days={"initial": 60, "dev": 90, "mid": 120, "late": 95},
        is_perennial=True,
    ),
    "potatoes": FAO56CropEntry(
        crop_type="potatoes",
        display_name="Potatoes",
        kc_ini=0.50,
        kc_mid=1.15,
        kc_end=0.75,
        stage_lengths_days={"initial": 25, "dev": 30, "mid": 45, "late": 30},
        is_perennial=False,
    ),
}

FALLBACK_NOTICE_TEXT = (
    "⚠️ Notice: Planting date unrecorded. Using baseline grass ET₀ (Kc=1.00). "
    "Update your planting date to get crop-specific precision."
)


def get_crop_entry(crop_type: str) -> Optional[FAO56CropEntry]:
    """Retrieve FAO-56 crop parameters by canonical key (case-insensitive)."""
    if not crop_type:
        return None
    return FAO56CropCatalog_lookup(crop_type.strip().lower())


def FAO56CropCatalog_lookup(key: str) -> Optional[FAO56CropEntry]:
    """Case-insensitive lookup in FAO-56 catalog."""
    for catalog_key, entry in FAO56_CROP_CATALOG.items():
        if catalog_key == key or entry.display_name.lower() == key:
            return entry
    return None


def calculate_crop_etc(
    crop_type: str,
    et0_mm: float,
    planting_date_str: Optional[str] = None,
    calculation_date: Optional[date] = None,
    is_mature_orchard: bool = False
) -> ETcCalculationResult:
    """Calculate crop-specific evapotranspiration (ETc = ET0 * Kc) based on growth stage."""
    calc_date = calculation_date or date.today()
    crop_entry = get_crop_entry(crop_type)

    # Fallback Case 1: Unrecognized crop type
    if not crop_entry:
        return ETcCalculationResult(
            et0_mm=round(et0_mm, 2),
            kc_applied=1.00,
            etc_mm=round(et0_mm * 1.00, 2),
            growth_stage="unknown",
            days_since_planting=None,
            notice=FALLBACK_NOTICE_TEXT,
        )

    # Perennial Orchards (Citrus / Olives)
    if crop_entry.is_perennial or is_mature_orchard:
        kc = crop_entry.kc_ini
        return ETcCalculationResult(
            et0_mm=round(et0_mm, 2),
            kc_applied=round(kc, 2),
            etc_mm=round(et0_mm * kc, 2),
            growth_stage="perennial",
            days_since_planting=None,
            notice=None,
        )

    # Fallback Case 2: Missing or unparseable planting date
    if not planting_date_str:
        return ETcCalculationResult(
            et0_mm=round(et0_mm, 2),
            kc_applied=1.00,
            etc_mm=round(et0_mm * 1.00, 2),
            growth_stage="unknown",
            days_since_planting=None,
            notice=FALLBACK_NOTICE_TEXT,
        )

    try:
        p_date = datetime.strptime(planting_date_str.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return ETcCalculationResult(
            et0_mm=round(et0_mm, 2),
            kc_applied=1.00,
            etc_mm=round(et0_mm * 1.00, 2),
            growth_stage="unknown",
            days_since_planting=None,
            notice=FALLBACK_NOTICE_TEXT,
        )

    days_elapsed = (calc_date - p_date).days

    if days_elapsed < 0:
        # Pre-planting date edge case
        return ETcCalculationResult(
            et0_mm=round(et0_mm, 2),
            kc_applied=crop_entry.kc_ini,
            etc_mm=round(et0_mm * crop_entry.kc_ini, 2),
            growth_stage="initial",
            days_since_planting=days_elapsed,
            notice=None,
        )

    stages = crop_entry.stage_lengths_days
    l_ini = stages.get("initial", 30)
    l_dev = stages.get("dev", 40)
    l_mid = stages.get("mid", 45)
    l_late = stages.get("late", 30)

    # 1. Initial Stage
    if days_elapsed <= l_ini:
        kc = crop_entry.kc_ini
        stage = "initial"
    # 2. Crop Development Stage (Linear interpolation Kc_ini -> Kc_mid)
    elif days_elapsed <= (l_ini + l_dev):
        stage = "development"
        dev_days = days_elapsed - l_ini
        kc = crop_entry.kc_ini + (dev_days / l_dev) * (crop_entry.kc_mid - crop_entry.kc_ini)
    # 3. Mid-Season Stage
    elif days_elapsed <= (l_ini + l_dev + l_mid):
        stage = "mid_season"
        kc = crop_entry.kc_mid
    # 4. Late-Season Stage (Linear interpolation Kc_mid -> Kc_end)
    elif days_elapsed <= (l_ini + l_dev + l_mid + l_late):
        stage = "late_season"
        late_days = days_elapsed - (l_ini + l_dev + l_mid)
        kc = crop_entry.kc_mid + (late_days / l_late) * (crop_entry.kc_end - crop_entry.kc_mid)
    # 5. Post-Harvest Bounds
    else:
        stage = "post_harvest"
        kc = crop_entry.kc_end

    etc_val = et0_mm * kc

    return ETcCalculationResult(
        et0_mm=round(et0_mm, 2),
        kc_applied=round(kc, 2),
        etc_mm=round(etc_val, 2),
        growth_stage=stage,
        days_since_planting=days_elapsed,
        notice=None,
    )
