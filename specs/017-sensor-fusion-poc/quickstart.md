# Quickstart Validation Guide: Closed-Loop Sensor Fusion Telemetry

**Feature Branch**: `017-sensor-fusion-poc`  
**Created**: 2026-07-31  
**Spec Reference**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/017-sensor-fusion-poc/spec.md)

---

## Runnable Validation Scenarios

### Scenario 1: Telemetry Ingestion API & Schema Bounds Check

Verify that `POST /telemetry/sensor` validates payloads, accepts valid VWC % data, and rejects out-of-range values.

```bash
# 1. Execute unit test covering schema validation
pytest tests/unit/test_schemas.py -k "test_sensor_telemetry"

# 2. Run local API server
uvicorn app.main:app --port 8000 &

# 3. Post valid telemetry payload
curl -X POST "http://localhost:8000/telemetry/sensor" \
  -H "Content-Type: application/json" \
  -d '{"farm_id": "+212600000000", "soil_moisture_vwc": 16.5, "depth_cm": 15}'
```

**Expected Outcome**: API returns `HTTP 200 OK` with `{"status": "success", "fused_moisture_vwc": 16.5}`.

---

### Scenario 2: Fused Sensor + Weather Math Decision Calibration

Verify that depleted soil ($\text{VWC} < 18\%$) appends calibrated duration minutes ($+10 \text{ to } +15\text{ min}$) and includes the sensor badge in the advisory string.

```bash
# Execute decision fusion unit tests
pytest tests/unit/test_decision.py -k "test_sensor_fusion"
```

**Expected Outcome**: Unit tests confirm:
1. Depleted soil ($\text{VWC} = 16.5\%$) adds $+10 \text{ to } +15\text{ min}$ over weather-only baseline.
2. Advisory text includes `"📡 Données Capteur Sol (15cm): Humidité mesurée à 16.5%."`.
3. Stale telemetry ($> 24\text{ hours}$ old) gracefully falls back to pure weather math.

---

### Scenario 3: Live CLI Telemetry Simulation

Demonstrate a 15-second closed-loop sensor telemetry update for live pitch presentations.

```bash
# Run simulator CLI script
python scripts/simulate_sensor.py --farm "+212600000000" --vwc 14.5
```

**Expected Outcome**: Script outputs success response, and triggering `POST /jobs/daily-recommendations` dispatches a sensor-calibrated WhatsApp advisory.
