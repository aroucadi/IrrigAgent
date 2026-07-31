# Feature Specification: Closed-Loop Sensor Fusion Telemetry & Decision Calibration

**Feature Branch**: `017-sensor-fusion-poc`

**Created**: 2026-07-31

**Status**: Implemented

**Input**: User description: "Closed-loop sensor fusion PoC ingesting mock soil moisture telemetry (Volumetric Water Content VWC %) via REST API endpoint, calibrating FAO-56 ETc weather math with ground-truth moisture readings, and generating hardware-ready WhatsApp irrigation advisories with 100% human-in-the-loop approval and CLI demo simulation script."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Simulated Soil Sensor Telemetry Ingestion API (Priority: P1)

As a farm manager or agricultural cooperative operator with soil moisture probes, I want the system to ingest live Volumetric Water Content ($\text{VWC}\%$) telemetry via a REST API endpoint, so that ground-truth soil moisture measurements are recorded and associated with my farm profile.

**Why this priority**: Core prerequisite for sensor fusion. Providing a clean HTTP API endpoint allows both real IoT gateways and mock simulation scripts to feed ground-truth telemetry into the platform.

**Independent Test**: Can be independently tested by sending JSON telemetry payloads to `POST /telemetry/sensor` and verifying payload validation, state persistence, and HTTP 200/422 response handling without requiring active weather or WhatsApp services.

**Acceptance Scenarios**:

1. **Given** a valid JSON telemetry payload containing `farm_id`, `timestamp`, `soil_moisture_vwc`, `depth_cm`, and `battery_level`, **When** `POST /telemetry/sensor` is invoked, **Then** the system validates the payload schema, updates the farm profile's latest sensor reading state, and returns HTTP 200 with confirmation.
2. **Given** an invalid sensor telemetry payload (such as negative moisture $\text{VWC} < 0\%$ or out-of-range value $> 100\%$), **When** `POST /telemetry/sensor` is invoked, **Then** the system rejects the request with HTTP 422 Unprocessable Entity and logs a validation warning without corrupting existing farm state.

---

### User Story 2 - Closed-Loop Sensor Fusion Irrigation Recommendation Calibration (Priority: P1)

As Hassan the farmer, I want my daily WhatsApp irrigation advisory to combine Open-Meteo weather math ($ET_c$) with my latest ground-truth soil moisture readings, so that daily water recommendations automatically adjust for measured soil depletion or saturation.

**Why this priority**: Hero capability of closed-loop sensor fusion. Demonstrates enterprise-grade intelligence by fusing weather forecast math with live ground-truth telemetry while adhering strictly to Constitution Principle I (Human-in-the-Loop).

**Independent Test**: Can be independently tested by seeding a farm profile with recent sensor telemetry ($\text{VWC} = 16.5\%$), running the daily decision calculation, and asserting that the output advisory incorporates sensor depletion adjustments and includes the "📡 Données Capteur Sol" badge.

**Acceptance Scenarios**:

1. **Given** a farm profile with a recent ($< 24\text{ hours}$) soil moisture reading below optimal threshold (e.g. $\text{VWC} < 18\%$), **When** daily recommendation processing executes, **Then** the decision engine appends calibrated irrigation minutes ($+10 \text{ to } +15\text{ min}$) to compensate for depletion and highlights the sensor reading in the advisory text.
2. **Given** a farm profile with a recent soil moisture reading near or above field capacity (e.g. $\text{VWC} > 28\%$), **When** daily recommendation processing executes, **Then** the decision engine reduces or skips recommended irrigation duration to prevent overwatering.
3. **Given** a farm profile with no sensor telemetry or stale telemetry ($> 24\text{ hours}$ old), **When** daily recommendation processing executes, **Then** the decision engine falls back seamlessly to standard FAO-56 weather math ($ET_c = ET_0 \times K_c$) without error or missing advisory dispatch.
4. **Given** a sensor-calibrated irrigation recommendation delivered to Hassan over WhatsApp, **When** Hassan responds with standard reply options (`1` Approve, `2` Skip, `3` Modify), **Then** interactive reply handling executes identically to standard weather advisories with zero direct hardware actuation.

---

### User Story 3 - CLI Telemetry Simulator Utility for Live Demos (Priority: P2)

As a demonstrator or developer, I want a lightweight command-line script (`scripts/simulate_sensor.py`) to simulate capacitive soil probe readings for target test farms, so that closed-loop sensor fusion flows can be demonstrated live in under 15 seconds.

**Why this priority**: Provides a zero-dependency demo mechanism for pitches and investor presentations without relying on physical microcontroller hardware.

**Independent Test**: Can be independently tested by running `python scripts/simulate_sensor.py --farm "+212600000000" --vwc 16.5` against a local or deployed service instance and verifying telemetry ingestion confirmation.

**Acceptance Scenarios**:

1. **Given** a target farm phone number and desired moisture percentage parameter, **When** `scripts/simulate_sensor.py` is executed, **Then** it constructs a valid telemetry payload, posts it to `/telemetry/sensor`, and prints the response status and fused moisture readings to the terminal.

---

### Edge Cases

- What happens if sensor telemetry reports extremely low battery level ($< 10\%$)? The system accepts the moisture reading but appends a low-battery alert flag to internal logs and optional telemetry summary.
- What happens if multiple sensor readings arrive within a short time window? The system updates farm state with the latest timestamped reading, maintaining an idempotent state buffer.
- What happens if the weather API fails while sensor telemetry is available? The system uses the ground-truth moisture reading to generate a conservative fallback recommendation, preserving system availability.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose a REST API endpoint `POST /telemetry/sensor` accepting JSON telemetry payloads containing `farm_id` (WhatsApp phone number string), `timestamp` (ISO datetime string), `soil_moisture_vwc` (float percentage), `depth_cm` (integer depth), and `battery_level` (integer percentage).
- **FR-002**: System MUST enforce strict Pydantic v2 validation on incoming sensor telemetry, validating that `soil_moisture_vwc` is within $[0.0, 100.0]\%$ and `battery_level` is within $[0, 100]\%$.
- **FR-003**: System MUST persist the latest valid sensor reading per farm profile in state with timestamp tracking.
- **FR-004**: The decision engine MUST evaluate whether a farm profile has fresh sensor telemetry ($< 24\text{ hours}$ old) during daily advisory calculation.
- **FR-005**: When fresh sensor telemetry indicates depleted soil ($\text{VWC} < 18.0\%$), the decision engine MUST add calibrated irrigation duration ($+10 \text{ to } +15\text{ min}$) to the baseline FAO-56 $ET_c$ recommendation.
- **FR-006**: When fresh sensor telemetry indicates near-saturated soil ($\text{VWC} > 28.0\%$), the decision engine MUST reduce or skip recommended irrigation duration.
- **FR-007**: WhatsApp advisory messages generated for sensor-calibrated farms MUST include a localized sensor telemetry section (e.g., `"📡 Données Capteur Sol (15cm): Humidité mesurée à 16.5%."`) explaining the ground-truth adjustment.
- **FR-008**: System MUST maintain 100% compliance with Constitution Principle I (Human-in-the-Loop Only) — sensor telemetry MUST strictly inform recommendation text and interactive options (`1`/`2`/`3`), with ZERO automated hardware or solenoid valve control.
- **FR-009**: When a farm profile has no sensor telemetry or telemetry older than 24 hours, the decision engine MUST fall back to pure FAO-56 weather math ($ET_c = ET_0 \times K_c$) without error or missing message delivery.
- **FR-010**: System MUST include a CLI simulation utility `scripts/simulate_sensor.py` capable of posting configurable mock telemetry payloads to local or deployed application endpoints.

### Key Entities

- **SensorTelemetryReading**: Data entity representing an ingested soil probe measurement with attributes `farm_id`, `timestamp`, `soil_moisture_vwc`, `depth_cm`, and `battery_level`.
- **FusedIrrigationDecision**: Decision output entity combining baseline $ET_c$ water deficit, sensor calibration delta ($\Delta \text{minutes}$), telemetry timestamp, sensor badge text, and interactive WhatsApp reply parameters.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Telemetry ingestion endpoint `POST /telemetry/sensor` processes and validates payloads in under 200ms with 100% schema enforcement.
- **SC-002**: 100% of daily advisories generated for farms with fresh depleted moisture telemetry ($\text{VWC} < 18\%$) incorporate calibrated duration adjustments and explicit sensor telemetry indicators.
- **SC-003**: Telemetry older than 24 hours is automatically ignored by the decision engine with 100% graceful fallback to pure FAO-56 weather math.
- **SC-004**: 100% of sensor-calibrated recommendations require human approval via WhatsApp reply loop, maintaining zero automated hardware control.
- **SC-005**: Automated test suite (`pytest tests/`) achieves 100% pass rate covering telemetry endpoint validation, sensor fusion calculation logic, and advisory text formatting.

## Assumptions

- Target farm profiles are identified by their primary WhatsApp phone number string (`farm_id`).
- Volumetric Water Content ($\text{VWC}\%$) is reported as a float percentage (e.g. `18.2` for $18.2\%$).
- Telemetry is transmitted via standard HTTPS/HTTP REST POST requests.
- Hardware probe calibration, wireless SIM connectivity, and physical installation are managed by third-party sensor vendors or simulated via CLI script.
