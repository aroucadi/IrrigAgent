from typing import Dict, Any, Tuple


def evaluate_irrigation_recommendation(
    crop_type: str,
    acreage: float,
    weather_data: Dict[str, Any],
    data_quality: str = "fresh"
) -> Tuple[str, str]:
    """Evaluate weather metrics and return (recommended_action, recommendation_text_message)."""
    et0 = weather_data.get("et0", 4.5)
    precip = weather_data.get("precipitation_mm", 0.0)

    if precip >= 15.0:
        action = "skip_rain"
        base_msg = f"Heavy rainfall expected ({precip} mm). Recommendation: SKIP irrigation tomorrow."
    elif et0 >= 5.5:
        action = "adjust_water"
        base_msg = f"High evapotranspiration expected ({et0} mm ET₀). Recommendation: Increase irrigation duration by +15 min tomorrow morning."
    else:
        action = "approve_standard"
        base_msg = f"Standard weather forecast ({et0} mm ET₀). Recommendation: Maintain standard irrigation schedule tomorrow."

    # Build prompt options for Hassan
    msg_lines = [
        f"🌾 *IrrigAgent Advisory for Tomorrow*",
        base_msg,
        "",
        "Reply to confirm:",
        "1 = Approve",
        "2 = Skip",
        "3 = Modify (e.g. '+10 min at 05:00')"
    ]

    if data_quality == "estimated":
        msg_lines.append("")
        msg_lines.append("⚠️ *Notice*: Estimated ET₀ data used due to weather service delay.")

    return action, "\n".join(msg_lines)
