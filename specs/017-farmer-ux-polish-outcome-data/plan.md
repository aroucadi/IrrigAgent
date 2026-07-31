# Implementation Plan: v1.0 Farmer UX Polish, Code Quality Cleanup, and Outcome-Data Foundation

**Branch**: `017-farmer-ux-polish-outcome-data` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/017-farmer-ux-polish-outcome-data/spec.md)

**Input**: Feature specification from `/specs/017-farmer-ux-polish-outcome-data/spec.md`

## Summary

This feature resolves the remaining "To Do" items from Version 1.0 in `backlog.md` (UX-001 non-daily advisory portion, UX-002, UX-003, UX-004, UX-005, and SMELL-001 through SMELL-003) and incorporates critical YC partner feedback for explicit onboarding data consent and outcome-feedback quick-reply data collection ("Did you irrigate as recommended? Yes / Less / More / Skipped").

Implementation updates interactive button message routing in `app/main.py` and `app/decision.py`, adds opt-out filtering in daily recommendation batch jobs, implements explicit onboarding state machine prompts, captures outcome feedback in Firestore recommendation records, and fixes code quality smells in markdown fence stripping, Sentinel-2 band array shape alignment (`out_shape`), and GenAI imports.

---

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, httpx, rasterio, numpy, google-genai, pytest  
**Storage**: Google Cloud Firestore (`farms`, `recommendations`)  
**Testing**: `pytest tests/`  
**Target Platform**: GCP Cloud Run  
**Project Type**: Web Service / WhatsApp Messaging Service  
**Performance Goals**: Sub-second webhook execution for text/button messages  
**Constraints**: Meta WhatsApp Cloud API Sandbox Tier, WhatsApp 20-character button title limit  
**Scale/Scope**: Solo founder pilot application (< 5 verified numbers, lightweight Firestore schema)  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Human-in-the-Loop Only (PASS)**: Voice pending intent actions and recommendations require explicit farmer confirmation via button tap or text reply. Zero hardware control.
- **Principle II: Rule-Based First Logic (PASS)**: Onboarding state machine, opt-out logic, and help menu routing use deterministic rule-based checks. LLM dynamic parsing is isolated to voice ASR.
- **Principle IV: WhatsApp Cloud API Sandbox Tier Only (PASS)**: Utilizes Meta WhatsApp Cloud API sandbox endpoints for button and list payload dispatches.
- **Principle V: Strict Scope Boundary & Cut List Enforcement (PASS)**: Excludes hardware control, billing, multi-farm scheduling, and non-WhatsApp voice fallbacks.
- **Principle VI: End-to-End Demoability (PASS)**: All features testable via WhatsApp test numbers and local pytest integration suites.
- **Principle VIII: Quality, Security & Automated Verification Gates (PASS)**:
  - Zero-Broken-Tests policy enforced (`pytest tests/`).
  - No synthetic fallback signals matching test-detection patterns (CRIT-007).
  - Explicit unit test coverage added for SMELL-001, SMELL-002, and SMELL-003.

---

## Project Structure

### Documentation (this feature)

```text
specs/017-farmer-ux-polish-outcome-data/
├── spec.md              # Feature specification
├── plan.md              # This implementation plan
├── research.md          # Technical decisions & SMELL fixes (Phase 0)
├── data-model.md        # Firestore schema extensions & state machine (Phase 1)
├── quickstart.md        # Automated test & manual verification guide (Phase 1)
├── contracts/           # WhatsApp interactive payload schemas (Phase 1)
│   └── whatsapp-interactive-menu-contract.md
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code Impact

```text
app/
├── main.py              # Slash command routing (/help, /stop, /start), interactive button webhook handler
├── decision.py          # process_pending_intent_reply(), parse_voice_intent() (SMELL-001, SMELL-003)
├── sentinel.py          # fetch_sentinel2_bands() out_shape enforcement (SMELL-002)
├── firestore_client.py   # Farm profile onboarding fields, opt-out flag, recommendation outcome_feedback
└── jobs.py              # Daily recommendation batch filtering for opted_out profiles

tests/
├── unit/
│   ├── test_voice_darija_stt.py     # Pending intent button/text resolution test & SMELL-001/003 tests
│   ├── test_help_menu_buttons.py    # /help menu interactive button rendering test
│   ├── test_opt_out_flow.py         # Opt-out / opt-in & batch job exclusion test
│   ├── test_onboarding_consent.py   # Real location/crop onboarding & consent text test
│   ├── test_outcome_feedback.py     # Outcome feedback button persistence test
│   └── test_sentinel_canopy_heatmap.py # Sentinel-2 band out_shape matching test (SMELL-002)
```

---

## Complexity Tracking

> *No constitutional violations requiring justification.*

| Component | Architecture Choice | Rationale |
|---|---|---|
| Outcome Feedback | Add field `outcome_feedback` to `IrrigationRecommendation` | Avoids introducing new collections; leverages existing document ID. |
| Button Titles | Limit button title strings to <= 20 chars | Strictly satisfies Meta WhatsApp API payload schema rules. |
| SMELL-002 Fix | Pass `out_shape` to `src_red.read()` and `src_nir.read()` | Directly resolves window bounding box pixel rounding without resampling noise. |
