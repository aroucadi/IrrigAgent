from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response, Query, Header, HTTPException
from typing import Optional

from app.config import VERIFY_TOKEN, JOB_SECRET_TOKEN
from app.whatsapp import send_text_message, extract_incoming_message, download_media
from app.weather import get_et0_forecast
from app.decision import evaluate_irrigation_recommendation
from app.regex_parser import parse_modification_text
from app.cropdoctor import perform_cropdoctor_triage
from app.firestore_client import (
    get_farm_profile,
    save_farm_profile,
    list_active_farm_profiles,
    save_recommendation,
    get_latest_recommendation_for_user,
    save_triage_request,
    detect_arabizi_or_arabic,
)

app = FastAPI(title="IrrigAgent AI", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "IrrigAgent AI", "version": "1.0.0"}


@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """Meta webhook verification handshake endpoint."""
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    return Response(content="Forbidden", status_code=403)


@app.post("/webhook")
async def receive_webhook(request: Request):
    """Receive incoming WhatsApp messages (text replies and leaf photo images)."""
    payload = await request.json()
    incoming = extract_incoming_message(payload)
    if not incoming:
        return {"status": "ignored"}

    sender = incoming["from"]
    msg_type = incoming["type"]
    text = (incoming.get("text") or "").strip()
    image_id = incoming.get("image_id")

    # Fetch or initialize Farm Profile
    profile = await get_farm_profile(sender)
    is_new_user = False
    if not profile:
        is_new_user = True
        profile = {
            "phone_number": sender,
            "location": {"latitude": 30.4278, "longitude": -9.5981},
            "crop_type": "tomatoes",
            "acreage_hectares": 10.0,
            "preferred_language": "french",
        }
        await save_farm_profile(profile)

    # Rule-based Arabizi / Arabic script language auto-detection heuristic
    if text and detect_arabizi_or_arabic(text):
        if profile.get("preferred_language") != "darija":
            profile["preferred_language"] = "darija"
            await save_farm_profile(profile)

    # First interaction for a new user: Dual-language initial greeting
    if is_new_user and text and text not in ["1", "2", "3"]:
        greeting_msg = (
            "🌾 *Bienvenue sur IrrigAgent AI / Marhaba bik fe IrrigAgent AI!*\n\n"
            "Je suis votre assistant d'irrigation et de santé des cultures.\n"
            "Ana l'assistant dyalk l'irrigation wa sehhat l'mahsoul.\n\n"
            "Chaque soir à 19:00, vous recevrez une recommandation d'arrosage."
        )
        await send_text_message(sender, greeting_msg)
        return {"status": "welcomed"}

    # Handle Leaf Photo Image Event (CropDoctor)
    if msg_type == "image" or image_id:
        try:
            image_bytes = await download_media(image_id or "mock_img_1")
            crop_type = profile.get("crop_type", "tomatoes")
            triage_result = await perform_cropdoctor_triage(image_bytes, crop_type)
            
            # Log triage request to Firestore
            triage_record = {
                "request_id": f"triage_{sender}_{int(datetime.now(timezone.utc).timestamp())}",
                "phone_number": sender,
                "image_id": image_id or "mock_img_1",
                "pathogen_identified": triage_result["pathogen_identified"],
                "confidence_score": triage_result["confidence_score"],
                "confidence_tier": triage_result["confidence_tier"],
                "onssa_product_pointer": triage_result["onssa_product_pointer"],
                "disclaimer_included": triage_result["disclaimer_included"],
                "response_text": triage_result["response_text"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            await save_triage_request(triage_record)
            
            # Send WhatsApp response to Hassan
            await send_text_message(sender, triage_result["response_text"])
            return {"status": "triage_completed"}
        except Exception as e:
            error_msg = (
                "🍃 *CropDoctor Advisory*\n"
                "Unable to process image. Please try resending a clear leaf photo.\n\n"
                "⚠️ This is a first-pass triage only. Always verify with ONSSA-authorized products."
            )
            await send_text_message(sender, error_msg)
            return {"status": "triage_error", "error": str(e)}

    # Handle Text One-Tap Replies (1 = Approve, 2 = Skip, 3 = Modify)
    latest_rec = await get_latest_recommendation_for_user(sender)
    
    if text == "1":
        reply_msg = "Approved. Irrigation adjustment applied for tomorrow."
        if latest_rec:
            latest_rec["status"] = "approved"
            latest_rec["user_response_raw"] = text
            latest_rec["responded_at"] = datetime.now(timezone.utc).isoformat()
            await save_recommendation(latest_rec)
        await send_text_message(sender, reply_msg)
        return {"status": "approved"}

    elif text == "2":
        reply_msg = "Understood, skipping tomorrow's adjustment."
        if latest_rec:
            latest_rec["status"] = "skipped"
            latest_rec["user_response_raw"] = text
            latest_rec["responded_at"] = datetime.now(timezone.utc).isoformat()
            await save_recommendation(latest_rec)
        await send_text_message(sender, reply_msg)
        return {"status": "skipped"}

    elif text.startswith("3"):
        custom_input = text[1:].strip() if len(text) > 1 else ""
        if not custom_input:
            prompt_msg = "Reply with your preferred adjustment (e.g. '+10 min at 05:00')."
            await send_text_message(sender, prompt_msg)
            return {"status": "modification_prompted"}

        parsed_payload, ack_msg = parse_modification_text(custom_input)
        if latest_rec:
            latest_rec["status"] = "modified"
            latest_rec["user_response_raw"] = text
            latest_rec["parsed_modification"] = parsed_payload
            latest_rec["responded_at"] = datetime.now(timezone.utc).isoformat()
            await save_recommendation(latest_rec)
        await send_text_message(sender, ack_msg)
        return {"status": "modified"}

    else:
        # Default prompt for unrecognized text
        fallback_msg = (
            "🌾 *IrrigAgent AI*\n"
            "Please reply with:\n"
            "1 = Approve\n"
            "2 = Skip\n"
            "3 = Modify (e.g. '+10 min at 05:00')"
        )
        await send_text_message(sender, fallback_msg)
        return {"status": "prompt_sent"}


@app.post("/jobs/daily-recommendations")
async def trigger_daily_recommendations(authorization: Optional[str] = Header(None)):
    """18:45 GMT+1 Batch recommendation execution job."""
    if authorization != f"Bearer {JOB_SECRET_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized job execution token")

    profiles = await list_active_farm_profiles()
    dispatched_count = 0
    failed_count = 0
    quality_summary = {"fresh": 0, "estimated": 0}

    for profile in profiles:
        phone = profile["phone_number"]
        loc = profile.get("location", {"latitude": 30.4278, "longitude": -9.5981})
        crop = profile.get("crop_type", "tomatoes")
        acreage = profile.get("acreage_hectares", 10.0)

        # 1. Fetch weather with 3 short-backoff retries
        weather_data, data_quality = await get_et0_forecast(loc["latitude"], loc["longitude"])
        quality_summary[data_quality] += 1

        # 2. Evaluate recommendation logic
        action, rec_msg = evaluate_irrigation_recommendation(crop, acreage, weather_data, data_quality)

        # 3. Store recommendation record
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        rec_id = f"rec_{phone}_{today_str}"
        rec_record = {
            "recommendation_id": rec_id,
            "phone_number": phone,
            "target_date": today_str,
            "forecast_weather": weather_data,
            "data_quality": data_quality,
            "recommended_action": action,
            "recommendation_text": rec_msg,
            "status": "pending",
            "user_response_raw": None,
            "parsed_modification": None,
            "dispatched_at": datetime.now(timezone.utc).isoformat(),
            "responded_at": None,
        }
        await save_recommendation(rec_record)

        # 4. Dispatch WhatsApp message
        try:
            await send_text_message(phone, rec_msg)
            dispatched_count += 1
        except Exception:
            failed_count += 1

    return {
        "status": "success",
        "dispatched_count": dispatched_count,
        "failed_count": failed_count,
        "data_quality_summary": quality_summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
