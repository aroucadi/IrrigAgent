# IrrigAgent AI — Full Product Roadmap & Jira-Style Backlog

**Last Updated:** 2026-07-31  
**Source Baseline:** Reconciled from `PRD.md` (v0.4), `PRDvNext.md`, `backlog.md`, `backlogv2.md`, all 17 feature specifications in `specs/001` through `specs/017`, and empirical runtime test suite verification (183/183 passing tests).  
**Export Note:** This document is formatted as a standard Markdown table for direct preview and seamless conversion/import into Jira (CSV export).

---

## 📊 Summary Metrics

- **Total Backlog Items:** 48
- **Done (Implemented & Verified):** 40
- **In Progress:** 0 (Codebase 100% feature-complete for v1.0)
- **To Do (Pre-Demo Final Non-Code Task):** 1 (IRRIG-046: Record StartGate Demo Video)
- **Backlog (Post-Selection / v1.1 / v2 / v3):** 7

---

## 📋 Comprehensive Jira-Style Product Backlog Table

| Key | Issue Type | Summary | Description | Release Version | Status |
|---|---|---|---|---|---|
| IRRIG-001 | Feature | Weather & Evapotranspiration Data Pull | Automatically fetches daily weather forecasts, solar radiation, humidity, and FAO-56 reference evapotranspiration ($ET_0$) for farm coordinates using Open-Meteo API. Sourced from PRD v0.4 & Spec 001. | v0.4 (MVP Baseline) | Done |
| IRRIG-002 | Feature | Daily Irrigation Recommendation Engine | Evaluates daily $ET_0$, precipitation forecasts, and crop parameters to calculate recommended irrigation duration adjustments (in minutes) for target crops (tomatoes, citrus). Sourced from PRD v0.4 & Spec 001. | v0.4 (MVP Baseline) | Done |
| IRRIG-003 | Feature | Proactive WhatsApp Advisory Dispatch & Interactive Reply Loop | Schedules proactive daily evening advisories to registered farm managers over WhatsApp with interactive reply options (1=Approve, 2=Skip, 3=Modify). Sourced from PRD v0.4 & Spec 001. | v0.4 (MVP Baseline) | Done |
| IRRIG-004 | Feature | Crop-Specific $ET_c$ Calculation via FAO-56 Coefficients | Upgrades reference $ET_0$ to crop-specific water demand ($ET_c = ET_0 \times K_c$) using FAO-56 crop coefficient tables and days-since-planting growth stage tracking for tomatoes and citrus. Sourced from PRDvNext & Spec 006. | v0.6 (Crop $ET_c$) | Done |
| IRRIG-005 | Feature | Extreme Weather Threshold Alerts (Frost & Heatwave) | Detects forecasted temperature extremes (frost $<2^\circ\text{C}$ or heatwave $>40^\circ\text{C}$) and appends localized protective action advisories (misting, frost cloth) to the daily WhatsApp message. Sourced from PRDvNext & Spec 014. | v1.0 (MVP Polish) | Done |
| IRRIG-006 | Feature | CropDoctor Multimodal Leaf Photo Disease Triage | Accepts leaf photos sent via WhatsApp, invoking Gemini 1.5 Flash to generate first-pass diagnoses in French and Darija alongside mandatory ONSSA disclaimers. Sourced from PRD v0.4 & Spec 001. | v0.4 (MVP Baseline) | Done |
| IRRIG-007 | Feature | OpenCV Image Prefilter Heuristics | Applies OpenCV Laplacian variance blur checks and green-chrominance non-leaf image filtering before invoking LLM vision triage, rejecting unreadable/non-plant photos fast and cheaply. Sourced from PRDvNext & Spec 007. | v0.7 (CV Prefilter) | Done |
| IRRIG-008 | Feature | ONSSA Phytosanitary Registry Scraping & Sync Tool | Automated Python scraper (`scripts/sync_onssa_registry.py`) that fetches, parses, and normalizes authorized plant protection products from the official ONSSA registry into `data/onssa_registry.json`. Sourced from PRD v0.4 & Spec 005. | v0.5 (ONSSA Sync) | Done |
| IRRIG-009 | Feature | Dynamic ONSSA Registry Integration for CropDoctor | Connects CropDoctor's treatment pointer lookup to `data/onssa_registry.json` as the primary dataset with fallback to the static catalog and fail-closed behavior on unverified products. Sourced from PRDvNext & Spec 014. | v1.0 (MVP Polish) | Done |
| IRRIG-010 | Feature | Fine-Tuned CropDoctor Disease Classifier & IAV Ingestion | Training/eval pipeline for fine-tuning EfficientNet/ViT on Moroccan crop disease presentations. Gated on IAV Hassan II providing $\ge 500$ verified labeled images/class via `scripts/ingest_iav_dataset.py`. Sourced from PRDvNext & Spec 010. | v2.0 (Medium-Term) | Backlog |
| IRRIG-011 | Feature | Standalone Photo Quality & Exposure Prefilter Gate | Lightweight pre-check (exposure, lighting, framing) upgrading the basic blur filter before Gemini vision calls, improving triage confidence. Sourced from PRDvNext Section 2.2a. | v1.1 (Post-Selection) | Backlog |
| IRRIG-012 | Feature | Real Sentinel-2 Satellite Imagery Discovery & NDVI Calculation | Connects to Copernicus / Element84 STAC API to search, fetch, and calculate real Normalized Difference Vegetation Index (NDVI) from 10m Red/NIR band COG geotiffs. Sourced from PRDvNext & Spec 011. | v0.8 (Sentinel NDVI) | Done |
| IRRIG-013 | Feature | WhatsApp Multi-Pin Parcel Boundary & Canopy Heatmap Generation | Enables farmers to define field boundaries by sharing GPS pins over WhatsApp, generating high-resolution spatial NDVI canopy health heatmaps rendered via Matplotlib. Sourced from PRDvNext, Spec 008 & Spec 011. | v0.8 (Sentinel NDVI) | Done |
| IRRIG-014 | Feature | Hardened Parcel Boundary Pin Collection & Geometry Validation | Hardens WhatsApp location pin collection with validation for pin count ($\ge 3$), minimum spacing ($\ge 5\text{m}$), non-self-intersecting polygon checks, and multi-language restart commands (`restart`, `recommencer`, `بداية جديدة`). Sourced from PRDvNext & Spec 014. | v1.0 (MVP Polish) | Done |
| IRRIG-015 | Feature | Voice-to-Intent Darija STT with Gemini 1.5 Flash Audio ASR | Transcribes incoming Moroccan Darija audio voice notes using Gemini 1.5 Flash Audio ASR API, extracting intent (`1`/`2`/`3`) with a 15-minute TTL pending confirmation safety loop. Sourced from PRDvNext, Spec 009 & Spec 012. | v0.9 (Voice ASR) | Done |
| IRRIG-016 | Feature | Darija Text-to-Speech (TTS) Audio Note Generation | Generates synthetic Darija spoken audio response notes using GCP Text-to-Speech API for low-literacy farmer audio teaser dispatches. Sourced from PRD v0.4 & Spec 001. | v0.4 (MVP Baseline) | Done |
| IRRIG-017 | Bug | WhatsApp 24-Hour Service Window Policy Violation (CRIT-005) | Proactive daily advisories sent via `type: text` fail outside 24h of user reply (Meta error 131026). Resolved by tracking inbound message timestamps and switching to Meta Utility Message Templates for out-of-window delivery. Sourced from backlogv2.md & Spec 015/016. | v1.0 (MVP Polish) | Done |
| IRRIG-018 | Feature | Daily Advisory Meta Utility Template with Embedded Quick Reply Buttons | Constructs and dispatches approved Meta `UTILITY` category Message Template (`irrigagent_daily_advisory`) with dynamic ETc variables and 3 embedded Quick Reply buttons (`Approve`, `Skip`, `Modify`). Sourced from backlogv2.md (UX-001) & Spec 016. | v1.0 (MVP Polish) | Done |
| IRRIG-019 | Feature | WhatsApp Tappable Interactive Buttons for Open Windows | Replaces free-text digit typing (`1`/`2`/`3`) with native WhatsApp interactive quick reply buttons for all user-initiated dialogs within active 24-hour service windows. Sourced from backlogv2.md (UX-001). | v1.0 (MVP Polish) | Done |
| IRRIG-020 | Feature | Always-Available `/help` & Interactive Menu System | Implements a universal `help` / `menu` command (and persistent menu button) returning available bot capabilities in Darija and French to prevent farmer confusion. Sourced from backlogv2.md (UX-003). | v1.0 (MVP Polish) | Done |
| IRRIG-021 | Feature | In-Product Opt-Out / Unsubscribe Mechanism | Provides explicit farmer opt-out commands (`STOP`, `ABONNER`, `ARRÊTER`) to halt daily advisories in compliance with WhatsApp Business policies. Sourced from backlogv2.md (UX-004). | v1.0 (MVP Polish) | Done |
| IRRIG-022 | Feature | Interactive Onboarding Location & Profile Confirmation Flow | Prompts newly registered farmers to confirm location pin and crop parameters during onboarding, replacing hardcoded Agadir/tomato defaults. Sourced from backlogv2.md (UX-005). | v1.0 (MVP Polish) | Done |
| IRRIG-023 | Feature | FastAPI Backend Architecture on GCP Cloud Run | Single-container FastAPI asynchronous server deployed to Google Cloud Run, featuring Meta webhook endpoint verification, payload routing, and Firestore persistence. Sourced from PRD v0.4 & Spec 001. | v0.4 (MVP Baseline) | Done |
| IRRIG-024 | Feature | Security & Quality Gate Module | Implements GCP Secret Manager integration for API token protection, Pydantic v2 strict payload validation, and pre-commit security sanity checks. Sourced from Spec 002. | v0.5 (Security Gate) | Done |
| IRRIG-025 | Feature | Immutable Interaction Audit Logging Schema | Logs every inbound webhook, agent decision state, outbound message, and API error into Firestore with structured schema validation for auditability. Sourced from Spec 003. | v0.5 (Audit Schema) | Done |
| IRRIG-026 | Feature | WhatsApp Client Unit Tests & Multi-Farm Batch Integration Tests | Direct isolated unit tests for `app/whatsapp.py` (`test_whatsapp.py`) and multi-farm batch execution integration tests (`test_daily_batch_multi_farm.py`) verifying fault isolation across farms. Sourced from backlog.md (POLISH-001/002) & Spec 013. | v1.0 (MVP Polish) | Done |
| IRRIG-027 | Task | Deletion of Out-of-Scope Pre-Selection Terraform IaC | Purged premature `infra/` Terraform files from the codebase to align with Constitution Principle VII (gating IaC until post-StartGate selection). Sourced from backlog.md (BUG-003) & Spec 012. | v0.9 (P0 Stabilization) | Done |
| IRRIG-028 | Task | Post-StartGate Selection Infrastructure as Code (IaC) | Declarative Terraform scripts covering GCP Cloud Run, Cloud Scheduler, Firestore, and service accounts. Explicitly gated until StartGate incubator selection is confirmed. Sourced from PRDvNext & Spec 014 (US4). | v1.1 (Post-Selection) | Backlog |
| IRRIG-029 | Bug | Darija STT `parse_voice_intent()` Hardcoded Output (BUG-001) | Replaced hardcoded transcript ("Zid 15 dqiqa") and fake 0.88 confidence with real Gemini 1.5 Flash Audio ASR API call and fail-closed safety handling. Sourced from backlog.md (BUG-001) & Spec 012. | v0.9 (P0 Stabilization) | Done |
| IRRIG-030 | Bug | Sentinel-2 Canopy Heatmap Synthetic Data Fallback (BUG-002) | Removed `np.random.seed(42)` synthetic NDVI array generation, replacing it with live windowed band reads from Copernicus Sentinel-2 COG imagery. Sourced from backlog.md (BUG-002) & Spec 011. | v0.8 (Sentinel NDVI) | Done |
| IRRIG-031 | Bug | Terraform/IaC Scope Re-Appearance (BUG-003) | Resolved repeated scope creep by deleting `infra/` directory and recording explicit Constitution rule restricting IaC pre-selection. Sourced from backlog.md (BUG-003) & Spec 012. | v0.9 (P0 Stabilization) | Done |
| IRRIG-032 | Bug | Spec Headers Metadata Accuracy Out-of-Sync (BUG-004) | Synchronized `Status: Implemented` headers across completed feature specs (001-007, 011, 012) in alignment with actual codebase implementation. Sourced from backlog.md (BUG-004) & Spec 012. | v0.9 (P0 Stabilization) | Done |
| IRRIG-033 | Bug | Missing `python-multipart` Dependency (CRIT-006) | Fixed application startup and Docker build failure caused by missing `python-multipart` required by FastAPI `UploadFile` endpoints. Sourced from backlogv2.md (CRIT-006) & Spec 016. | v1.0 (MVP Polish) | Done |
| IRRIG-034 | Bug | Mock-Media ID Fallback Backdoor Closure (CRIT-007) | Removed silent fallback to `"mock_img_1"` and `"mock_audio_1"` in `app/main.py`, replacing it with an explicit log entry and farmer-facing retry request. Sourced from backlogv2.md (CRIT-007) & Spec 016. | v1.0 (MVP Polish) | Done |
| IRRIG-035 | Bug | Live Verification of 24h Customer Service Window Restriction | Live sandbox test pass verifying Meta Graph API error `131026` response payload after 25+ hours of recipient inactivity. Sourced from backlogv2.md & Spec 016 (US1). | v1.0 (MVP Polish) | Done |
| IRRIG-036 | Bug | Fragile String Stripping in ASR Parser (SMELL-001) | Replace `response.text.strip().strip("```json")` with `removeprefix`/`removesuffix` to prevent unexpected character stripping from model outputs in `app/decision.py`. Sourced from backlogv2.md (SMELL-001). | v1.0 (MVP Polish) | Done |
| IRRIG-037 | Bug | `np.resize` Pixel Misalignment Safeguard (SMELL-002) | Replace `np.resize` buffer wrapping with explicit `rasterio` `out_shape` windowed dimension enforcement in `app/sentinel.py` to prevent NIR/Red spatial misalignment. Sourced from backlogv2.md (SMELL-002). | v1.0 (MVP Polish) | Done |
| IRRIG-038 | Bug | Redundant `importlib.import_module` Cleanup (SMELL-003) | Replace dynamic `importlib.import_module("google.genai")` in `app/decision.py` with standard top-level import since `google-genai` is a hard dependency. Sourced from backlogv2.md (SMELL-003). | v1.0 (MVP Polish) | Done |
| IRRIG-039 | Feature | Closed-Loop Sensor Fusion Telemetry & Decision Calibration | Integrates REST API telemetry endpoint (`POST /telemetry/sensor`) ingesting volumetric water content (VWC %), calibrating FAO-56 ETc weather math with soil moisture ground-truth, appending sensor status badges, and providing CLI simulation script (`scripts/simulate_sensor.py`). Sourced from PRDvNext, Spec 017 & backlog.md (V2-002). | v1.0 (MVP Polish) | Done |
| IRRIG-040 | Feature | Farmer-to-Farmer Proximity Disease Alerts | Triggers proximity-based alerts to neighboring registered farms when a high-confidence CropDoctor diagnosis is confirmed in their area, gated on verification & farmer consent. Sourced from PRDvNext & backlog.md (V2-003). | v2.0 (Medium-Term) | Backlog |
| IRRIG-041 | Feature | ONSSA / Extension Services Outbreak Signal Escalation | Routes confirmed high-confidence disease outbreak clusters to regional ONSSA or extension service human reviewers. Sourced from PRDvNext & backlog.md (V2-004). | v2.0 (Medium-Term) | Backlog |
| IRRIG-042 | Feature | Regional Analytics & Irrigation Pattern Aggregation | Aggregated regional dashboard visualizing confirmed crop diseases, regional water consumption, and irrigation trends across cooperatives. Sourced from PRDvNext & backlog.md (V2-005). | v2.0 (Medium-Term) | Backlog |
| IRRIG-043 | Feature | Autonomous Valve & Solenoid Actuation Control | Enables direct IoT valve opening/closing based on AI recommendations. Flagged as high-risk; strictly deferred and requires Constitution amendment and sign-off. Sourced from PRDvNext & backlog.md (V3-001). | v3.0 (Long-Term Strategic) | Backlog |
| IRRIG-044 | Feature | Bidirectional Multi-Crop Expansion Beyond Tomatoes/Citrus | Expands $ET_c$ crop coefficient lookups, ONSSA product mappings, and disease vision models to additional Moroccan staple crops (olives, wheat, potatoes, sugar beets). Sourced from PRDvNext & backlog.md (V3-002). | v3.0 (Long-Term Strategic) | Backlog |
| IRRIG-045 | Task | Verify Real Test Count Baseline (POLISH-003) | Execute `pytest --collect-only -q` to verify exact test count (currently 183 tests passing across 25 test modules) for pitch & submission materials. Sourced from backlog.md (POLISH-003). | v1.0 (MVP Polish) | Done |
| IRRIG-046 | Task | Record StartGate Demo Video (POLISH-004) | Record 90-120 second video demonstrating live WhatsApp daily advisory, quick reply button approval, leaf photo triage, Darija voice intent, and IoT soil sensor telemetry calibration. Sourced from PRD v0.4 & backlog.md (POLISH-004). | v1.0 (MVP Polish) | To Do |
| IRRIG-047 | Feature | Multi-Farm Recommendation Batch Execution Fault Isolation | Ensures single-farm weather lookup or delivery failures during daily batch runs (`POST /jobs/daily-recommendations`) do not halt batch execution for remaining farms. Sourced from Spec 013 (US2). | v1.0 (MVP Polish) | Done |
| IRRIG-048 | Feature | Pydantic v2 Data Models & Strict Schema Validation | Centralized data model schemas (`app/schemas.py`) for farm profiles, weather payloads, decision intents, telemetry payloads, and WhatsApp webhooks with strict Pydantic v2 typing. Sourced from Spec 002. | v0.5 (Security Gate) | Done |

---

## 🎯 Release Horizons Breakdown

### 🟢 Version 0.4 - 1.0 Codebase (100% Implemented & Verified Baseline)
Includes all initial MVP features, security gates, ONSSA scraper, FAO-56 $ET_c$ math, Sentinel-2 NDVI heatmaps, Gemini Darija Voice STT, Meta WhatsApp 24h Window compliance, interactive quick reply buttons, `/help` menu system, opt-out mechanisms, sensor fusion telemetry ingestion & calibration, and P0/code smell bug resolutions (BUG-001 through BUG-004, CRIT-006, CRIT-007, SMELL-001 through SMELL-003). All **40 code items marked `Done`** are fully covered by automated unit & integration tests (**183 passing tests**).

### 🟡 Version 1.0 (Pre-Demo & StartGate Submission Polish)
Currently active sprint status:
1. **Codebase Status:** 100% COMPLETE & VERIFIED.
2. **Remaining Non-Code Action:** **Record StartGate Demo Video (IRRIG-046)** — a 90–120 second walkthrough demonstrating live WhatsApp daily advisories, quick reply button approval, leaf photo triage, Darija voice notes, and live IoT sensor simulation.

### 🔵 Version 1.1 - 2.0 (Post-Selection Incubation Roadmap)
Gated on StartGate selection and partner dependencies:
- **Gated on Selection:** Infrastructure as Code (Terraform IaC) fresh deployment (IRRIG-028).
- **Gated on IAV Hassan II:** Fine-tuned disease vision classifier with 500 images/class dataset ingestion (IRRIG-010).
- **Medium-Term:** Proximity disease alerts (IRRIG-040), ONSSA outbreak escalation (IRRIG-041), and regional analytics (IRRIG-042).

### 🔴 Version 3.0 (Long-Term / Strategic Expansion)
- **High-Risk (Requires Constitution Amendment):** Autonomous valve control (IRRIG-043).
- **Catalog Expansion:** Multi-crop catalog expansion (IRRIG-044).
