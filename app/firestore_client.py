import os
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from app.config import GCP_PROJECT_ID

# In-memory store fallback for local testing & development when Firestore client is offline
_IN_MEMORY_FARM_PROFILES: Dict[str, Dict[str, Any]] = {
    "+212600000000": {
        "phone_number": "+212600000000",
        "location": {"latitude": 30.4278, "longitude": -9.5981}, # Agadir region
        "crop_type": "tomatoes",
        "acreage_hectares": 10.0,
        "preferred_language": "french",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
}
_IN_MEMORY_RECOMMENDATIONS: Dict[str, Dict[str, Any]] = {}
_IN_MEMORY_TRIAGE_REQUESTS: Dict[str, Dict[str, Any]] = {}
_IN_MEMORY_PIN_SESSIONS: Dict[str, Dict[str, Any]] = {}
_IN_MEMORY_FARM_PARCELS: Dict[str, Dict[str, Any]] = {}
_IN_MEMORY_PENDING_INTENTS: Dict[str, Dict[str, Any]] = {}
_IN_MEMORY_INBOUND_TIMESTAMPS: Dict[str, str] = {}

_db_client = None

def get_firestore_client():
    global _db_client
    if _db_client is None:
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ or "K_SERVICE" in os.environ:
            try:
                from google.cloud import firestore
                _db_client = firestore.AsyncClient(project=GCP_PROJECT_ID)
            except Exception:
                _db_client = False
        else:
            _db_client = False
    return _db_client


def detect_arabizi_or_arabic(text: str) -> bool:
    """Detects Arabic script or word-internal Arabizi digit substitutions ('3', '7', '9')."""
    if not text:
        return False
    # Arabic script Unicode range check
    if re.search(r'[\u0600-\u06FF]', text):
        return True
    # Strip clock-time tokens matching e.g. 07h00, 19h00, 06h30 (\b\d{1,2}h\d{2}\b)
    cleaned_text = re.sub(r'\b\d{1,2}h\d{2}\b', '', text, flags=re.IGNORECASE)
    # Word-internal Arabizi digit substitutions for Arabic phonemes (e.g. 'm3ak', '7na', '9dim')
    # Excludes standalone choice digits ('3'), time strings ('06h30'), and quantities ('30 min')
    if re.search(r'\b[a-zA-Z]+[379][a-zA-Z0-9]*\b|\b[a-zA-Z0-9]*[379][a-zA-Z]+\b', cleaned_text):
        return True
    return False



async def get_farm_profile(phone_number: str) -> Optional[Dict[str, Any]]:
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("farm_profiles").document(phone_number)
            doc = await doc_ref.get()
            if doc.exists:
                return doc.to_dict()
        except Exception:
            pass
    return _IN_MEMORY_FARM_PROFILES.get(phone_number)


async def save_farm_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    from app.schemas import FarmProfile
    validated = FarmProfile.model_validate(profile_data)
    clean_data = validated.model_dump()
    phone_number = clean_data["phone_number"]
    clean_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("farm_profiles").document(phone_number)
            await doc_ref.set(clean_data, merge=True)
        except Exception:
            pass
    
    if phone_number in _IN_MEMORY_FARM_PROFILES:
        _IN_MEMORY_FARM_PROFILES[phone_number].update(clean_data)
    else:
        clean_data["created_at"] = datetime.now(timezone.utc).isoformat()
        _IN_MEMORY_FARM_PROFILES[phone_number] = clean_data
    return _IN_MEMORY_FARM_PROFILES[phone_number]



async def list_active_farm_profiles() -> List[Dict[str, Any]]:
    client = get_firestore_client()
    if client:
        try:
            docs = client.collection("farm_profiles").stream()
            profiles = []
            async for doc in docs:
                profiles.append(doc.to_dict())
            if profiles:
                return profiles
        except Exception:
            pass
    return list(_IN_MEMORY_FARM_PROFILES.values())


async def save_recommendation(rec_data: Dict[str, Any]) -> Dict[str, Any]:
    rec_id = rec_data["recommendation_id"]
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("irrigation_recommendations").document(rec_id)
            await doc_ref.set(rec_data, merge=True)
        except Exception:
            pass
    _IN_MEMORY_RECOMMENDATIONS[rec_id] = rec_data
    return rec_data


async def get_recommendation(rec_id: str) -> Optional[Dict[str, Any]]:
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("irrigation_recommendations").document(rec_id)
            doc = await doc_ref.get()
            if doc.exists:
                return doc.to_dict()
        except Exception:
            pass
    return _IN_MEMORY_RECOMMENDATIONS.get(rec_id)


async def update_farm_profile_opt_out(phone_number: str, opted_out: bool) -> Optional[Dict[str, Any]]:
    """Update opted_out status of a farm profile in Firestore / in-memory store."""
    update_data = {
        "opted_out": opted_out,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("farm_profiles").document(phone_number)
            await doc_ref.set(update_data, merge=True)
        except Exception:
            pass
    if phone_number in _IN_MEMORY_FARM_PROFILES:
        _IN_MEMORY_FARM_PROFILES[phone_number].update(update_data)
        return _IN_MEMORY_FARM_PROFILES[phone_number]
    return None


async def save_outcome_feedback(recommendation_id: str, feedback: str) -> Optional[Dict[str, Any]]:
    """Persist farmer outcome feedback on an existing IrrigationRecommendation record."""
    update_data = {
        "outcome_feedback": feedback,
        "outcome_updated_at": datetime.now(timezone.utc).isoformat()
    }
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("irrigation_recommendations").document(recommendation_id)
            await doc_ref.set(update_data, merge=True)
        except Exception:
            pass
    if recommendation_id in _IN_MEMORY_RECOMMENDATIONS:
        _IN_MEMORY_RECOMMENDATIONS[recommendation_id].update(update_data)
        return _IN_MEMORY_RECOMMENDATIONS[recommendation_id]
    return None



async def get_latest_recommendation_for_user(phone_number: str) -> Optional[Dict[str, Any]]:
    client = get_firestore_client()
    if client:
        try:
            from google.cloud.firestore import Query
            query = client.collection("irrigation_recommendations").where("phone_number", "==", phone_number).order_by("dispatched_at", direction=Query.DESCENDING).limit(1)
            docs = query.stream()
            async for doc in docs:
                return doc.to_dict()
        except Exception:
            pass
    user_recs = [r for r in _IN_MEMORY_RECOMMENDATIONS.values() if r.get("phone_number") == phone_number]
    if user_recs:
        user_recs.sort(key=lambda x: x.get("dispatched_at", ""), reverse=True)
        return user_recs[0]
    return None


async def save_triage_request(triage_data: Dict[str, Any]) -> Dict[str, Any]:
    request_id = triage_data["request_id"]
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("disease_triage_requests").document(request_id)
            await doc_ref.set(triage_data, merge=True)
        except Exception:
            pass
    _IN_MEMORY_TRIAGE_REQUESTS[request_id] = triage_data
    return triage_data


def parse_profile_command(text: str, profile: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Parse rule-based farm profile view/update command.
    
    Returns (is_profile_cmd, updated_fields, confirmation_text).
    """
    if not text:
        return False, None, ""

    raw_lower = text.strip().lower()
    lang = profile.get("preferred_language", "french").lower()
    
    # 1. Profile View Command
    if raw_lower in ["profile", "view profile", "mon profil", "profil"]:
        crop = profile.get("crop_type", "tomatoes")
        area = profile.get("acreage_hectares", 10.0)
        if lang == "darija":
            msg = (
                f"🌾 *Profile dyalk:*\n"
                f"• Mahsoul: {crop}\n"
                f"• Masaha: {area} ha\n"
                f"• Lougha: Darija"
            )
        else:
            msg = (
                f"🌾 *Votre Profil Ferme:*\n"
                f"• Culture: {crop}\n"
                f"• Superficie: {area} ha\n"
                f"• Langue: Français"
            )
        return True, None, msg

    # 2. Update Crop
    crop_match = re.search(r'^(?:update|modifier)\s+crop\s+(.+)$', raw_lower) or re.search(r'^(?:update|modifier)\s+culture\s+(.+)$', raw_lower)
    if crop_match:
        new_crop = crop_match.group(1).strip()
        updated_fields = {"crop_type": new_crop}
        if lang == "darija":
            msg = f"Safi, beddelna l'mahsoul l '{new_crop}'."
        else:
            msg = f"Profil mis à jour: Culture = '{new_crop}'."
        return True, updated_fields, msg

    # 3. Update Area / Acreage
    area_match = re.search(r'^(?:update|modifier)\s+(?:area|superficie|acreage)\s+([0-9]+(?:\.[0-9]+)?)\s*(?:ha|hectares)?$', raw_lower)
    if area_match:
        new_area = float(area_match.group(1))
        updated_fields = {"acreage_hectares": new_area}
        if lang == "darija":
            msg = f"Safi, beddelna l'masaha l {new_area} ha."
        else:
            msg = f"Profil mis à jour: Superficie = {new_area} ha."
        return True, updated_fields, msg

    # 4. Update Language
    lang_match = re.search(r'^(?:update|modifier)\s+(?:language|langue)\s+(french|français|darija)$', raw_lower)
    if lang_match:
        target_lang = "darija" if "darija" in lang_match.group(1) else "french"
        updated_fields = {"preferred_language": target_lang}
        if target_lang == "darija":
            msg = "Safi, beddelna l'lougha l Darija."
        else:
            msg = "Profil mis à jour: Langue définie sur le Français."
        return True, updated_fields, msg

    # 5. Unrecognized update command fallback
    if raw_lower.startswith("update ") or raw_lower.startswith("modifier "):
        if lang == "darija":
            fallback = (
                "Ktaba dyal update ma mfehoumach.\n"
                "Jarrab: 'update crop tomatoes' aw 'update area 8 ha'."
            )
        else:
            fallback = (
                "Commande de mise à jour non reconnue.\n"
                "Exemples valides: 'update crop tomatoes' ou 'update area 8 ha'."
            )
        return True, None, fallback

    return False, None, ""


async def save_pin_session(session_data: Dict[str, Any]) -> Dict[str, Any]:
    phone_number = session_data["phone_number"]
    session_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("farm_sessions").document(phone_number)
            await doc_ref.set(session_data, merge=True)
        except Exception:
            pass
    _IN_MEMORY_PIN_SESSIONS[phone_number] = session_data
    return session_data


async def get_pin_session(phone_number: str) -> Optional[Dict[str, Any]]:
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("farm_sessions").document(phone_number)
            doc = await doc_ref.get()
            if doc.exists:
                return doc.to_dict()
        except Exception:
            pass
    return _IN_MEMORY_PIN_SESSIONS.get(phone_number)


async def delete_pin_session(phone_number: str) -> None:
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("farm_sessions").document(phone_number)
            await doc_ref.delete()
        except Exception:
            pass
    _IN_MEMORY_PIN_SESSIONS.pop(phone_number, None)


async def save_farm_parcel(phone_number: str, parcel_data: Dict[str, Any]) -> Dict[str, Any]:
    parcel_record = {
        "parcel": parcel_data,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("farm_profiles").document(phone_number)
            await doc_ref.set(parcel_record, merge=True)
        except Exception:
            pass
    if phone_number in _IN_MEMORY_FARM_PROFILES:
        _IN_MEMORY_FARM_PROFILES[phone_number]["parcel"] = parcel_data
    _IN_MEMORY_FARM_PARCELS[phone_number] = parcel_data
    return parcel_data


async def get_farm_parcel(phone_number: str) -> Optional[Dict[str, Any]]:
    profile = await get_farm_profile(phone_number)
    if profile and "parcel" in profile:
        return profile["parcel"]
    return _IN_MEMORY_FARM_PARCELS.get(phone_number)


async def save_pending_intent(phone_number: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
    """Persist a draft voice intent in Firestore under pending_intents collection."""
    now_utc = datetime.now(timezone.utc)
    from datetime import timedelta
    created_at_str = intent_data.get("created_at") or now_utc.isoformat()
    expires_at_str = intent_data.get("expires_at") or (now_utc + timedelta(minutes=15)).isoformat()
    
    payload = {
        "pending_voice_intent": {
            "intent_type": intent_data.get("intent_type", "MODIFY_IRRIGATION"),
            "proposed_adjustment_minutes": intent_data.get("proposed_adjustment_minutes", 15),
            "confidence_score": float(intent_data.get("confidence_score", 0.85)),
            "transcribed_text": intent_data.get("transcribed_text", ""),
            "created_at": created_at_str,
            "expires_at": expires_at_str,
            "status": intent_data.get("status", "AWAITING_CONFIRMATION")
        }
    }
    
    doc_id = f"pending_{phone_number}"
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("pending_intents").document(doc_id)
            await doc_ref.set(payload, merge=True)
        except Exception:
            pass
            
    _IN_MEMORY_PENDING_INTENTS[phone_number] = payload
    return payload


async def get_pending_intent(phone_number: str) -> Optional[Dict[str, Any]]:
    """Retrieve active pending intent for phone number, checking 15-minute TTL expiration."""
    doc_id = f"pending_{phone_number}"
    record = None
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("pending_intents").document(doc_id)
            doc = await doc_ref.get()
            if doc.exists:
                record = doc.to_dict()
        except Exception:
            pass
            
    if not record:
        record = _IN_MEMORY_PENDING_INTENTS.get(phone_number)
        
    if not record or "pending_voice_intent" not in record:
        return None
        
    inner = record["pending_voice_intent"]
    expires_at_raw = inner.get("expires_at")
    if expires_at_raw:
        try:
            exp_time = datetime.fromisoformat(expires_at_raw.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > exp_time:
                inner["status"] = "EXPIRED"
                await update_pending_intent_status(phone_number, "EXPIRED")
        except Exception:
            pass
            
    return record


async def update_pending_intent_status(phone_number: str, status: str) -> Optional[Dict[str, Any]]:
    """Update status of pending intent for phone number."""
    record = await get_pending_intent(phone_number)
    if not record or "pending_voice_intent" not in record:
        return None
        
    record["pending_voice_intent"]["status"] = status
    doc_id = f"pending_{phone_number}"
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("pending_intents").document(doc_id)
            await doc_ref.set(record, merge=True)
        except Exception:
            pass
            
    _IN_MEMORY_PENDING_INTENTS[phone_number] = record
    return record


async def delete_pending_intent(phone_number: str) -> None:
    """Delete pending intent record."""
    doc_id = f"pending_{phone_number}"
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("pending_intents").document(doc_id)
            await doc_ref.delete()
        except Exception:
            pass
    _IN_MEMORY_PENDING_INTENTS.pop(phone_number, None)


async def save_inbound_timestamp(phone_number: str, timestamp_str: Optional[str] = None) -> str:
    """Save ISO-8601 UTC timestamp of last inbound message received from user."""
    if not timestamp_str:
        timestamp_str = datetime.now(timezone.utc).isoformat()
    
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("farm_profiles").document(phone_number)
            await doc_ref.set({"last_inbound_timestamp": timestamp_str}, merge=True)
        except Exception:
            pass
            
    _IN_MEMORY_INBOUND_TIMESTAMPS[phone_number] = timestamp_str
    if phone_number in _IN_MEMORY_FARM_PROFILES:
        _IN_MEMORY_FARM_PROFILES[phone_number]["last_inbound_timestamp"] = timestamp_str
    return timestamp_str


async def get_inbound_timestamp(phone_number: str) -> Optional[str]:
    """Retrieve ISO-8601 UTC timestamp of last inbound message received from user."""
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("farm_profiles").document(phone_number)
            doc = await doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                if "last_inbound_timestamp" in data:
                    return data["last_inbound_timestamp"]
        except Exception:
            pass
            
    if phone_number in _IN_MEMORY_INBOUND_TIMESTAMPS:
        return _IN_MEMORY_INBOUND_TIMESTAMPS[phone_number]
    if phone_number in _IN_MEMORY_FARM_PROFILES:
        return _IN_MEMORY_FARM_PROFILES[phone_number].get("last_inbound_timestamp")
    return None


