# Contract: Sensor Telemetry Ingestion REST API

**Endpoint**: `POST /telemetry/sensor`  
**Content-Type**: `application/json`

---

## Request Payload

```json
{
  "farm_id": "+212600000000",
  "timestamp": "2026-07-31T14:00:00Z",
  "soil_moisture_vwc": 16.5,
  "depth_cm": 15,
  "battery_level": 94
}
```

### Request Headers
- `Content-Type: application/json`
- `X-Sensor-Secret` *(Optional / Future API Key)*

---

## Response Contracts

### 1. HTTP 200 OK — Telemetry Ingested Successfully

```json
{
  "status": "success",
  "farm_id": "+212600000000",
  "soil_moisture_vwc": 16.5,
  "timestamp": "2026-07-31T14:00:00Z",
  "message": "Telemetry recorded. Sensor state active."
}
```

### 2. HTTP 422 Unprocessable Entity — Validation Failure

```json
{
  "detail": [
    {
      "loc": ["body", "soil_moisture_vwc"],
      "msg": "Input should be less than or equal to 100",
      "type": "less_than_equal"
    }
  ]
}
```
