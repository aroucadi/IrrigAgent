# Implementation Plan: Audit Schema & Test Coverage Extension

**Branch**: `003-audit-schema-coverage` | **Date**: 2026-07-28 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/003-audit-schema-coverage/spec.md)

**Input**: Feature specification from `specs/003-audit-schema-coverage/spec.md`

## Summary

Extend application architecture and test coverage to address Audit Report recommendations by implementing Pydantic v2 data schemas in `app/schemas.py`, refactoring API endpoints in `app/main.py` to enforce strict request/response validation, and adding explicit test cases `test_health_endpoint()` and `test_daily_advisory_alias_endpoint()` in `tests/integration/test_webhook.py` to guarantee 100% test pass rate and coverage.

## Technical Context

**Language/Version**: Python 3.11+ (running 3.13.9)
**Primary Dependencies**: FastAPI, Pydantic v2, httpx
**Storage**: Firestore (mocked/in-memory client for tests)
**Testing**: pytest, pytest-asyncio, httpx AsyncClient
**Target Platform**: GCP Cloud Run
**Project Type**: Web application / API service
**Performance Goals**: Sub-second HTTP endpoint execution (<100ms)
**Constraints**: Constitution Principle VIII compliance (Zero-broken-tests policy, strict schema enforcement, 100% test pass rate)
**Scale/Scope**: 4 Pydantic v2 models, 2 new integration test cases, 2 refactored endpoint return annotations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Zero-Broken-Tests Policy**: PASS (All 32 existing tests pass, new tests will run with 100% pass rate).
- **Deterministic Math & Parsing Coverage**: PASS (Existing tests cover ET₀ calculation and regex parsing).
- **Zero Secrets in Code**: PASS (No API keys or secret tokens committed).
- **Mandatory Pre-Commit Gate Enforcement**: PASS (Local commits run automated formatting and fast tests).
- **Automated Verification Standard**: PASS (Explicit `pytest` test cases verify endpoints deterministically).

## Project Structure

### Documentation (this feature)

```text
specs/003-audit-schema-coverage/
├── plan.md              # Implementation Plan
├── research.md          # Technical decisions and rationale
├── data-model.md        # Pydantic v2 model definitions
├── quickstart.md        # Validation commands and expected outcomes
├── contracts/           # OpenAPI / JSON Schema definitions
│   ├── health.json
│   └── jobs.json
└── tasks.md             # Implementation tasks (/speckit-tasks command)
```

### Source Code (repository root)

```text
app/
├── main.py              # Refactored Fast API routes with response_model annotations
├── schemas.py           # [NEW] Strict Pydantic v2 BaseModel schemas
├── config.py
├── cropdoctor.py
├── decision.py
├── firestore_client.py
├── regex_parser.py
├── tts_voice.py
├── weather.py
└── whatsapp.py

tests/
└── integration/
    └── test_webhook.py  # [MODIFY] Added test_health_endpoint and test_daily_advisory_alias_endpoint
```

**Structure Decision**: Single Python project structure adhering to FastAPI best practices with a dedicated `app/schemas.py` module for Pydantic models.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations detected. Implementation follows clean, minimal FastAPI architecture.*
