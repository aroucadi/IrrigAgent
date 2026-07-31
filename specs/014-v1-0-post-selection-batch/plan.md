# Implementation Plan: v1.0 — ONSSA Live Registry Activation, Frost Alerts, Parcel UX Hardening, and Post-Selection IaC (gated)

**Branch**: `014-v1-0-post-selection-batch` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/014-v1-0-post-selection-batch/spec.md)

**Input**: Feature specification from `/specs/014-v1-0-post-selection-batch/spec.md`

## Summary

This plan covers four independent MVP+ / Post-Selection stories (V1-001 through V1-004):
1. **Live ONSSA Registry Activation**: Execute a `--commit` run of `scripts/sync_onssa_registry.py` to generate `data/onssa_registry.json`. Wire `app/cropdoctor.py::lookup_onssa_product()` to query the dynamic registry first (using case-insensitive, whitespace-stripped keys), falling back to static catalog table, and preserving fail-closed behavior and regulatory disclaimers.
2. **Extreme Weather Threshold Alerts**: Configure heat (40°C) and frost (2°C) temperature thresholds in `app/config.py`. Update `app/decision.py` to append clear localized warning sections and actionable advice to daily WhatsApp advisories when tomorrow's forecast crosses thresholds.
3. **Parcel UX Hardening**: Enhance `app/parcel_validation.py` to validate boundary pin count (<3), pin distance (<5m), and self-intersection. Update WhatsApp boundary handler in `app/main.py` to return clear guidance and support multi-lingual reset commands (`"restart boundary"`, `"restart"`, `"recommencer"`, `"réinitialiser"`, `"بداية جديدة"`).
4. **Post-Selection IaC (Gated)**: Strictly deferred until explicit StartGate selection confirmation. Zero implementation artifacts generated in this pass.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Open-Meteo API, Shapely (for polygon validation), Pytest

**Storage**: `data/onssa_registry.json` (dynamic dataset), Firestore Native DB (user/farm state)

**Testing**: Pytest (`pytest tests/`)

**Target Platform**: GCP Cloud Run CLI deployment (`gcloud run deploy`)

**Project Type**: Web service / Messaging application (FastAPI backend + WhatsApp Cloud API)

**Performance Goals**: Sub-second WhatsApp message parsing & decision processing

**Constraints**: Sandbox tier limits (max 5 recipient numbers); Zero hardcoded secrets; Zero facade mocks in production paths; IaC deferred

**Scale/Scope**: v1.0 Pilot batch release

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Human-in-the-Loop Only (Principle I)**: PASS — All advisories and warnings are transmitted via WhatsApp for farmer review. No automated hardware control.
2. **Rule-Based First Logic (Principle II)**: PASS — Extreme weather alerts and boundary validations use deterministic python rules without LLM dependency.
3. **Mandatory ONSSA Regulatory Disclaimer (Principle III)**: PASS — Product lookup retains mandatory verbatim disclaimer and confidence-tiered suppression rules regardless of data source.
4. **WhatsApp Cloud API Sandbox Tier Only (Principle IV)**: PASS — Uses sandbox tier endpoints.
5. **Strict Scope Boundary & Cut List Enforcement (Principle V)**: PASS — No hardware control, payments, multi-farm scheduling, or physical sensors.
6. **Infrastructure Management & Deployment Path (Principle VII)**: PASS — Pilot uses GCP Cloud Run CLI. Terraform IaC is explicitly deferred and gated (User Story 4 produces zero artifacts in this pass).
7. **Quality, Security & Automated Verification Gates (Principle VIII)**: PASS — Zero-broken-tests policy, deterministic unit test coverage, zero secrets committed.

## Project Structure

### Documentation (this feature)

```text
specs/014-v1-0-post-selection-batch/
├── plan.md              # Implementation Plan
├── research.md          # Phase 0 Research & Decisions
├── data-model.md        # Phase 1 Data Model & Schemas
├── quickstart.md        # Phase 1 Validation Guide
├── contracts/           # Phase 1 Interface Contracts
│   ├── cropdoctor_lookup_contract.json
│   └── boundary_validation_contract.json
└── checklists/
    └── requirements.md  # Spec Quality Checklist
```

### Source Code (repository root)

```text
app/
├── config.py             # Weather threshold defaults (HEAT_WARNING_TEMP_C, FROST_WARNING_TEMP_C)
├── cropdoctor.py         # Modified lookup_onssa_product() for dynamic JSON registry lookup + static fallback
├── decision.py           # Extreme weather warning evaluation & advisory text formatting
├── main.py               # WhatsApp boundary reset command parser & state handler
└── parcel_validation.py  # Hardened polygon validation (<3 pins, <5m distance, self-intersection)

data/
└── onssa_registry.json   # Output of live ONSSA scrape commit run

scripts/
└── sync_onssa_registry.py # Existing ONSSA scraper (--commit mode)

tests/
├── unit/
│   ├── test_cropdoctor.py
│   ├── test_decision.py
│   ├── test_parcel_pin_collection.py
│   └── test_weather.py
└── test_sync_onssa_registry.py
```

**Structure Decision**: Single Python project structure using `app/` service modules and `tests/` test suites.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | Fully compliant with Constitution v1.6.1 |
