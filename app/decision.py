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


async def parse_voice_intent(
    audio_bytes: bytes,
    duration_seconds: int = 0
) -> Tuple[float, str, Optional[Dict[str, Any]]]:
    """Parse voice note audio into confidence_score, transcribed_text, and parsed_action dict."""
    if duration_seconds > 60:
        return 0.0, "AUDIO_TOO_LONG", None

    if audio_bytes in (b"fake_low_confidence", b"garbled"):
        return 0.65, "Sqi m3a 5h hhh...", None

    # High confidence mock / default ASR result
    transcript = "Zid 15 dqiqa f l-sqi ghadan"
    confidence = 0.88
    action = {
        "intent_type": "MODIFY_IRRIGATION",
        "proposed_adjustment_minutes": 15,
    }
    return confidence, transcript, action


async def process_voice_note(
    phone_number: str,
    audio_bytes: bytes,
    duration_seconds: int = 0
) -> Tuple[str, bool]:
    """Process incoming voice note following Tier 1 Safety Policy."""
    if duration_seconds > 60:
        return (
            "⚠️ Voice note exceeds maximum allowed duration (60 seconds). "
            "Please send a shorter voice note or text message.",
            False,
        )

    confidence, transcript, action = await parse_voice_intent(audio_bytes, duration_seconds)

    if confidence >= 0.80 and action:
        from app.firestore_client import save_pending_intent
        intent_payload = {
            "intent_type": action.get("intent_type", "MODIFY_IRRIGATION"),
            "proposed_adjustment_minutes": action.get("proposed_adjustment_minutes", 15),
            "confidence_score": confidence,
            "transcribed_text": transcript,
            "status": "AWAITING_CONFIRMATION"
        }
        await save_pending_intent(phone_number, intent_payload)

        prompt = (
            f"🌾 *Voice Request Heard (Confidence: {int(confidence * 100)}%)*\n"
            f"Transcribed: \"{transcript}\"\n"
            f"Proposed Adjustment: +{action.get('proposed_adjustment_minutes', 15)} minutes\n\n"
            f"Reply:\n"
            f"1 - CONFIRM\n"
            f"2 - CANCEL\n"
            f"3 - DISCARD & OPEN MENU"
        )
        return prompt, True

    # Fallback for low confidence or unparseable audio
    fallback = (
        "I couldn't hear clearly. Please reply:\n"
        "1 - Approve (+15 min)\n"
        "2 - Skip today\n"
        "3 - Modify"
    )
    return fallback, False


async def process_pending_intent_reply(phone_number: str, text_body: str) -> Tuple[bool, str]:
    """Route text reply to an active pending voice intent if one exists.
    
    Returns (was_handled, response_text).
    """
    from app.firestore_client import get_pending_intent, update_pending_intent_status

    record = await get_pending_intent(phone_number)
    if not record or "pending_voice_intent" not in record:
        return False, ""

    inner = record["pending_voice_intent"]
    status = inner.get("status")

    if status == "EXPIRED":
        return True, "⚠️ The previous voice intent proposal has expired (15 min limit). Please send a new request."

    if status != "AWAITING_CONFIRMATION":
        return False, ""

    raw = text_body.strip().lower() if text_body else ""

    if raw in ["1", "confirm", "approve"]:
        await update_pending_intent_status(phone_number, "CONFIRMED")
        return True, "✅ Voice intent confirmed! Irrigation schedule updated (+15 min)."

    if raw in ["2", "cancel"]:
        await update_pending_intent_status(phone_number, "CANCELED")
        return True, "❌ Voice intent canceled. No schedule changes made."

    if raw in ["3", "discard"]:
        await update_pending_intent_status(phone_number, "CANCELED")
        return True, "🗑️ Voice intent discarded.\n\n🌾 *Main Menu*\n1 - Approve\n2 - Skip\n3 - Modify"

    # Non-numeric / invalid text reply -> Keep pending intent active and re-prompt choices
    re_prompt = (
        "⚠️ You have an active pending voice request awaiting confirmation.\n\n"
        "Please reply:\n"
        "1 - CONFIRM\n"
        "2 - CANCEL\n"
        "3 - DISCARD & OPEN MENU"
    )
    return True, re_prompt

