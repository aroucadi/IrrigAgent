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
    # Word-internal Arabizi digit substitutions for Arabic phonemes (e.g. 'm3ak', '7na', '9dim')
    # Excludes standalone choice digits ('3'), time strings ('06h30'), and quantities ('30 min')
    if re.search(r'\b[a-zA-Z]+[379][a-zA-Z0-9]*\b|\b[a-zA-Z0-9]*[379][a-zA-Z]+\b', text):
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
    phone_number = profile_data["phone_number"]
    profile_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    client = get_firestore_client()
    if client:
        try:
            doc_ref = client.collection("farm_profiles").document(phone_number)
            await doc_ref.set(profile_data, merge=True)
        except Exception:
            pass
    
    if phone_number in _IN_MEMORY_FARM_PROFILES:
        _IN_MEMORY_FARM_PROFILES[phone_number].update(profile_data)
    else:
        profile_data["created_at"] = datetime.now(timezone.utc).isoformat()
        _IN_MEMORY_FARM_PROFILES[phone_number] = profile_data
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
