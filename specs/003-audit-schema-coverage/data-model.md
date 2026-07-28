# Data Model & Schema Definitions: Audit Schema & Test Coverage Extension

**Feature Branch**: `003-audit-schema-coverage`
**Spec Link**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/003-audit-schema-coverage/spec.md)

## Pydantic v2 Models (`app/schemas.py`)

### 1. HealthCheckResponse

Represents system operational state returned by `GET /health`.

```python
class HealthCheckResponse(BaseModel):
    status: str
    app: str
    version: str
    voice_teaser_enabled: bool
```

- **Validation Rules**:
  - `status`: String (e.g., `"ok"`).
  - `app`: String (e.g., `"IrrigAgent AI"`).
  - `version`: SemVer string (e.g., `"1.0.0"`).
  - `voice_teaser_enabled`: Boolean flag indicating feature state.

---

### 2. FarmProfile

Represents farm configuration payload schema.

```python
class FarmProfile(BaseModel):
    phone: str
    region: str
    crop: str
    flow_rate_lph: float
    baseline_minutes: int
```

- **Validation Rules**:
  - `phone`: E.164 phone string (e.g., `"+212600000000"`).
  - `region`: Geographical region string.
  - `crop`: Crop type string.
  - `flow_rate_lph`: Non-negative float representing irrigation emitter rate in LPH.
  - `baseline_minutes`: Non-negative integer representing baseline daily irrigation run time.

---

### 3. DailyAdvisoryJobResponse

Represents execution results for batch daily advisory jobs.

```python
class DailyAdvisoryJobResponse(BaseModel):
    status: str
    processed_count: int
    skipped_count: int
```

- **Validation Rules**:
  - `status`: String (e.g., `"success"`).
  - `processed_count`: Non-negative integer count of processed farm profiles.
  - `skipped_count`: Non-negative integer count of skipped farm profiles.

---

### 4. WebhookVerification

Represents incoming Meta WhatsApp Cloud API webhook challenge parameters.

```python
class WebhookVerification(BaseModel):
    hub_mode: str
    hub_challenge: str
    hub_verify_token: str
```

- **Validation Rules**:
  - `hub_mode`: String (expected: `"subscribe"`).
  - `hub_challenge`: Echo challenge string returned on verification.
  - `hub_verify_token`: Shared secret string matched against system `VERIFY_TOKEN`.
