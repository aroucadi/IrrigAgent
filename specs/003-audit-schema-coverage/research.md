# Research & Technical Decisions: Audit Schema & Test Coverage Extension

**Feature Branch**: `003-audit-schema-coverage`
**Spec Link**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/003-audit-schema-coverage/spec.md)

## Decisions & Rationale

### 1. Pydantic v2 Schema Architecture (`app/schemas.py`)

- **Decision**: Implement strict Pydantic v2 `BaseModel` schemas in a new standalone module `app/schemas.py`.
- **Schemas**:
  1. `HealthCheckResponse`:
     - `status: str`
     - `app: str`
     - `version: str`
     - `voice_teaser_enabled: bool`
  2. `FarmProfile`:
     - `phone: str`
     - `region: str`
     - `crop: str`
     - `flow_rate_lph: float`
     - `baseline_minutes: int`
  3. `DailyAdvisoryJobResponse`:
     - `status: str`
     - `processed_count: int`
     - `skipped_count: int`
  4. `WebhookVerification`:
     - `hub_mode: str`
     - `hub_challenge: str`
     - `hub_verify_token: str`
- **Rationale**: Keeps model definitions decoupled from routing logic in `app/main.py`. Provides strict type validation and automatic OpenAPI schema documentation.

### 2. Integration Test Matrix Additions (`tests/integration/test_webhook.py`)

- **Decision**: Add two explicit `pytest` test cases to `tests/integration/test_webhook.py`:
  1. `test_health_endpoint()`:
     - Issues `GET /health`.
     - Asserts HTTP 200.
     - Validates returned JSON against `HealthCheckResponse` model attributes (`status`, `app`, `version`, `voice_teaser_enabled`).
  2. `test_daily_advisory_alias_endpoint()`:
     - Issues `POST /api/v1/jobs/daily-advisory` with valid authorization token (`Bearer {JOB_SECRET_TOKEN}`).
     - Asserts HTTP 200.
     - Verifies unauthorized requests without valid token return HTTP 401.
     - Asserts output payload attributes match `/jobs/daily-recommendations`.
- **Rationale**: Fulfills explicit requirements from the Audit Report and satisfies Constitution Principle VIII (Zero-Broken-Tests Policy & Automated Verification Gates).

### 3. Alternatives Considered

- **Inline Pydantic models in `app/main.py`**: Rejected to maintain clean separation of concerns and reusability across services.
- **Pydantic v1 Dataclasses**: Rejected because the project standard requires Pydantic v2 `BaseModel`.
