# Implementation Plan: Sentinel-2 Canopy Heatmaps (Multi-Pin WhatsApp Interaction)

**Branch**: `008-sentinel-canopy-heatmaps` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/008-sentinel-canopy-heatmaps/spec.md)

**Input**: Feature specification from `/specs/008-sentinel-canopy-heatmaps/spec.md`

## Summary

Implement a conversational WhatsApp location-pin collection state machine (`COLLECTING_PINS`) allowing farmers to define field boundaries step-by-step. Validate polygon geometry using Shapely and the Shoelace formula ($N \ge 3$, non-self-intersecting, $0.1\text{ ha} \le \text{Area} \le 200\text{ ha}$) and persist GeoJSON representations in Firestore. Integrate Copernicus Sentinel-2 L2A satellite imagery retrieval to compute NDVI, render field-cropped high-contrast canopy health heatmaps with overlays (watermark, scale legend, date stamp), and dispatch image media with actionable irrigation advice over WhatsApp Cloud API.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Shapely, NumPy, Pillow / Rasterio, Matplotlib, Pydantic v2

**Storage**: Firestore (`farm_sessions` collection for pin state machine, `farms` collection for GeoJSON parcel storage)

**Testing**: Pytest (`tests/unit/test_parcel_pin_collection.py`, `tests/unit/test_sentinel_canopy_heatmap.py`, `tests/integration/test_whatsapp_sentinel_flow.py`)

**Target Platform**: GCP Cloud Run (Linux container)

**Project Type**: Web Service / Conversational Agent API

**Performance Goals**: Geometry validation <100ms; Sentinel-2 canopy heatmap rendering & WhatsApp media delivery <30 seconds end-to-end.

**Constraints**: Sandbox WhatsApp Cloud API (5 verified numbers limit); zero hardware control; strict 0.1–200 ha boundary bounds; 100% test pass rate; zero secrets in code.

**Scale/Scope**: v1 Hackathon Pilot (max 5 verified WhatsApp numbers, individual farm parcels).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Human-in-the-Loop Only**: Heatmaps and recommendations are delivered to farmers via WhatsApp for review/inspection; no automated solenoid/valve/pump control.
- [x] **II. Rule-Based First Logic**: Geometry checks (Shapely `is_simple`, Shoelace area) and NDVI band math ($(B08 - B04)/(B08 + B04)$) use deterministic python math; no LLM needed for core pipeline.
- [x] **III. Mandatory ONSSA Regulatory Disclaimer**: CropDoctor disclaimer rules remain preserved across system endpoints.
- [x] **IV. WhatsApp Cloud API Sandbox Tier Only**: Media and text messages dispatched strictly via Meta WhatsApp Cloud API Sandbox endpoint.
- [x] **V. Strict Scope Boundary & Cut List Enforcement**: No solenoid/hardware control, payment subscription flows, multi-farm scheduling, or physical soil hardware.
- [x] **VI. End-to-End Demoability**: Full flow testable over WhatsApp sandbox endpoint with location pin attachments.
- [x] **VII. Infrastructure as Code**: Firestore collections and Terraform/HCL definitions used for GCP provisioning.
- [x] **VIII. Quality, Security & Automated Verification Gates**: Enforces 100% pytest pass rate, zero secrets in code, pre-commit hook checks.

## Project Structure

### Documentation (this feature)

```text
specs/008-sentinel-canopy-heatmaps/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical research & decisions (Phase 0 output)
├── data-model.md        # Entities, schemas, state transitions (Phase 1 output)
├── quickstart.md        # Validation guide (Phase 1 output)
└── contracts/           # API and Webhook contracts (Phase 1 output)
    ├── whatsapp-location-webhook.md
    └── sentinel-heatmap-api.md
```

### Source Code (repository root)

```text
app/
├── main.py                   # FastAPI router & WhatsApp webhook handler
├── schemas.py                # Pydantic schemas (ParcelBoundary, PinSession, CanopyHealthReport)
├── firestore_client.py       # Firestore persistence for sessions & farm parcel GeoJSON
├── whatsapp.py               # WhatsApp messaging & media upload helpers
├── parcel_validation.py      # Polygon geometry checks & Shoelace area calculation
└── sentinel.py               # Sentinel-2 imagery fetch, NDVI computation & heatmap rendering

tests/
├── unit/
│   ├── test_parcel_pin_collection.py    # Geometry validation & Shoelace area tests
│   └── test_sentinel_canopy_heatmap.py  # NDVI calculation & color mapping tests
└── integration/
    └── test_whatsapp_sentinel_flow.py   # Multi-turn WhatsApp location webhook integration tests
```

**Structure Decision**: Single project layout extending existing `app/` modules and `tests/` directories.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No constitution violations. All features adhere strictly to IrrigAgent AI Constitution 1.4.0.*
