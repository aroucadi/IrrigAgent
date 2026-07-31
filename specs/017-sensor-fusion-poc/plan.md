# Implementation Plan: Closed-Loop Sensor Fusion Telemetry & Decision Calibration

**Branch**: `017-sensor-fusion-poc` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/017-sensor-fusion-poc/spec.md)

**Input**: Feature specification from `/specs/017-sensor-fusion-poc/spec.md`

## Summary

Exposes a REST API endpoint `POST /telemetry/sensor` to ingest Volumetric Water Content ($\text{VWC}\%$) soil moisture telemetry, extends `app/decision.py` to fuse live ground-truth soil moisture with FAO-56 $ET_c$ weather math, generates WhatsApp daily advisories with localized sensor badges (`"📡 Données Capteur Sol"`), and provides a CLI simulation script (`scripts/simulate_sensor.py`) for live investor/incubator demos while maintaining 100% Human-in-the-Loop approval.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI 0.115.0, Pydantic 2.9.2, httpx 0.27.2, google-cloud-firestore 2.19.0  
**Storage**: Firestore (Farm profile document sensor state)  
**Testing**: pytest 8.3.3, pytest-asyncio 0.24.0  
**Target Platform**: GCP Cloud Run serverless web service  
**Project Type**: Async Web Service / REST API  
**Performance Goals**: Telemetry ingestion response time $< 200\text{ms}$  
**Constraints**: Zero hardware control; 100% human-in-the-loop via WhatsApp reply loop  
**Scale/Scope**: Hardware-ready PoC supporting mock scripts and cooperative pilot farms  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle I (Human-in-the-Loop Only)**: Recommendations transmitted via WhatsApp requiring farmer approval (1/2/3). ZERO automated hardware valve control.
- [x] **Principle II (Rule-Based First Logic)**: Decision fusion algorithm implemented via deterministic threshold calculations ($ET_c$ + VWC % delta).
- [x] **Principle IV (Sandbox Messaging)**: Messaging remains strictly on WhatsApp Cloud API Sandbox tier.
- [x] **Principle V (Scope Boundaries)**: Read-only telemetry REST API ingestion & simulation script. No physical hardware deployment required.
- [x] **Principle VII (Deployment Path)**: Deploys via GCP Cloud Run CLI (`gcloud run deploy`). No Terraform IaC dependency.
- [x] **Principle VIII (Quality & Automated Verification Gates)**: 100% automated test coverage for payload validation, decision fusion math, and fallback behavior.

## Project Structure

### Documentation (this feature)

```text
specs/017-sensor-fusion-poc/
├── plan.md              # Implementation plan document
├── research.md          # Technical research & design decisions
├── data-model.md        # Telemetry & fused decision schemas
├── quickstart.md        # Runnable validation scenarios
└── contracts/           # API & CLI interface definitions
    ├── telemetry-api.md
    └── simulator-cli.md
```

### Source Code (repository root)

```text
app/
├── main.py              # POST /telemetry/sensor endpoint route
├── schemas.py           # SensorTelemetryPayload Pydantic v2 model
├── decision.py          # Fused irrigation decision calculation logic
└── firestore_client.py  # Farm sensor state persistence helper

scripts/
└── simulate_sensor.py   # CLI telemetry simulation script for demos

tests/
├── unit/
│   ├── test_schemas.py  # Telemetry schema validation tests
│   └── test_decision.py # Sensor fusion decision calculation tests
└── integration/
    └── test_sensor_fusion.py # End-to-end telemetry ingestion & WhatsApp advisory flow
```

**Structure Decision**: Single web service project using standard FastAPI `app/` modules, root `scripts/` utility, and `tests/` suite.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | *All constitution rules satisfied* | *N/A* |
