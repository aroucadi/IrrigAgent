# Technical Research & Architecture Decisions: Hassan Persona

**Feature**: Hassan Persona - Proactive Irrigation Agent & Leaf Photo Triage  
**Branch**: `001-hassan-irrigation-agent`  
**Date**: 2026-07-28

---

## 1. Web Framework & Application Structure

### Decision
Use **FastAPI (Python 3.11+)** with `uvicorn` as the web application container.

### Rationale
- Built-in asynchronous I/O natively supports non-blocking HTTP calls (`httpx`) to Meta Graph API, Open-Meteo, and Vertex AI.
- Lightweight memory footprint (<80MB idle), enabling fast cold starts on GCP Cloud Run.
- Pydantic v2 data validation for webhook payloads and Firestore model schemas.

### Alternatives Considered
- *Flask*: Synchronous by default, requires WSGI wrapping or threading for async HTTP client operations.
- *Django*: Excessively heavy for a webhook API service; ORM and admin interface unnecessary for Firestore.

---

## 2. Meta WhatsApp Cloud API Integration

### Decision
Direct HTTP integration using `httpx.AsyncClient` against Meta Graph API `v20.0` sandbox endpoints.

### Rationale
- Sandbox tier supports up to 5 verified recipient phone numbers at $0 cost.
- Direct Graph API calls (`/messages`, `/media`) avoid third-party wrapper library bloat or unmaintained dependencies.
- Handles webhook verification handshake (`GET /webhook`) and event payload extraction (`POST /webhook`) cleanly.

### Alternatives Considered
- *Twilio / MessageBird*: Introduced unnecessary vendor cost, business verification overhead, and extra API latency.

---

## 3. Weather & Evapotranspiration (ET₀) Data Pipeline

### Decision
Pull daily weather forecast and FAO-56 Penman-Monteith ET₀ values from **Open-Meteo API** (`https://api.open-meteo.com/v1/forecast`).

### Rationale
- Free, open-access API requiring no API keys or subscription management.
- Provides native `et0_fao_evapotranspiration` and `precipitation_sum` parameters by latitude/longitude.
- Scheduled batch execution at 18:45 GMT+1 with 3 short-backoff retries (10s / 30s / 60s) fits inside a single Cloud Run job invocation before the 19:00 GMT+1 WhatsApp dispatch.
- Fallback logic to yesterday's stored ET₀ baseline in Firestore ensures 100% daily advisory delivery even during API hiccups.

---

## 4. CropDoctor Vision Triage & Safety Architecture

### Decision
Multimodal leaf photo triage using **Gemini 1.5 Flash via Vertex AI**, paired with a **Static ONSSA Product Lookup Table**.

### Rationale
- Gemini 1.5 Flash offers low latency (<3s) and cost-effective image analysis funded by GCP hackathon credits.
- **Hallucination Elimination**: Gemini is strictly scoped to identify the pathogen/symptom and return a confidence rating. Treatment product pointers are retrieved via deterministic code lookup from a hardcoded Python dictionary of ~10–15 tomato and citrus pathogens mapped to ONSSA-authorized active ingredients.
- **Confidence-Tiered Safety**:
  - *High/Medium Confidence (>=50%)*: Primary diagnosis + static ONSSA product pointer + mandatory disclaimer.
  - *Low Confidence (<50%)*: Cautious observation ("possible signs of discoloration, unable to confirm") + request for a clearer close-up photo + mandatory disclaimer (**NO chemical or product names provided**).

---

## 5. Persistence & State Storage

### Decision
Use **Google Cloud Firestore** in Native Mode.

### Rationale
- Serverless document database scaling to zero cost when idle.
- Flat schema structure with three simple collections:
  1. `farm_profiles` (keyed by E.164 phone number)
  2. `irrigation_recommendations` (keyed by `rec_{phone}_{YYYYMMDD}`)
  3. `disease_triage_requests` (keyed by `triage_{phone}_{timestamp}`)
- Fast document read/write latency (<20ms).
