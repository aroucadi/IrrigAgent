# Research & Design Decisions: Closed-Loop Sensor Fusion Telemetry & Decision Calibration

**Feature Branch**: `017-sensor-fusion-poc`  
**Created**: 2026-07-31  
**Spec Reference**: [spec.md](file:///d:/rouca/DVM\workPlace\IrrigAgent\specs\017-sensor-fusion-poc\spec.md)

---

## Technical Context & Decisions

### 1. Telemetry Ingestion API & Schema Validation

- **Decision**: Implement `POST /telemetry/sensor` in `app/main.py` backed by a strict Pydantic v2 model `SensorTelemetryPayload` in `app/schemas.py`.
- **Rationale**: Reuses existing FastAPI backend architecture (`fastapi==0.115.0`) and Pydantic v2 validation (`pydantic==2.9.2`). Enforces physical constraints ($\text{VWC} \in [0.0, 100.0]\%$, $\text{battery} \in [0, 100]\%$) automatically with HTTP 422 error responses on invalid data.
- **Alternatives Evaluated**:
  - *Raw JSON dictionary parsing*: Rejected because untyped parsing bypasses validation and risks silent state corruption.
  - *MQTT Broker*: Rejected to avoid adding external broker infrastructure to v1 per Constitution Principle V.

---

### 2. State Storage & Persistence Pattern

- **Decision**: Extend `app/firestore_client.py` with `update_farm_sensor_state()` to store the latest sensor reading under the farm profile document in Firestore (and mock memory client for tests).
- **Rationale**: Maintains single-source-of-truth persistence without requiring new database connections or new tables.
- **Alternatives Evaluated**:
  - *Separate Sensor Collection*: Rejected to keep queries fast and single-read for daily advisory processing.

---

### 3. Closed-Loop Sensor Fusion Decision Engine

- **Decision**: Extend `recommend_irrigation()` in `app/decision.py` to evaluate sensor telemetry freshness ($< 24\text{ hours}$) alongside FAO-56 $ET_c = ET_0 \times K_c$ calculations.
- **Rules**:
  - **Soil Depletion ($\text{VWC} < 18.0\%$):** Add $+10 \text{ to } +15\text{ min}$ irrigation to baseline $ET_c$.
  - **Near Field Capacity ($\text{VWC} > 28.0\%$):** Reduce irrigation duration by $50\%$ to $100\%$ (skip).
  - **Stale or Absent Telemetry ($> 24\text{ hours}$ or `None`):** Fall back to pure $ET_c$ weather math with zero error.
  - **WhatsApp Message Badge:** Include localized text `"📡 Données Capteur Sol (15cm): Humidité mesurée à X.X%."`.
- **Rationale**: Deterministic, rule-based math meeting Constitution Principle II (Rule-Based First Logic) and Principle I (Human-in-the-Loop Only).

---

### 4. Demo Simulation Utility

- **Decision**: Provide `scripts/simulate_sensor.py` using standard Python `httpx` and `argparse`.
- **Rationale**: Allows developers and pitch presenters to fire simulated telemetry to local Uvicorn or live GCP Cloud Run instances in under 5 seconds.
