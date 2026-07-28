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
