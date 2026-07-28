import os
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
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
    """Detects Arabic script or common Arabizi digit substitutions ('3', '7', '9')."""
    if not text:
        return False
    # Arabic script Unicode range check
    if re.search(r'[\u0600-\u06FF]', text):
        return True
    # Common Arabizi digit substitutions for Arabic phonemes (3=ʿAyn, 7=Ḥāʾ, 9=Qāf)
    if re.search(r'\b\w*[379]\w*\b', text):
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
