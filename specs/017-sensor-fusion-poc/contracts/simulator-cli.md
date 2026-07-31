# Contract: CLI Telemetry Simulator Utility

**Command**: `python scripts/simulate_sensor.py [OPTIONS]`

---

## Command Line Arguments

| Argument | Short | Type | Default | Description |
|---|---|---|---|---|
| `--farm` | `-f` | `str` | `"+212600000000"` | Farm recipient phone number ID |
| `--vwc` | `-v` | `float` | `16.5` | Volumetric Water Content percentage ($\text{VWC}\%$) |
| `--depth` | `-d` | `int` | `15` | Soil probe depth ($\text{cm}$) |
| `--battery` | `-b` | `int` | `95` | Battery level percentage ($\%$) |
| `--url` | `-u` | `str` | `"http://localhost:8000"` | Target IrrigAgent API base URL |

---

## Usage Examples

### 1. Simulate Dry Soil Depleted State (Triggers +15 min Irrigation Calibration)
```bash
python scripts/simulate_sensor.py --farm "+212600000000" --vwc 14.5
```

### 2. Simulate Saturated Soil State (Triggers Irrigation Reduction/Skip)
```bash
python scripts/simulate_sensor.py --farm "+212600000000" --vwc 30.0
```

### Expected Terminal Output
```text
📡 Transmitting soil moisture telemetry to http://localhost:8000/telemetry/sensor...
  • Farm ID : +212600000000
  • VWC %   : 14.5%
  • Depth   : 15 cm
✅ Telemetry successfully recorded! Response: {'status': 'success', 'fused_moisture_vwc': 14.5}
```
