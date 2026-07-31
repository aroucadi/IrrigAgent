import os
from dotenv import load_dotenv

load_dotenv()

# Meta WhatsApp Cloud API settings
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "irrigagent_verify_token")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v20.0")

# GCP Project ID & Firestore
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "irrigagent-dev")

# Batch Job Protection Token
JOB_SECRET_TOKEN = os.getenv("JOB_SECRET_TOKEN", "irrigagent_secret_token")

# Voice Teaser Feature Flag
ENABLE_DARIJA_VOICE_TEASER = os.getenv("ENABLE_DARIJA_VOICE_TEASER", "false").lower() in ("true", "1", "yes")

# Image Quality Pre-Filter OpenCV Settings
PREFILTER_ENABLED = os.getenv("PREFILTER_ENABLED", "true").lower() in ("true", "1", "yes")
PREFILTER_BLUR_THRESHOLD = float(os.getenv("PREFILTER_BLUR_THRESHOLD", "100.0"))
PREFILTER_MIN_LUMINANCE = float(os.getenv("PREFILTER_MIN_LUMINANCE", "40.0"))
PREFILTER_MAX_LUMINANCE = float(os.getenv("PREFILTER_MAX_LUMINANCE", "220.0"))
PREFILTER_MAX_DARK_RATIO = float(os.getenv("PREFILTER_MAX_DARK_RATIO", "0.40"))
PREFILTER_MAX_BRIGHT_RATIO = float(os.getenv("PREFILTER_MAX_BRIGHT_RATIO", "0.35"))
PREFILTER_MIN_WIDTH = int(os.getenv("PREFILTER_MIN_WIDTH", "400"))
PREFILTER_MIN_HEIGHT = int(os.getenv("PREFILTER_MIN_HEIGHT", "400"))
PREFILTER_MIN_HUE = int(os.getenv("PREFILTER_MIN_HUE", "35"))
PREFILTER_MAX_HUE = int(os.getenv("PREFILTER_MAX_HUE", "85"))
PREFILTER_MIN_FOLIAGE_RATIO = float(os.getenv("PREFILTER_MIN_FOLIAGE_RATIO", "0.30"))

# Phase 2.2b Vision Model Settings & Milestone Triggers
PHASE_2_2B_ACTIVE = os.getenv("PHASE_2_2B_ACTIVE", "false").lower() in ("true", "1", "yes")
IAV_MILESTONE_THRESHOLD = int(os.getenv("IAV_MILESTONE_THRESHOLD", "500"))
FAIL_CLOSED_CONFIDENCE_THRESHOLD = float(os.getenv("FAIL_CLOSED_CONFIDENCE_THRESHOLD", "0.75"))
TEMPERATURE_SCALING_PARAM = float(os.getenv("TEMPERATURE_SCALING_PARAM", "1.25"))
# Extreme Weather Advisory Threshold Settings
HEAT_WARNING_TEMP_C = float(os.getenv("HEAT_WARNING_TEMP_C", "40.0"))
FROST_WARNING_TEMP_C = float(os.getenv("FROST_WARNING_TEMP_C", "2.0"))

ONSSA_REGISTRY_PATH = os.getenv("ONSSA_REGISTRY_PATH", os.path.join("data", "onssa_registry.json"))



