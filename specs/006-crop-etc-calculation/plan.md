# Implementation Plan: Crop-Specific ETc Calculation

**Branch**: `006-crop-etc-calculation` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/006-crop-etc-calculation/spec.md)

**Input**: Feature specification from `/specs/006-crop-etc-calculation/spec.md`

## Summary

Implement crop-specific evapotranspiration ($\text{ET}_c = \text{ET}_0 \times K_c$) calculation logic in IrrigAgent using static FAO-56 crop coefficient lookup tables ($K_{c,\text{ini}}$, $K_{c,\text{mid}}$, $K_{c,\text{end}}$) and dynamic growth stage tracking derived from planting date. Integrates seamlessly into `app/decision.py` and `app/weather.py` daily pulls, providing accurate crop water demand while maintaining deterministic fallback logic ($K_c = 1.00$) when planting metadata is unrecorded.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Pydantic, httpx  
**Storage**: Firestore (Farm profiles) + static in-memory lookup module (`app/fao56.py`)  
**Testing**: pytest  
**Target Platform**: GCP Cloud Run  
**Project Type**: Python web service / decision engine  
**Performance Goals**: ETc calculation completed in $<10\text{ms}$ per farm profile  
**Constraints**: Zero-broken-tests policy, deterministic rule-based logic (Constitution Principle II)  
**Scale/Scope**: Primary Moroccan crops (Tomatoes, Citrus, Watermelon, Olives, Potatoes)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Assessment | Status |
|---|---|---|
| **I. Human-in-the-Loop Only** | ETc calculation feeds into daily WhatsApp recommendation message for farmer confirmation. No automated hardware control. | ✅ PASS |
| **II. Rule-Based First Logic** | $\text{ET}_c = \text{ET}_0 \times K_c$ is calculated purely deterministically with linear stage interpolation. Zero LLM dependency for water math. | ✅ PASS |
| **III. ONSSA Disclaimer** | IrrigAgent core decision messages preserve ONSSA disclaimers where required. | ✅ PASS |
| **IV. WhatsApp Sandbox Tier** | Recommendation messages formatted for WhatsApp Cloud API sandbox. | ✅ PASS |
| **V. Scope Boundary** | Strictly bounded to ETc mathematical refinement. No hardware or payment integrations. | ✅ PASS |
| **VI. End-to-End Demoability** | Testable end-to-end via decision test suite and WhatsApp simulation. | ✅ PASS |
| **VII. IaC** | Backend changes deployable via existing Cloud Run container pipeline. | ✅ PASS |
| **VIII. Quality & Verification Gates** | Unit test suite targeting 100% coverage of stage interpolation boundaries and fallback cases. | ✅ PASS |

## Project Structure

### Documentation (this feature)

```text
specs/006-crop-etc-calculation/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (/speckit-plan output)
├── research.md          # FAO-56 lookup & interpolation research (/speckit-plan Phase 0)
├── data-model.md        # FAO56CropEntry & ETcResult schemas (/speckit-plan Phase 1)
├── quickstart.md        # Runnable verification guide (/speckit-plan Phase 1)
├── contracts/           # API function contracts (/speckit-plan Phase 1)
│   └── etc_calculation_api.md
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (/speckit-tasks output)
```

### Source Code (repository root)

```text
app/
├── fao56.py             # [NEW] FAO-56 crop lookup catalog & ETc calculation engine
├── decision.py          # [MODIFY] Update decision logic to use ETc = ET0 * Kc
├── schemas.py           # [MODIFY] Add FarmProfileCropMeta & ETcCalculationResult schemas
├── main.py              # [MODIFY] Wire crop parameters into recommendation endpoint
└── weather.py           # Reference Open-Meteo ET0 pull module

tests/
└── unit/
    ├── test_fao56.py    # [NEW] Comprehensive unit tests for FAO-56 stage interpolation
    └── test_decision.py # [MODIFY] Update decision tests for ETc values
```

**Structure Decision**: Single project modular layout reusing existing `app/` and `tests/` directories.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No constitution violations. Zero complex patterns added.*
