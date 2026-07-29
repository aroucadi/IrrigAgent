# Contract: ETc Calculation Engine API

**Feature**: `006-crop-etc-calculation`
**Date**: 2026-07-29

## Function Contract

### `calculate_crop_etc`

Pure calculation function in `app/fao56.py`.

```python
def calculate_crop_etc(
    crop_type: str,
    et0_mm: float,
    planting_date_str: Optional[str] = None,
    calculation_date: Optional[date] = None
) -> ETcCalculationResult
```

#### Input Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `crop_type` | `str` | Yes | Canonical crop key (e.g., `"tomatoes"`, `"citrus"`, `"watermelon"`, `"olives"`, `"potatoes"`). Case-insensitive. |
| `et0_mm` | `float` | Yes | Pulled reference evapotranspiration in mm/day from Open-Meteo. |
| `planting_date_str` | `Optional[str]` | No | ISO format date string (`"YYYY-MM-DD"`). If `None` or invalid format, fallback is triggered. |
| `calculation_date` | `Optional[date]` | No | Target calculation date (defaults to `date.today()`). |

#### Return Value

`ETcCalculationResult`:
- `et0_mm`: float
- `kc_applied`: float (rounded to 2 decimal places)
- `etc_mm`: float (rounded to 2 decimal places)
- `growth_stage`: str (`"initial"`, `"development"`, `"mid_season"`, `"late_season"`, `"post_harvest"`, `"unknown"`)
- `days_since_planting`: Optional[int]
- `notice`: Optional[str]

---

### `evaluate_irrigation_recommendation` Update Contract

Modified signature in `app/decision.py`:

```python
def evaluate_irrigation_recommendation(
    crop_type: str,
    acreage: float,
    weather_data: Dict[str, Any],
    planting_date_str: Optional[str] = None,
    data_quality: str = "fresh"
) -> Tuple[str, str]
```

#### Behavior & Output Message Example

When ETc is calculated (e.g. `ET0 = 5.0`, `Kc = 1.15` $\rightarrow$ `ETc = 5.75 mm`):

```text
🌾 *IrrigAgent Advisory for Tomorrow*
High crop water demand expected (5.75 mm ETc [ET₀ 5.0 × Kc 1.15]). Recommendation: Increase irrigation duration by +15 min tomorrow morning.

Reply to confirm:
1 = Approve
2 = Skip
3 = Modify (e.g. '+10 min at 05:00')
```
