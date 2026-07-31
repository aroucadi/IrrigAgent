# Data Model: v1.0 — ONSSA Live Registry Activation, Frost Alerts, Parcel UX Hardening, and Post-Selection IaC (gated)

**Feature Branch**: `014-v1-0-post-selection-batch`
**Date**: 2026-07-31

## Key Entities & Data Schemas

### 1. ONSSA Registry Data Structures (`data/onssa_registry.json`)

#### ONSSARegistryDataset (File Root)
- `metadata` (object):
  - `last_synced` (string, ISO-8601 timestamp): Timestamp of the last sync run.
  - `total_records` (integer): Total number of authorized products parsed.
  - `parse_failures` (integer): Count of records skipped due to parsing issues.
- `catalog` (dictionary):
  - Key: Normalized pathogen string (`pathogen.strip().lower()`).
  - Value: Dictionary of crop entries keyed by normalized crop name (`crop_type.strip().lower()`), containing array of `ONSSARegistryEntry`.

#### ONSSARegistryEntry
- `trade_name` (string): Commercial product name authorized by ONSSA (e.g. `"Score 250 EC"`).
- `active_ingredient` (string): Chemical active substance (e.g. `"Difenoconazole"`).
- `authorization_number` (string): Official ONSSA AP/MA approval number.
- `formulation` (string, optional): Physical formulation type (e.g. `"EC"`, `"WP"`).
- `company` (string, optional): Registrar/distributor company name.

---

### 2. Extreme Weather Threshold Config & Advisory Warnings (`app/config.py`, `app/decision.py`)

#### WeatherThresholdConfig
- `heat_warning_temp_c` (float, default `40.0`): Maximum temperature threshold triggering heatwave alerts.
- `frost_warning_temp_c` (float, default `2.0`): Minimum temperature threshold triggering frost alerts.

#### WeatherWarningPayload
- `warning_type` (enum: `"HEAT"`, `"FROST"`, `"NONE"`): Type of extreme weather risk detected.
- `temperature_c` (float): Extreme temperature value from forecast.
- `suggested_action` (string): Localized protective advice text based on language (`"fr"`, `"ar"`, `"en"`).

---

### 3. Parcel Boundary Validation & Buffer (`app/parcel_validation.py`)

#### ParcelBoundaryBuffer (Session / State)
- `phone_number` (string): Farmer WhatsApp identifier.
- `pins` (list of lat/lon tuples `[(lat, lon), ...]`): Collected boundary GPS pins.
- `state` (enum: `"COLLECTING"`, `"VALID"`, `"INVALID"`): Current collection state.

#### ParcelValidationError (Enum & Result)
- `error_code` (enum):
  - `INSUFFICIENT_PINS`: Fewer than 3 boundary pins provided.
  - `PIN_TOO_CLOSE`: Two or more pins are under 5 meters apart.
  - `SELF_INTERSECTING`: Polygon perimeter boundary lines cross over each other.
- `guidance_message` (string): Localized actionable text explaining how the farmer should fix the issue.
