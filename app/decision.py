from typing import Dict, Any, Tuple, Optional
from app.fao56 import calculate_crop_etc


def evaluate_irrigation_recommendation(
    crop_type: str,
    acreage: float,
    weather_data: Dict[str, Any],
    planting_date: Optional[str] = None,
    is_mature_orchard: bool = False,
    data_quality: str = "fresh"
) -> Tuple[str, str]:
    """Evaluate weather metrics and crop-specific ETc to return (recommended_action, recommendation_text_message)."""
    et0 = weather_data.get("et0", 4.5)
    precip = weather_data.get("precipitation_mm", 0.0)

    etc_res = calculate_crop_etc(
        crop_type=crop_type,
        et0_mm=et0,
        planting_date_str=planting_date,
        is_mature_orchard=is_mature_orchard
    )
    etc = etc_res.etc_mm
    kc = etc_res.kc_applied

    if precip >= 15.0:
        action = "skip_rain"
        base_msg = f"Heavy rainfall expected ({precip} mm). Recommendation: SKIP irrigation tomorrow."
    elif etc >= 5.5:
        action = "adjust_water"
        base_msg = f"High crop water demand expected ({etc} mm ETc [ET₀ {et0} × Kc {kc}]). Recommendation: Increase irrigation duration by +15 min tomorrow morning."
    else:
        action = "approve_standard"
        base_msg = f"Standard weather forecast ({etc} mm ETc [ET₀ {et0} × Kc {kc}]). Recommendation: Maintain standard irrigation schedule tomorrow."

    # Build prompt options for Hassan
    msg_lines = [
        "🌾 *IrrigAgent Advisory for Tomorrow*",
        base_msg,
        "",
        "Reply to confirm:",
        "1 = Approve",
        "2 = Skip",
        "3 = Modify (e.g. '+10 min at 05:00')"
    ]

    if etc_res.notice:
        msg_lines.append("")
        msg_lines.append(etc_res.notice)

    if data_quality == "estimated":
        msg_lines.append("")
        msg_lines.append("⚠️ *Notice*: Estimated ET₀ data used due to weather service delay.")

    return action, "\n".join(msg_lines)
