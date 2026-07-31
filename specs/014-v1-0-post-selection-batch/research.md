# Phase 0 Research: v1.0 — ONSSA Live Registry Activation, Frost Alerts, Parcel UX Hardening, and Post-Selection IaC (gated)

**Feature Branch**: `014-v1-0-post-selection-batch`
**Date**: 2026-07-31

## Research & Design Decisions

### 1. ONSSA Registry Data Sync & Primary Lookup Integration

- **Decision**: Execute `scripts/sync_onssa_registry.py --commit` to produce `data/onssa_registry.json`. Modify `app/cropdoctor.py::lookup_onssa_product()` to load and query `data/onssa_registry.json` using normalized keys (`crop_type.strip().lower()`, `pathogen.strip().lower()`), falling back to `ONSSA_STATIC_CATALOG`, and returning `None` if missing from both.
- **Rationale**:
  - The script `scripts/sync_onssa_registry.py` already supports robots.txt compliance, rate-limiting, error logging, and atomic file commits to `data/onssa_registry.json`.
  - Wrapping dataset loading in a try/except block ensures zero runtime crashes if the file is absent or malformed during edge-case startup scenarios.
  - Normalizing keys via `.strip().lower()` guarantees robust string matching regardless of slight typography differences between ONSSA scraped strings and incoming vision/text triage labels.
- **Alternatives Considered**:
  - *Direct live web scraping during CropDoctor triage*: Rejected to prevent latency spikes, network failures, and violation of the sub-second triage SLA.
  - *Database ingestion (Firestore)*: Rejected per Constitution Section VII (keep Firestore schema minimal/flat for user states; file-based JSON caching is faster and zero-cost).

### 2. Extreme Weather Threshold Alert Pipeline

- **Decision**: Define default constants `HEAT_WARNING_TEMP_C = 40.0` and `FROST_WARNING_TEMP_C = 2.0` in `app/config.py` (overrideable via environment variables). In `app/decision.py`, compare forecast `temperature_2m_max` and `temperature_2m_min` against these thresholds. Append a localized warning block to the advisory text.
- **Rationale**:
  - Leverages existing daily Open-Meteo daily forecast payload (`temperature_2m_max` and `temperature_2m_min` are already fetched by `app/weather.py`).
  - Appending advisory text directly to the daily message requires zero additional scheduled jobs or messaging API quota overhead.
  - Interactive reply processing (1=Approve, 2=Modify, 3=Skip) remains completely unaffected because message parser matches option digits regardless of body text length.
- **Alternatives Considered**:
  - *Separate standalone WhatsApp warning message*: Rejected to avoid extra WhatsApp Cloud API messages and potential message re-ordering over carrier networks.
  - *New scheduled Cron job for weather alerts*: Rejected per User Story 2 requirement to reuse the existing daily batch pipeline.

### 3. Hardened Parcel Boundary Pin Validation & Reset Flow

- **Decision**: Enhance `app/parcel_validation.py` with explicit checks for pin counts (< 3), pairwise geodesic distance checks (< 5 meters), and polygon self-intersection (using Shapely `is_simple` or line crossing checks). Update `app/main.py` boundary state machine to handle validation failures and respond to command list (`"restart boundary"`, `"restart"`, `"recommencer"`, `"réinitialiser"`, `"بداية جديدة"`).
- **Rationale**:
  - Checking pairwise geodesic distance using Haversine or Vincenty formula accurately identifies duplicate pins dropped by farmers within ~5m.
  - Detecting non-simple polygons prevents corrupted field area calculations and broken spatial queries downstream.
  - Adding multi-lingual restart commands provides a self-service recovery path for farmers without requiring admin intervention.
- **Alternatives Considered**:
  - *Silent auto-fixing of self-intersecting polygons*: Rejected because altering farmer boundary points without confirmation creates false field geometry.
  - *Strict single command string (`restart boundary` only)*: Rejected during clarification session in favor of multi-language options for Moroccan farmers.

### 4. Post-Selection Infrastructure as Code (Gated)

- **Decision**: Keep User Story 4 strictly gated. Mark all tasks associated with V1-004 as blocked/deferred in `tasks.md`. Generate zero IaC code artifacts in this feature branch.
- **Rationale**:
  - Mandated by Constitution Section VII and explicit User Story 4 hard gate condition.
  - Prevents premature scope drift while maintaining a clean backlog placeholder for post-selection deployment scaling.
- **Alternatives Considered**:
  - *Writing draft Terraform files*: Explicitly forbidden by Constitution Section VII and prompt instructions until StartGate confirmation.
