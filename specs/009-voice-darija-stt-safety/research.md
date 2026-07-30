# Research: Voice-to-Intent Darija STT Safety Policy & Confirmation Prompts

## Technical Decisions

### 1. Audio Media Ingestion & Duration Bounding
- **Decision**: Download `.ogg` (opus) media files directly via Meta WhatsApp Cloud API Media URL using the configured WhatsApp Access Token. Pre-validate media duration metadata (maximum 60 seconds).
- **Rationale**: WhatsApp Cloud API webhooks deliver incoming voice messages with a `media_id`. Querying Meta's media retrieval endpoint returns raw audio bytes and file headers. Rejecting recordings >60 seconds prior to ASR reduces compute latency and API costs.
- **Alternatives Considered**:
  - *Transcoding to MP3/WAV locally*: Unnecessary overhead since Gemini 1.5 Flash natively supports `.ogg` audio ingestion.

### 2. Speech-to-Text ASR & Confidence Score Evaluation
- **Decision**: Leverage Gemini 1.5 Flash Audio ASR (via Vertex AI SDK) to transcribe Darija voice notes and compute a normalized confidence score $[0.0, 1.0]$.
- **Rationale**: Gemini 1.5 Flash excels at multilingual audio understanding, Moroccan Darija phonetics, and mixed French/Darija code-switching (e.g. "Zid 15 minutes f l'arrosage stp"). It outputs structured JSON containing transcript, extracted parameters, and confidence metrics.
- **Safety Rule**: If ASR confidence $\ge 0.80$, save draft intent and emit 2-step confirmation prompt. If confidence $< 0.80$ or unparseable, degrade to standard text menu without saving state.
- **Alternatives Considered**:
  - *OpenAI Whisper API*: Requires external cloud service outside GCP infrastructure stack; Gemini 1.5 Flash keeps processing within GCP Cloud Run / Vertex AI footprint.

### 3. Firestore Pending Intent Data Model & 15-Minute TTL Lifecycle
- **Decision**: Persist draft voice intents in Firestore under the `pending_intents` collection using document key `pending_{phone_number}` (ensuring 1 active pending intent per farmer).
- **Attributes**: `intent_id`, `phone_number`, `transcript`, `action_type`, `duration_delta_minutes`, `confidence`, `status` (`pending`, `confirmed`, `canceled`, `expired`), `created_at`, `expires_at` (15 minutes post-creation).
- **Rationale**: Document keying by phone number guarantees automatic superseding when a farmer sends a second voice note, while explicit UTC timestamp checks enforce the 15-minute TTL window without background cron dependencies.

### 4. 2-Step Confirmation Loop State Machine & Interruption Routing
- **Decision**: Implement a state-machine router in `app/whatsapp.py` / `app/decision.py`.
- **Flow Rules**:
  - *High Confidence ($\ge 0.80$)*: Store pending intent, send WhatsApp text prompt (`"I heard: Increase irrigation by +15 min. Reply 1 to CONFIRM or 2 to CANCEL."`). If `ENABLE_DARIJA_VOICE_TEASER=true`, attach a Darija TTS voice note (`app/tts_voice.py`).
  - *Reply '1'*: Validate `expires_at > now`. Execute schedule change, mark intent `confirmed`, reply success.
  - *Reply '2'*: Mark intent `canceled`, reply cancellation message.
  - *Non-numeric / Invalid Reply*: Keep intent active, re-emit prompt with choices `1` (Confirm), `2` (Cancel), `3` (Discard & open main menu).
  - *Expired (TTL > 15 min)*: Mark status `expired`, inform farmer that intent proposal expired.

### 5. Graceful Fallback Menu
- **Decision**: When confidence $< 0.80$ or audio is garbled/unparseable, return fallback text: `"I couldn't hear clearly. Please reply: 1 - Approve (+15 min), 2 - Skip today, 3 - Modify"`. No pending intent record is written to Firestore.

## Summary of Architecture & Dependencies
- **Backend Stack**: Python 3.11+, FastAPI on Cloud Run
- **Database**: GCP Firestore (`pending_intents` collection)
- **Audio Processing**: Vertex AI Gemini 1.5 Flash (Audio mode)
- **Voice Teaser Output**: GCP Text-to-Speech API (`ar-MA` voice) behind `ENABLE_DARIJA_VOICE_TEASER=true`
- **Messaging**: Meta WhatsApp Cloud API Sandbox
