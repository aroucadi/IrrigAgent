# Implementation Plan: MVP Polish — WhatsApp Client Unit Tests & Multi-Farm Batch Integration Test

**Branch**: `013-mvp-polish-whatsapp-batch-tests` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/013-mvp-polish-whatsapp-batch-tests/spec.md)

**Input**: Feature specification from `/specs/013-mvp-polish-whatsapp-batch-tests/spec.md`

## Summary

Expand automated test coverage for the IrrigAgent platform by implementing dedicated unit tests for the WhatsApp Cloud API integration client (`tests/unit/test_whatsapp.py`) and a multi-farm integration test suite (`tests/integration/test_daily_batch_multi_farm.py`). All additions are strictly additive test files with zero production code changes (FR-008), operating entirely offline using local mocks (FR-009).

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, pytest, httpx, pytest-asyncio  
**Storage**: Mocked Firestore client (`tests/unit/test_firestore_client.py` pattern)  
**Testing**: `pytest tests/unit/test_whatsapp.py` and `pytest tests/integration/test_daily_batch_multi_farm.py`  
**Target Platform**: Local execution & GitHub Actions CI test runner  
**Project Type**: Python Web Service (Test Suite Expansion)  
**Performance Goals**: Full test execution under 3 seconds total; individual test modules < 1 second  
**Constraints**: Zero production code changes (FR-008); zero live network calls or real Meta credentials (FR-009)  
**Scale/Scope**: 2 new test modules (`tests/unit/test_whatsapp.py`, `tests/integration/test_daily_batch_multi_farm.py`), covering 8+ acceptance scenarios across unit and integration levels  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked post-Phase 1 design.*

- [x] **Principle I: Human-in-the-Loop Only**: Satisfied. Tests assert output formatting and message content; no automated hardware control logic exists or is tested.
- [x] **Principle IV: WhatsApp Cloud API Sandbox Tier Only**: Satisfied. Mock tokens and offline HTTP mocks are used; zero paid messaging or production Meta tokens used.
- [x] **Principle V: Scope Boundary & Cut List Enforcement**: Satisfied. Test-only scope; no cut-list capabilities introduced.
- [x] **Principle VI: End-to-End Demoability**: Satisfied. End-to-end webhook and daily recommendation dispatch flows validated via test client assertions.
- [x] **Principle VIII: Zero-Broken-Tests Policy**: Satisfied. New tests must achieve 100% pass rate without breaking existing test suite.
- [x] **Principle VIII: Zero Secrets in Code**: Satisfied. Mock secret strings (`mock_token`, `test_job_token`) used exclusively.
- [x] **Principle VIII: No-Facade Rule for External Integrations**: Satisfied. Tests temporarily set `WHATSAPP_TOKEN` to a non-placeholder value in fixtures to directly verify `httpx.AsyncClient` URL assembly, headers (`Authorization: Bearer`), JSON payload schemas, multipart files, and HTTP status error responses (`raise_for_status()`) rather than bypassing through `_is_mock_token`.

## Project Structure

### Documentation (this feature)

```text
specs/013-mvp-polish-whatsapp-batch-tests/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── test-suite-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
app/
├── whatsapp.py          # WhatsApp integration client (UNTOUCHED)
├── main.py              # FastAPI endpoints & daily batch job (UNTOUCHED)
└── decision.py          # Irrigation recommendation engine (UNTOUCHED)

tests/
├── unit/
│   ├── test_whatsapp.py # [NEW] Unit tests for send_text_message, upload_media, extract_incoming_message
│   ├── test_cropdoctor.py
│   └── test_weather.py
└── integration/
    ├── test_daily_batch_multi_farm.py # [NEW] Multi-farm daily batch job integration test
    └── test_webhook.py
```

**Structure Decision**: Single Python project structure with standard `app/` business logic and `tests/unit/` and `tests/integration/` pytest directories.

## Complexity Tracking

*No Constitution violations; zero complex architectural changes required.*
